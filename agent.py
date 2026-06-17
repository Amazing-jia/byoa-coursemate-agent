import os
import sys
import json
import urllib.error
import urllib.request
from pathlib import Path

VENDOR_DIR = Path(__file__).resolve().parent / ".vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from tools import read_local_file, search_in_text, summarize_text


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_FILE_PATH = BASE_DIR / "data" / "Week 13-15.pptx"
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
    ]

    for phrase in removable_phrases:
        lowered = lowered.replace(phrase, " ")

    keyword = " ".join(lowered.split())
    return keyword or cleaned


def retrieve_context(question, file_path=DEFAULT_FILE_PATH):
    material_text = read_local_file(file_path)

    if material_text.startswith("File not found") or material_text.startswith("Unsupported"):
        return material_text, "error"

    lowered = question.lower()
    if "summary" in lowered or "summarize" in lowered or "总结" in question:
        return summarize_text(material_text, max_chars=5000), "summary"

    keyword = infer_keyword(question)
    result = search_in_text(material_text, keyword, max_results=8)

    if result == "No relevant content found.":
        return summarize_text(material_text, max_chars=3500), "fallback-summary"

    return result, "keyword-search"


def answer_with_openai(question, context, retrieval_mode):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "OPENAI_API_KEY is not set. Add your API key to a .env file, then restart the app.\n\n"
            "Example:\n"
            "OPENAI_API_KEY=your_api_key_here\n"
            "OPENAI_MODEL=gpt-4.1-mini"
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    system_prompt = load_system_prompt()
    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    f"User question:\n{question}\n\n"
                    f"Retrieved local course context ({retrieval_mode}):\n{context}\n\n"
                    "Answer the question using the retrieved context. "
                    "If the context does not fully answer it, say what is missing."
                ),
            },
        ],
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        return f"OpenAI API request failed ({error.code}):\n{detail}"
    except urllib.error.URLError as error:
        return f"OpenAI API connection failed: {error.reason}"

    if "output_text" in data:
        return data["output_text"].strip()

    texts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                texts.append(content["text"])

    return "\n".join(texts).strip() or "The API returned no text."


def answer_question(question, file_path=DEFAULT_FILE_PATH, use_api=True):
    context, retrieval_mode = retrieve_context(question, file_path)

    if retrieval_mode == "error":
        return {
            "answer": context,
            "context": "",
            "retrieval_mode": retrieval_mode,
            "used_api": False,
        }

    if use_api:
        answer = answer_with_openai(question, context, retrieval_mode)
        used_api = not answer.startswith("OPENAI_API_KEY is not set.")
    else:
        answer = (
            "External API is disabled. Here is the retrieved local context:\n\n"
            f"{context}"
        )
        used_api = False

    return {
        "answer": answer,
        "context": context,
        "retrieval_mode": retrieval_mode,
        "used_api": used_api,
    }
