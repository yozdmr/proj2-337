"use client";
import { useState, useEffect, useRef } from "react";
import SuggestionButton from "./components/SuggestionButton";
import Header from "./components/Header";
import Footer from "./components/Footer";
import ChatWindow from "./components/ChatWindow";
import SpeechToTextButton from "./components/SpeechToTextButton";

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
    { type: "user" | "bot"; content: string; suggestions?: Record<string, string> }[]
  >([]);
  const [darkMode, setDarkMode] = useState(false);
  const [submittedUrl, setSubmittedUrl] = useState<string | null>(null);
  const [urlStatus, setUrlStatus] = useState<"loading" | "success" | "error" | null>(null);
  const [recipeName, setRecipeName] = useState<string | null>(null);
  const [recipeUrl, setRecipeUrl] = useState<string | null>(null);
  const [showFadeIn, setShowFadeIn] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Trigger fade-in after input box transition completes (500ms)
  useEffect(() => {
    if (urlStatus === "success") {
      const timer = setTimeout(() => {
        setShowFadeIn(true);
      }, 500);
      return () => clearTimeout(timer);
    } else {
      setShowFadeIn(false);
    }
  }, [urlStatus]);

  async function handleQuestionSubmit(question: string) {
    setError(null);
    setSubmitting(true);
    setMessages((msgs) => [
      ...msgs,
      { type: "user", content: question },
      { type: "bot", content: "Loading" },
    ]);

    try {
      const res = await fetch("http://localhost:8080/ask-question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error("Question service error");
      }

      const data = await res.json();

      let reply: string;
      let suggestions: Record<string, string> | undefined;
      if (data.answer) {
        reply = data.answer;
      } else if (data.message) {
        reply = data.message;
      } else {
        reply = "Sorry, I couldn't process your question.";
      }

      // Extract suggestions if present (expecting a dictionary/object)
      if (data.suggestions && typeof data.suggestions === "object" && !Array.isArray(data.suggestions)) {
        suggestions = data.suggestions;
      }

      setMessages((msgs) => [
        ...msgs.slice(0, msgs.length - 1),
        { type: "bot", content: reply, suggestions },
      ]);
    } catch (err: any) {
      const errorMessage = "Failed to process your question. Please try again.";
      setMessages((msgs) => [
        ...msgs.slice(0, msgs.length - 1),
        { type: "bot", content: errorMessage },
      ]);
      setError("Failed to process question.");
    } finally {
      setSubmitting(false);
      // Keep focus on input after submission
      inputRef.current?.focus();
    }
  }

  async function handleReset() {
    try {
      // Call the reset endpoint
      await fetch("http://localhost:8080/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      
      // Reset all UI state to default
      setInput("");
      setSubmitting(false);
      setError(null);
      setMessages([]);
      setSubmittedUrl(null);
      setUrlStatus(null);
      setRecipeName(null);
      setRecipeUrl(null);
      setShowFadeIn(false);
      
      // Focus on input after reset
      inputRef.current?.focus();
    } catch (err: any) {
      console.error("Failed to reset:", err);
      // Still reset UI state even if API call fails
      setInput("");
      setSubmitting(false);
      setError(null);
      setMessages([]);
      setSubmittedUrl(null);
      setUrlStatus(null);
      setRecipeName(null);
      setRecipeUrl(null);
      setShowFadeIn(false);
      inputRef.current?.focus();
    }
  }

  async function handleSpeechTranscript(transcript: string) {
    if (!transcript.trim()) {
      return;
    }

    const trimmedTranscript = transcript.trim();
    setInput(trimmedTranscript);

    // Automatically submit the transcribed text
    // If we're in question mode (recipe already loaded), submit as question
    if (urlStatus === "success") {
      await handleQuestionSubmit(trimmedTranscript);
      setInput("");
    } else {
      // For URL input mode, validate and submit if it's a valid URL
      if (isValidUrl(trimmedTranscript)) {
        // Trigger form submission by calling handleSubmit
        const form = inputRef.current?.closest("form");
        if (form) {
          const submitEvent = new Event("submit", { bubbles: true, cancelable: true });
          form.dispatchEvent(submitEvent);
        }
      }
      // If not a valid URL, just leave it in the input for user to review
    }
  }

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
      await handleQuestionSubmit(input);
      setInput("");
      return;
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
          setMessages([{ type: "bot", content: "Hi there, my name is Simon - your AI cooking assistant. Ask me anything you like!" }]);
        } else {
          setUrlStatus("error");
          setError(data.error || "Failed to process recipe");
        }
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
    <div className={`flex min-h-screen justify-center container-bg ${darkMode ? "dark" : "light"}`}>
      <main className={`flex h-screen w-3/5 flex-col items-center relative px-4 py-12 main-content ${darkMode ? "dark" : "light"}`}>
        <Header 
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          urlStatus={urlStatus}
          recipeUrl={recipeUrl}
        />
        <ChatWindow 
          messages={messages}
          darkMode={darkMode}
          onQuestionSubmit={handleQuestionSubmit}
        />
        {/* Divider above text input box */}
        {messages.length > 0 && urlStatus === "success" && (
          <div>
            <div 
              className={`w-2/3 divider-thin absolute left-1/2 -translate-x-1/2 ${
                darkMode ? "dark" : "light"
              }`}
              style={{
                bottom: 'calc(8rem + 11px)',
                transition: 'bottom 500ms ease-in-out, opacity 500ms ease-in-out',
                opacity: showFadeIn ? 1 : 0
              }}
            ></div>
          </div>
        )}
        {/* Suggestion buttons - show after recipe is processed, before first question */}
        {urlStatus === "success" && !messages.some(msg => msg.type === "user") && (
          <div 
            className="w-2/3 absolute left-1/2 -translate-x-1/2 flex flex-col gap-2"
            style={{
              bottom: 'calc(8rem + 11px + 1rem)',
              transition: 'bottom 500ms ease-in-out, opacity 500ms ease-in-out',
              opacity: showFadeIn ? 1 : 0
            }}
          >
            <h4 className={`text-sm text-secondary text-left ml-2 font-medium italic ${darkMode ? "dark" : "light"}`}>Suggestions:</h4>
            <SuggestionButton
              text="What's the whole recipe?"
              question="Display the recipe"
              onClick={handleQuestionSubmit}
              darkMode={darkMode}
              fullWidth={true}
            />
            <SuggestionButton
              text="What should I do first?"
              question="What should I do first?"
              onClick={handleQuestionSubmit}
              darkMode={darkMode}
              fullWidth={true}
            />
            <SuggestionButton
              text="What ingredients do I need in this recipe?"
              question="What ingredients do I need in this recipe?"
              onClick={handleQuestionSubmit}
              darkMode={darkMode}
              fullWidth={true}
            />
          </div>
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
            <div className={`text-secondary text-center italic text-lg mb-4 ${darkMode ? "dark" : "light"}`}>
              Get started...
            </div>
          )}
          <div className="relative">
            <button
              type="button"
              onClick={handleReset}
              disabled={submitting || submittedUrl === null || urlStatus !== "success"}
              className={`icon-button absolute left-2 top-1/2 -translate-y-1/2 ${
                submitting || submittedUrl === null || urlStatus !== "success"
                  ? "disabled"
                  : darkMode
                  ? "dark"
                  : "light"
              }`}
              title="Reset"
            >
              {/* https://icons.getbootstrap.com/icons/arrow-counterclockwise/ */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="currentColor"
                viewBox="0 0 16 16"
              >
                <path fillRule="evenodd" d="M8 3a5 5 0 1 1-4.546 2.914.5.5 0 0 0-.908-.417A6 6 0 1 0 8 2z" stroke="currentColor" strokeWidth="0.5"/>
                <path d="M8 4.466V.534a.25.25 0 0 0-.41-.192L5.23 2.308a.25.25 0 0 0 0 .384l2.36 1.966A.25.25 0 0 0 8 4.466" stroke="currentColor" strokeWidth="0.5"/>
              </svg>
            </button>
            <input
              ref={inputRef}
              className={`input-field ${darkMode ? "dark" : "light"} ${urlStatus === "success" ? "pr-28" : "pr-12"}`}
              type={urlStatus === "success" ? "text" : "url"}
              required
              pattern={urlStatus === "success" ? undefined : "https?://.+"}
              autoFocus
              disabled={submitting}
              placeholder={urlStatus === "success" ? "Ask a question about the recipe..." : "Paste a recipe URL (e.g. https://...)"}
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <SpeechToTextButton 
              disabled={submitting}
              darkMode={darkMode}
              onTranscript={handleSpeechTranscript}
            />
            <button
              type="submit"
              disabled={submitting || !input.trim()}
              className={`icon-button absolute right-2 top-1/2 -translate-y-1/2 ${darkMode ? "dark" : "light"}`}
            >
              {/* https://icons.getbootstrap.com/icons/arrow-right-short/ */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="currentColor"
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
        <Footer 
          darkMode={darkMode}
          showFadeIn={showFadeIn}
          urlStatus={urlStatus}
        />
      </main>
    </div>
  );
}
