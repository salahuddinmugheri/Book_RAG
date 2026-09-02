"use client";

import { useState } from "react";

type Source = {
  page: number;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

function renderAnswer(answer: string) {
  const parts = answer.split(/(\[Page\s+\d+\])/g);

  return parts.map((part, index) => {
    const match = part.match(/\[Page\s+(\d+)\]/);

    if (match) {
      return (
        <span
          key={index}
          className="mx-1 inline-flex items-center rounded-md border border-blue-200 bg-blue-50 px-2 py-0.5 align-middle text-xs font-semibold text-blue-700"
        >
          Page {match[1]}
        </span>
      );
    }

    return <span key={index}>{part}</span>;
  });
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  async function askQuestion() {
    if (!question.trim() || loading) return;

    const userQuestion = question.trim();

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const endpoint = baseUrl ? `${baseUrl}/ask` : "/api/ask";
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.error || `API request failed with status ${response.status}`);
      }

      if (data.error) {
        throw new Error(data.error);
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error: any) {
      console.error("API error:", error);

      const errorMessage =
        error?.message
          ? (error.message.startsWith("API request failed")
              ? "Sorry, I couldn't get an answer right now. Please check backend connection."
              : error.message)
          : "Sorry, I couldn't get an answer right now. Please try again.";

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: errorMessage,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLInputElement>
  ) {
    if (event.key === "Enter") {
      event.preventDefault();
      askQuestion();
    }
  }

  return (
    <main className="flex min-h-screen flex-col bg-[#f5f5f4] text-gray-900">

      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-gray-200/80 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-16 w-full max-w-5xl items-center justify-between px-4 sm:px-6">

          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gray-900 text-lg shadow-sm">
              📖
            </div>

            <div>
              <h1 className="text-sm font-semibold tracking-tight text-gray-900 sm:text-base">
                Why There Is No God
              </h1>

              <p className="text-xs text-gray-500">
                Book RAG Assistant
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-green-200 bg-green-50 px-3 py-1.5">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
            </span>

            <span className="text-xs font-medium text-green-700">
              Online
            </span>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <section className="flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-4xl px-4 py-8 sm:px-6 sm:py-10">

          {/* Welcome State */}
          {messages.length === 0 ? (
            <div className="flex min-h-[calc(100vh-190px)] flex-col items-center justify-center text-center">

              <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gray-900 text-4xl shadow-lg">
                📖
              </div>

              <p className="mb-2 text-sm font-medium text-gray-500">
                Ask questions about the book
              </p>

              <h2 className="max-w-2xl text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                Why There Is No God
              </h2>

              <p className="mt-4 max-w-xl text-sm leading-6 text-gray-500 sm:text-base">
                Explore the book through natural language. Ask about
                arguments, ideas, chapters, or specific topics and get
                answers grounded in the book&apos;s content.
              </p>

              <div className="mt-8 grid w-full max-w-2xl gap-3 sm:grid-cols-2">

                <button
                  onClick={() =>
                    setQuestion(
                      "Who is the author of the book?"
                    )
                  }
                  className="rounded-xl border border-gray-200 bg-white p-4 text-left text-sm text-gray-700 shadow-sm transition hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-md"
                >
                  <span className="font-medium text-gray-900">
                    About the author
                  </span>

                  <span className="mt-1 block text-xs text-gray-500">
                    Who wrote this book?
                  </span>
                </button>

                <button
                  onClick={() =>
                    setQuestion(
                      "What arguments does the book give against God's existence?"
                    )
                  }
                  className="rounded-xl border border-gray-200 bg-white p-4 text-left text-sm text-gray-700 shadow-sm transition hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-md"
                >
                  <span className="font-medium text-gray-900">
                    Main arguments
                  </span>

                  <span className="mt-1 block text-xs text-gray-500">
                    Explore the book&apos;s central arguments.
                  </span>
                </button>

                <button
                  onClick={() =>
                    setQuestion(
                      "What is the main idea of the book?"
                    )
                  }
                  className="rounded-xl border border-gray-200 bg-white p-4 text-left text-sm text-gray-700 shadow-sm transition hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-md"
                >
                  <span className="font-medium text-gray-900">
                    Main idea
                  </span>

                  <span className="mt-1 block text-xs text-gray-500">
                    Understand the book&apos;s overall message.
                  </span>
                </button>

                <button
                  onClick={() =>
                    setQuestion(
                      "What does the book say about religion?"
                    )
                  }
                  className="rounded-xl border border-gray-200 bg-white p-4 text-left text-sm text-gray-700 shadow-sm transition hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-md"
                >
                  <span className="font-medium text-gray-900">
                    Explore a topic
                  </span>

                  <span className="mt-1 block text-xs text-gray-500">
                    Ask about a specific subject.
                  </span>
                </button>

              </div>
            </div>
          ) : (
            /* Messages */
            <div className="space-y-8">

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={
                    message.role === "user"
                      ? "flex justify-end"
                      : "flex justify-start"
                  }
                >

                  {message.role === "user" ? (
                    /* User Message */
                    <div className="max-w-[88%] sm:max-w-[75%]">
                      <div className="rounded-2xl rounded-br-md bg-gray-900 px-4 py-3 text-sm leading-6 text-white shadow-sm sm:px-5">
                        {message.content}
                      </div>
                    </div>
                  ) : (
                    /* Assistant Message */
                    <div className="flex max-w-[92%] gap-3 sm:max-w-[82%]">

                      <div className="hidden h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gray-900 text-sm shadow-sm sm:flex">
                        📖
                      </div>

                      <div className="min-w-0">

                        <div className="rounded-2xl rounded-bl-md border border-gray-200 bg-white px-4 py-4 shadow-sm sm:px-5">

                          <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
                            Book RAG
                          </div>

                          <p className="whitespace-pre-wrap text-sm leading-7 text-gray-700 sm:text-[15px]">
                            {renderAnswer(message.content)}
                          </p>

                          {/* Source Cards */}
                          {message.sources &&
                            message.sources.length > 0 && (
                              <div className="mt-5 border-t border-gray-100 pt-4">

                                <div className="mb-3 flex items-center gap-2">
                                  <span className="text-sm">
                                    📚
                                  </span>

                                  <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                                    Sources
                                  </span>
                                </div>

                                <div className="grid gap-2 sm:grid-cols-2">
                                  {[
                                    ...new Map(
                                      message.sources.map((source) => [
                                        source.page,
                                        source,
                                      ])
                                    ).values(),
                                  ].map((source) => (
                                    <div
                                      key={source.page}
                                      className="flex items-center gap-3 rounded-xl border border-gray-200 bg-gray-50 p-3 transition hover:-translate-y-0.5 hover:border-blue-200 hover:bg-white hover:shadow-sm"
                                    >
                                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white text-sm shadow-sm">
                                        📄
                                      </div>

                                      <div className="min-w-0">
                                        <p className="text-sm font-semibold text-gray-800">
                                          Page {source.page}
                                        </p>

                                        <p className="text-[11px] text-gray-400">
                                          Book source
                                        </p>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {/* Loading Animation */}
              {loading && (
                <div className="flex justify-start">
                  <div className="flex max-w-[82%] gap-3">

                    <div className="hidden h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gray-900 text-sm shadow-sm sm:flex">
                      📖
                    </div>

                    <div className="rounded-2xl rounded-bl-md border border-gray-200 bg-white px-5 py-4 shadow-sm">

                      <div className="flex items-center gap-1.5">
                        <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.3s]" />
                        <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.15s]" />
                        <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
                      </div>

                    </div>
                  </div>
                </div>
              )}

            </div>
          )}
        </div>
      </section>

      {/* Input Area */}
      <footer className="sticky bottom-0 border-t border-gray-200/80 bg-[#f5f5f4]/95 px-4 py-4 backdrop-blur sm:px-6">

        <div className="mx-auto w-full max-w-4xl">

          <div className="rounded-2xl border border-gray-300 bg-white p-2 shadow-sm transition focus-within:border-gray-400 focus-within:shadow-md">

            <div className="flex items-center gap-2">

              <input
                type="text"
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Ask anything about the book..."
                disabled={loading}
                className="min-w-0 flex-1 bg-transparent px-3 py-2.5 text-sm text-gray-900 outline-none placeholder:text-gray-400 disabled:cursor-not-allowed disabled:opacity-60 sm:text-[15px]"
              />

              <button
                onClick={askQuestion}
                disabled={loading || !question.trim()}
                aria-label="Send question"
                className="flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-xl bg-gray-900 text-white transition hover:bg-gray-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    className="h-5 w-5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 12h14M13 6l6 6-6 6"
                    />
                  </svg>
                )}
              </button>

            </div>
          </div>

          <p className="mt-2 text-center text-[11px] text-gray-400 sm:text-xs">
            Answers are generated from the content of{" "}
            <span className="font-medium">
              Why There Is No God
            </span>
            .
          </p>

        </div>
      </footer>
    </main>
  );
}