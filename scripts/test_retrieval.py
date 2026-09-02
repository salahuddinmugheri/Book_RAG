from rag import retrieve_chunks


question = input(
    "Enter a question: "
).strip()


if not question:
    print("Question cannot be empty.")
    exit()


print(f"\nQuestion: {question}")
print("\nRetrieving relevant chunks...")


try:

    results = retrieve_chunks(
        question
    )

    print(
        f"\nFinal retrieved chunks: {len(results)}"
    )

    if not results:
        print(
            "\nNo relevant chunks were found."
        )
        exit()

    print("\n" + "=" * 70)

    for i, result in enumerate(
        results,
        start=1
    ):

        print(f"\nRESULT {i}")

        print(
            f"Chunk ID: {result['chunk_id']}"
        )

        print(
            f"Page: {result['page']}"
        )

        print(
            f"Semantic score: "
            f"{result['_semantic_score']:.4f}"
        )

        print(
            f"Lexical score: "
            f"{result['_lexical_score']:.4f}"
        )

        print(
            f"Rerank score: "
            f"{result['_rerank_score']:.4f}"
        )

        print("\nText:")
        print(result["text"])

        print("-" * 70)


except Exception as error:

    print(
        f"\nRetrieval error: {error}"
    )