import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

VENDOR_DIR = Path(__file__).resolve().parent / ".vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from tools import read_local_file, search_in_text, summarize_text


BASE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT_PATH = BASE_DIR / "prompts" / "system_prompt.txt"


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
    ]

    for phrase in removable_phrases:
        lowered = lowered.replace(phrase, " ")

    keyword = " ".join(lowered.split())
    return keyword or cleaned


def normalize_file_paths(file_paths):
    if not file_paths:
        return []
    if isinstance(file_paths, (str, Path)):
        return [Path(file_paths)]
    return [Path(path) for path in file_paths if path]


def read_materials(file_paths):
    paths = normalize_file_paths(file_paths)
    sources = []
    errors = []

    for path in paths:
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
    parts = []
    for source in sources:
        parts.append(f"===== {source['file_name']} =====\n{source['text']}")
    return "\n\n".join(parts)


def retrieve_context(question, file_paths):
    sources, errors = read_materials(file_paths)

    if not sources:
        if errors:
            return "\n".join(errors), "error", [], ""
        return "请先上传至少一个 PPTX、PDF 或 TXT 课程资料文件。", "error", [], ""

    full_text = format_sources_full_text(sources)
    lowered = question.lower()

    if "summary" in lowered or "summarize" in lowered or "总结" in question:
        return summarize_text(full_text, max_chars=9000), "summary", sources, full_text

    keyword = infer_keyword(question)
    result = search_in_text(full_text, keyword, max_results=14)

    if result == "No relevant content found.":
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]+|[\u4e00-\u9fff]{2,}", question)
        for token in tokens:
            result = search_in_text(full_text, token, max_results=14)
            if result != "No relevant content found.":
                return result, "keyword-token-search", sources, full_text

    if result == "No relevant content found.":
        return summarize_text(full_text, max_chars=6500), "fallback-summary", sources, full_text

    return result, "keyword-search", sources, full_text


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
    context, retrieval_mode, sources, full_text = retrieve_context(question, file_paths)
    file_names = [source["file_name"] for source in sources]

    if retrieval_mode == "error":
        return {
            "answer": context,
            "context": "",
            "source_text": "",
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
        "source_text": full_text,
        "retrieval_mode": retrieval_mode,
        "used_api": used_api,
        "file_names": file_names,
        "file_name": "、".join(file_names),
    }
