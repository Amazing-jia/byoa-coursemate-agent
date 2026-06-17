import json
import os
import re
import sys
import urllib.error
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

VENDOR_DIR = Path(__file__).resolve().parent / ".vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from tools import read_local_file, summarize_text


BASE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT_PATH = BASE_DIR / "prompts" / "system_prompt.txt"

QUERY_ALIASES = {
    "实验": ["experiment", "assignment", "lab"],
    "实验二": ["experiment 2", "assignment 2", "build your own agent", "byoa"],
    "要求": ["requirement", "requirements", "criteria", "deliverable"],
    "作业": ["assignment", "homework", "deliverable"],
    "代理": ["agent"],
    "智能体": ["agent"],
    "工具": ["tool", "tools", "function"],
    "技能": ["skill", "skills"],
    "上下文": ["context", "external context"],
    "函数调用": ["function calling", "function-based", "orchestration"],
    "提示": ["prompt", "prompting"],
    "提示词": ["prompt", "prompting"],
    "零样本": ["zero-shot"],
    "少样本": ["k-shot", "few-shot"],
    "链式思维": ["chain-of-thought", "cot"],
    "反思": ["reflection", "reflexion"],
    "总结": ["summary", "summarize"],
    "课程": ["course", "lecture", "slide"],
    "课件": ["slide", "slides", "ppt", "course material"],
}


def load_env_file(path):
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file(BASE_DIR / ".env")


def load_system_prompt():
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def infer_keyword(question):
    cleaned = question.strip()
    lowered = cleaned.lower()
    removable_phrases = [
        "what is",
        "what are",
        "tell me about",
        "summarize",
        "summary",
        "please explain",
        "explain",
        "describe",
        "总结",
        "请总结",
        "介绍",
        "说明",
        "解释",
        "什么是",
        "有哪些",
        "是什么",
        "区别",
    ]

    for phrase in removable_phrases:
        lowered = lowered.replace(phrase, " ")

    keyword = " ".join(lowered.split())
    return keyword or cleaned


def question_tokens(question):
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]+|[\u4e00-\u9fff]{2,}", question)
    stop_words = {
        "什么",
        "哪些",
        "这个",
        "这些",
        "资料",
        "课件",
        "文件",
        "内容",
        "主要",
        "区别",
        "总结",
        "请总结",
    }
    return [token.lower() for token in tokens if token not in stop_words]


def expanded_query_terms(question):
    lowered = question.lower()
    terms = set(question_tokens(question))
    keyword = infer_keyword(question).lower()
    if keyword:
        terms.add(keyword)

    for cn_term, aliases in QUERY_ALIASES.items():
        if cn_term in question:
            terms.update(alias.lower() for alias in aliases)

    if "zero" in lowered and "shot" in lowered:
        terms.add("zero-shot")
    if "k" in lowered and "shot" in lowered:
        terms.add("k-shot")
    if "chain" in lowered and "thought" in lowered:
        terms.add("chain-of-thought")

    return [term for term in terms if term]


def normalize_file_paths(file_paths):
    if not file_paths:
        return []
    if isinstance(file_paths, (str, Path)):
        return [Path(file_paths)]
    return [Path(path) for path in file_paths if path]


def read_materials(file_paths):
    sources = []
    errors = []

    for path in normalize_file_paths(file_paths):
        text = read_local_file(path)
        if text.startswith("File not found") or text.startswith("Unsupported"):
            errors.append(text)
            continue

        sources.append(
            {
                "file_name": path.name,
                "path": str(path),
                "text": text,
            }
        )

    return sources, errors


def format_sources_full_text(sources):
    return "\n\n".join(
        f"===== {source['file_name']} =====\n{source['text']}" for source in sources
    )


def split_source_blocks(source):
    raw_blocks = [block.strip() for block in source["text"].split("\n\n") if block.strip()]
    if not raw_blocks:
        raw_blocks = [line.strip() for line in source["text"].splitlines() if line.strip()]

    blocks = []
    for index, block in enumerate(raw_blocks, start=1):
        label = f"{source['file_name']} / 片段 {index}"
        first_line = block.splitlines()[0] if block.splitlines() else ""
        if first_line.startswith("[Slide ") or first_line.startswith("[Page "):
            label = f"{source['file_name']} / {first_line.strip('[]')}"

        blocks.append(
            {
                "file_name": source["file_name"],
                "index": index,
                "label": label,
                "text": block,
            }
        )

    return blocks


def trim_around_match(text, terms, max_chars):
    if len(text) <= max_chars:
        return text

    lowered = text.lower()
    positions = [lowered.find(term) for term in terms if term and lowered.find(term) >= 0]
    center = min(positions) if positions else 0
    half = max_chars // 2
    start = max(0, center - half)
    end = min(len(text), start + max_chars)

    if start > 0:
        line_start = text.find("\n", start)
        if line_start != -1 and line_start < center:
            start = line_start + 1
    if end < len(text):
        line_end = text.rfind("\n", start, end)
        if line_end > start:
            end = line_end

    prefix = "...\n" if start > 0 else ""
    suffix = "\n..." if end < len(text) else ""
    return prefix + text[start:end].strip() + suffix


def rank_passages(question, sources):
    terms = expanded_query_terms(question)
    keyword = infer_keyword(question).lower()
    candidates = []

    for source in sources:
        candidates.extend(split_source_blocks(source))

    if not candidates:
        return []

    def score(candidate):
        text = candidate["text"]
        lowered = text.lower()
        token_hits = sum(lowered.count(term) for term in terms if term)
        unique_hits = sum(1 for term in terms if term and term in lowered)
        keyword_hit = 5 if keyword and keyword in lowered else 0
        title_hit = 4 if any(term in candidate["label"].lower() for term in terms) else 0
        fuzzy = max(
            (SequenceMatcher(None, term, lowered[:1200]).ratio() for term in terms if len(term) >= 4),
            default=0,
        )
        density = token_hits / max(len(text), 1)
        final_score = (unique_hits * 12) + token_hits + keyword_hit + title_hit + (fuzzy * 2) + density
        return final_score, token_hits, unique_hits

    scored = []
    for candidate in candidates:
        final_score, token_hits, unique_hits = score(candidate)
        candidate = dict(candidate)
        candidate["_score"] = final_score
        candidate["_token_hits"] = token_hits
        candidate["_unique_hits"] = unique_hits
        scored.append(candidate)

    ranked = sorted(scored, key=lambda item: item["_score"], reverse=True)
    positive = [candidate for candidate in ranked if candidate["_score"] > 0]
    return positive or ranked[:1]


def normalize_base_url(base_url):
    url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").strip()
    return url.rstrip("/")


def extract_chat_completion_text(data):
    choices = data.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("text"):
                    parts.append(item["text"])
            if parts:
                return "\n".join(parts).strip()

    if "output_text" in data:
        return str(data["output_text"]).strip()

    return "API 返回了结果，但没有找到可显示的文本内容。"


def rerank_with_external_api(question, candidates, api_config=None):
    api_config = api_config or {}
    api_key = (api_config.get("api_key") or os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key or not candidates:
        return candidates

    model = (api_config.get("model") or os.getenv("OPENAI_MODEL") or "gpt-4.1-mini").strip()
    endpoint = f"{normalize_base_url(api_config.get('base_url'))}/chat/completions"
    compact_candidates = [
        {
            "index": index,
            "label": candidate["label"],
            "text": candidate["text"][:900],
        }
        for index, candidate in enumerate(candidates[:8])
    ]
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict passage reranker. Return only JSON. "
                    "Choose passages that best answer the user's question."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "candidates": compact_candidates,
                        "instruction": "Return JSON like {\"indices\":[0,2,1]} ordered from most relevant to least relevant.",
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": 0,
    }

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        content = extract_chat_completion_text(data)
        match = re.search(r"\{.*\}", content, flags=re.S)
        if not match:
            return candidates
        parsed = json.loads(match.group(0))
        indices = [index for index in parsed.get("indices", []) if isinstance(index, int)]
    except Exception:
        return candidates

    chosen = []
    seen = set()
    for index in indices:
        if 0 <= index < min(len(candidates), 8) and index not in seen:
            chosen.append(candidates[index])
            seen.add(index)

    for index, candidate in enumerate(candidates):
        if index not in seen:
            chosen.append(candidate)

    return chosen


def build_retrieved_context(question, sources, max_blocks=3, block_chars=900, api_config=None):
    ranked = rank_passages(question, sources)
    if not ranked:
        return "", []

    ranked = rerank_with_external_api(question, ranked, api_config=api_config)
    best_hits = ranked[0].get("_token_hits", 0)
    if best_hits > 1:
        min_hits = max(2, best_hits * 0.5)
        ranked = [item for item in ranked if item.get("_token_hits", 0) >= min_hits]

    selected = ranked[:max_blocks]
    terms = expanded_query_terms(question)

    parts = []
    for passage in selected:
        text = trim_around_match(passage["text"], terms, block_chars)
        parts.append(f"===== {passage['label']} =====\n{text}")

    return "\n\n---\n\n".join(parts), selected


def build_source_excerpt(question, selected_passages, max_chars=1600):
    if not selected_passages:
        return ""

    best = selected_passages[0]
    terms = expanded_query_terms(question)
    text = trim_around_match(best["text"], terms, max_chars)
    return f"===== {best['label']} =====\n{text}"


def retrieve_context(question, file_paths, api_config=None):
    sources, errors = read_materials(file_paths)

    if not sources:
        if errors:
            return "\n".join(errors), "error", [], ""
        return "请先上传至少一个 PPTX、PDF 或 TXT 课程资料文件。", "error", [], ""

    lowered = question.lower()
    if "summary" in lowered or "summarize" in lowered or "总结" in question:
        context, selected = build_retrieved_context(
            question,
            sources,
            max_blocks=5,
            block_chars=1100,
            api_config=api_config,
        )
        if not context:
            context = summarize_text(format_sources_full_text(sources), max_chars=3500)
        excerpt = build_source_excerpt(question, selected)
        return context, "hybrid-summary-context", sources, excerpt

    context, selected = build_retrieved_context(question, sources, api_config=api_config)
    excerpt = build_source_excerpt(question, selected)
    return context, "hybrid-passage-search", sources, excerpt


def answer_with_external_api(question, context, retrieval_mode, api_config=None):
    api_config = api_config or {}
    api_key = (api_config.get("api_key") or os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        return (
            "请先在页面右侧输入 API Key，或在项目 .env 文件中设置 OPENAI_API_KEY。\n\n"
            "本次已经完成了本地资料检索，但没有调用外部 API。"
        )

    model = (api_config.get("model") or os.getenv("OPENAI_MODEL") or "gpt-4.1-mini").strip()
    base_url = normalize_base_url(api_config.get("base_url"))
    endpoint = f"{base_url}/chat/completions"
    system_prompt = load_system_prompt()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"用户问题：\n{question}\n\n"
                    f"本地课程资料检索结果（{retrieval_mode}）：\n{context}\n\n"
                    "请基于检索到的课程资料回答。"
                    "如果资料不足以回答，请明确说明缺少哪些信息。"
                    "回答请使用中文，结构清晰，简洁准确。"
                ),
            },
        ],
        "temperature": 0.2,
    }

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        return f"外部 API 请求失败（HTTP {error.code}）：\n{detail}"
    except urllib.error.URLError as error:
        return f"外部 API 连接失败：{error.reason}"
    except TimeoutError:
        return "外部 API 请求超时，请检查网络、API 地址或模型名称。"

    return extract_chat_completion_text(data)


def answer_question(question, file_paths=None, use_api=True, api_config=None):
    context, retrieval_mode, sources, source_excerpt = retrieve_context(
        question,
        file_paths,
        api_config=api_config if use_api else None,
    )
    file_names = [source["file_name"] for source in sources]

    if retrieval_mode == "error":
        return {
            "answer": context,
            "context": "",
            "source_excerpt": "",
            "retrieval_mode": retrieval_mode,
            "used_api": False,
            "file_names": file_names,
            "file_name": "未上传文件",
        }

    if use_api:
        answer = answer_with_external_api(question, context, retrieval_mode, api_config)
        used_api = not answer.startswith("请先在页面右侧输入 API Key")
    else:
        answer = "已关闭外部 API 调用。以下是从上传资料中检索到的内容：\n\n" + context
        used_api = False

    return {
        "answer": answer,
        "context": context,
        "source_excerpt": source_excerpt,
        "retrieval_mode": retrieval_mode,
        "used_api": used_api,
        "file_names": file_names,
        "file_name": "、".join(file_names),
    }
