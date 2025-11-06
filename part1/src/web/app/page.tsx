"use client";
import { useState, useEffect, useRef } from "react";

function isValidUrl(urlStr: string) {
  try {
    // Basic check: must have http(s) and a dot
    const u = new URL(urlStr);
    return /^https?:\/\/.+\..+$/.test(urlStr);
  } catch {
    return false;
  }
}

export default function Home() {
  const [input, setInput] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<
    { type: "user" | "bot"; content: string }[]
  >([]);
  const [darkMode, setDarkMode] = useState(false);
  const [submittedUrl, setSubmittedUrl] = useState<string | null>(null);
  const [urlStatus, setUrlStatus] = useState<"loading" | "success" | "error" | null>(null);
  const [recipeName, setRecipeName] = useState<string | null>(null);
  const [recipeUrl, setRecipeUrl] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const isFirstSubmission = submittedUrl === null || urlStatus !== "success";

    // Only validate URL for first submission
    if (isFirstSubmission) {
      if (!isValidUrl(input)) {
        setError("Please enter a valid URL (starting with http:// or https://)");
        return;
      }
      
      // Set URL and loading state (update if retrying after error)
      setSubmittedUrl(input); // this is the URL that was submitted to the API
      setUrlStatus("loading");
      setSubmitting(true);
    } else {
      // Subsequent submissions: questions to ask-question
      setSubmitting(true);
      setMessages((msgs) => [
        ...msgs,
        { type: "user", content: input },
        { type: "bot", content: "Loading" },
      ]);
    }

    try {
      let res: Response;
      let data: any;

      if (isFirstSubmission) {
        // First submission: URL to get-recipe
        res = await fetch("http://localhost:8080/get-recipe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: input }),
        });

        data = await res.json();

        // Check for error in response
        if (data.error) {
          setUrlStatus("error");
          setError(data.error);
          return;
        }

        if (!res.ok) {
          setUrlStatus("error");
          setError(data.error || "Recipe service error");
          return;
        }

        if (data.status === "saved" && typeof data.num_steps === "number") {
          setUrlStatus("success");
          setError(null); // Clear any previous errors
          // Store recipe name and URL from API response
          if (data.recipe_name) {
            setRecipeName(data.recipe_name);
          }
          if (data.recipe_url) {
            setRecipeUrl(data.recipe_url);
          }
          // Add bot message when recipe is successfully processed
          setMessages([{ type: "bot", content: "Recipe processed! Ask a question" }]);
        } else {
          setUrlStatus("error");
          setError(data.error || "Failed to process recipe");
        }
      } else {
        // Subsequent submissions: questions to ask-question
        res = await fetch("http://localhost:8080/ask-question", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: input }),
        });

        if (!res.ok) {
          throw new Error("Question service error");
        }

        data = await res.json();

        let reply: string;
        if (data.answer) {
          reply = data.answer;
        } else if (data.message) {
          reply = data.message;
        } else {
          reply = "Sorry, I couldn't process your question.";
        }

        setMessages((msgs) => [
          ...msgs.slice(0, msgs.length - 1),
          { type: "bot", content: reply },
        ]);
      }

      setInput("");
    } catch (err: any) {
      if (isFirstSubmission) {
        setUrlStatus("error");
        // Default error message if we can't extract from response
        setError("Failed to fetch recipe. Please try again.");
      } else {
        const errorMessage = "Failed to process your question. Please try again.";
        setMessages((msgs) => [
          ...msgs.slice(0, msgs.length - 1),
          { type: "bot", content: errorMessage },
        ]);
        setError("Failed to process question.");
      }
    } finally {
      setSubmitting(false);
      // Keep focus on input after submission
      inputRef.current?.focus();
    }
  }

  return (
    <div
      className={`flex min-h-screen justify-center transition-colors duration-200 ${
        darkMode ? "bg-black" : "bg-zinc-100"
      }`}
    >
      <main
        className={`flex h-screen w-3/5 flex-col items-center relative px-4 py-12 transition duration-200 ${
          darkMode ? "bg-zinc-900" : "bg-white"
        }`}
      >
        {/* Header */}
        <div className="w-full flex items-center justify-center mb-6 relative">
          <h1 className={`text-center text-4xl font-bold tracking-tight ${darkMode ? "text-white" : "text-black"}`}>
            Welcome to{" "}
            <span className="bg-orange-500 text-white px-2 py-1 rounded">
              CookBaum
            </span>
          </h1>
          {/* Toggle dark mode */}
          <button
            onClick={() => setDarkMode((dm) => !dm)}
            className="absolute right-0 transition-colors rounded-full p-2 bg-orange-100 hover:bg-orange-200 dark:bg-zinc-800 dark:hover:bg-orange-600"
            type="button"
          >
            {darkMode ? (
              // Sun icon
              // https://icons.getbootstrap.com/icons/sun-fill/
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="#FB923C" className="bi bi-sun-fill" viewBox="0 0 16 16">
                <path d="M8 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8M8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0m0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13m8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5M3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8m10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0m-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0m9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707M4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708"/>
              </svg>
            ) : (
              // Moon icon
              // https://icons.getbootstrap.com/icons/moon-fill/
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="#FB923C" className="bi bi-moon-fill" viewBox="0 0 16 16">
                <path d="M6 .278a.77.77 0 0 1 .08.858 7.2 7.2 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.318 7.277q.792-.001 1.533-.16a.79.79 0 0 1 .81.316.73.73 0 0 1-.031.893A8.35 8.35 0 0 1 8.344 16C3.734 16 0 12.286 0 7.71 0 4.266 2.114 1.312 5.124.06A.75.75 0 0 1 6 .278"/>
              </svg>
            )}
          </button>
        </div>
        {/* Submitted URL display */}
        {submittedUrl && (
          <div className="w-full flex justify-center mb-12">
            <span
              className={`italic text-zinc-500 px-3 py-1 rounded-xl transition-colors ${
                urlStatus === "loading"
                  ? "bg-orange-200"
                  : urlStatus === "success"
                  ? "bg-green-200"
                  : urlStatus === "error"
                  ? "bg-red-200"
                  : ""
              }`}
            >
              {urlStatus === "success" && recipeName && recipeUrl ? (
                <a
                  href={recipeUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-zinc-500 hover:text-zinc-700 underline"
                >
                  {recipeName}
                </a>
              ) : (
                submittedUrl
              )}
            </span>
          </div>
        )}
        {/* Chat history */}
        <section className={`w-full flex-1 overflow-y-scroll px-4 ${messages.length > 0 ? "mb-14" : ""}`}>
          <div className="flex flex-col gap-4">
            {messages.length > 0 && messages.map((msg, i) => {
              const bgColor = msg.type === "user"
                ? darkMode ? "rgb(234, 88, 12)" : "rgb(251, 146, 60)" // orange-600 : orange-400
                : darkMode ? "rgb(39, 39, 42)" : "rgb(228, 228, 231)"; // zinc-800 : zinc-200
              
              return (
              <div key={i} className="relative" style={{ alignSelf: msg.type === "user" ? "flex-end" : "flex-start" }}>
                {/* Tail for bot messages (left side) */}
                {msg.type === "bot" && (
                  <div
                    style={{
                      position: 'absolute',
                      left: '-8px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      width: 0,
                      height: 0,
                      borderTop: '8px solid transparent',
                      borderBottom: '8px solid transparent',
                      borderRight: `8px solid ${bgColor}`,
                    }}
                  />
                )}
                {/* Tail for user messages (right side) */}
                {msg.type === "user" && (
                  <div
                    style={{
                      position: 'absolute',
                      right: '-8px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      width: 0,
                      height: 0,
                      borderTop: '8px solid transparent',
                      borderBottom: '8px solid transparent',
                      borderLeft: `8px solid ${bgColor}`,
                    }}
                  />
                )}
                <div
                  className={`px-4 py-3 rounded-xl max-w-full whitespace-pre-line transition-colors ${
                    msg.type === "user"
                      ? darkMode
                        ? "bg-orange-600 text-white"
                        : "bg-orange-400 text-white"
                      : darkMode
                      ? "bg-zinc-800 text-zinc-100"
                      : "bg-zinc-200 text-black"
                  }`}
                >
                  {msg.type === "bot" && msg.content === "Loading" ? (
                    <div className="flex items-center gap-2">
                      <span>Loading</span>
                      <svg
                        className="animate-spin h-4 w-4"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                    </div>
                  ) : msg.type === "bot" ? (
                    <span
                      dangerouslySetInnerHTML={{
                        __html: msg.content
                          .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
                          .replace(/\n/g, "<br/>"),
                      }}
                    />
                  ) : (
                    msg.content
                  )}
                </div>
              </div>
            );
            })}
            <div ref={messagesEndRef} />
          </div>
        </section>
        {/* Divider above text input box */}
        {messages.length > 0 && urlStatus === "success" && (
          <div 
            className="w-2/3 border-t border-zinc-300 dark:border-zinc-700 absolute left-1/2 -translate-x-1/2"
            style={{
              bottom: 'calc(8rem + 11px)',
              transition: 'bottom 500ms ease-in-out'
            }}
          ></div>
        )}
        {/* Input form */}
        {/* Disgusting transition code that makes it move down when recipe is inputted */}
        <form 
          style={{
            transition: 'top 500ms ease-in-out, transform 500ms ease-in-out'
          }}
          className={`w-2/3 absolute left-1/2 -translate-x-1/2 ${
            urlStatus !== "success" 
              ? "top-1/2 -translate-y-1/2" 
              : "top-[calc(100%-8rem)] translate-y-0"
          }`}
          onSubmit={handleSubmit} 
          autoComplete="off"
        >
          {urlStatus !== "success" && (
            <div className="text-zinc-500 text-center italic text-lg mb-4">
              Get started...
            </div>
          )}
          <div className="relative">
            <input
              ref={inputRef}
              className={`w-full rounded-xl border pr-12 px-4 py-3 outline-none transition-colors text-base placeholder-zinc-400 shadow-sm
                ${
                  darkMode
                    ? "bg-zinc-800 border-zinc-700 text-zinc-100 focus:border-orange-400"
                    : "bg-zinc-100 border-zinc-300 text-zinc-900 focus:border-orange-500"
                }
              `}
              type={urlStatus === "success" ? "text" : "url"}
              required
              pattern={urlStatus === "success" ? undefined : "https?://.+"}
              autoFocus
              disabled={submitting}
              placeholder={urlStatus === "success" ? "Ask a question about the recipe..." : "Paste a recipe URL (e.g. https://...)"}
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button
              type="submit"
              disabled={submitting || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:ring-2 hover:ring-orange-500 disabled:hover:ring-0"
            >
              {/* https://icons.getbootstrap.com/icons/arrow-right-short/ */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="currentColor"
                className={`bi bi-arrow-right-short ${darkMode ? "text-zinc-100" : "text-zinc-900"}`}
                viewBox="0 0 16 16"
              >
                <path fillRule="evenodd" d="M4 8a.5.5 0 0 1 .5-.5h5.793L8.146 5.354a.5.5 0 1 1 .708-.708l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L10.293 8.5H4.5A.5.5 0 0 1 4 8"/>
              </svg>
            </button>
          </div>
        </form>
        {/* Error message */}
        {error && urlStatus === "error" && (
          <p className="text-sm text-red-500 text-center mt-2">{error}</p>
        )}
        {/* Footer */}
        {urlStatus === "success" && (
          <footer className="mt-4 text-sm text-zinc-400 text-center">
            API: <span className="font-mono">localhost:8080/ask-question</span>
          </footer>
        )}
      </main>
    </div>
  );
}
