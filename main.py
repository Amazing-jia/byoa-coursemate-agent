from agent import DEFAULT_FILE_PATH, answer_question


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

        result = answer_question(question)
        print("\n[Agent Answer]")
        print(result["answer"])
        print("\n[Retrieved Context]")
        print(result["context"][:1200])
        print()


if __name__ == "__main__":
    main()
