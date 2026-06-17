import argparse
from pathlib import Path

from agent import answer_question


def main():
    parser = argparse.ArgumentParser(description="CourseMate Agent command-line interface")
    parser.add_argument(
        "file",
        help="Path to a PPTX, PDF, or TXT course material file.",
    )
    args = parser.parse_args()

    file_path = Path(args.file)
    print("CourseMate Agent started.")
    print(f"Using uploaded/local material: {file_path}")
    print("Type a question, or type 'exit' to quit.")
    print()

    while True:
        question = input(">>> ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not question:
            continue

        result = answer_question(question, file_path=file_path)
        print("\n[Agent Answer]")
        print(result["answer"])
        print("\n[Retrieved Context]")
        print(result["context"][:1200])
        print()


if __name__ == "__main__":
    main()
