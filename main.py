from pathlib import Path

from tools import read_local_file, search_in_text, summarize_text


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_FILE_PATH = BASE_DIR / "data" / "Week 13-15.pptx"
SYSTEM_PROMPT_PATH = BASE_DIR / "prompts" / "system_prompt.txt"


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
        "总结",
        "请总结",
        "介绍",
        "说明",
    ]

    for phrase in removable_phrases:
        lowered = lowered.replace(phrase, " ")

    keyword = " ".join(lowered.split())
    return keyword or cleaned


def agent_answer(question, file_path=DEFAULT_FILE_PATH):
    material_text = read_local_file(file_path)

    if material_text.startswith("File not found") or material_text.startswith("Unsupported"):
        return material_text

    if any(word in question.lower() for word in ["summary", "summarize"]) or "总结" in question:
        summary = summarize_text(material_text)
        return (
            "Here is a brief summary based on the local course material:\n\n"
            f"{summary}"
        )

    keyword = infer_keyword(question)
    result = search_in_text(material_text, keyword)

    if result == "No relevant content found.":
        return (
            "No exact keyword match was found in the local material. "
            "Try a shorter keyword such as 'prompting', 'agent', or 'Experiment 2'."
        )

    return (
        "I found the following relevant content in the local course material:\n\n"
        f"{result}"
    )


def main():
    print("CourseMate Agent started.")
    print(f"Using material: {DEFAULT_FILE_PATH}")
    print("Type a question, or type 'exit' to quit.")
    print()

    while True:
        question = input(">>> ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not question:
            continue

        print("\n[Agent Answer]")
        print(agent_answer(question))
        print()


if __name__ == "__main__":
    main()
