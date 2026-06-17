import argparse
from pathlib import Path

from agent import answer_question


def main():
    parser = argparse.ArgumentParser(description="CourseMate Agent command-line interface")
    parser.add_argument(
        "files",
        nargs="+",
        help="One or more PPTX, PDF, or TXT course material files.",
    )
    args = parser.parse_args()

    file_paths = [Path(file) for file in args.files]
    print("CourseMate Agent started.")
    print("Using uploaded/local materials:")
    for file_path in file_paths:
        print(f"- {file_path}")
    print("Type a question, or type 'exit' to quit.")
    print()

    while True:
        question = input(">>> ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not question:
            continue

        result = answer_question(question, file_paths=file_paths)
        print("\n[Agent Answer]")
        print(result["answer"])
        print("\n[Retrieved Context]")
        print(result["context"][:1200])
        print("\n[Called File Original Text]")
        print(result["source_text"][:1200])
        print()


if __name__ == "__main__":
    main()
