"use client";
import { useRef, useEffect } from "react";
import SuggestionButton from "./SuggestionButton";
import TextToSpeechButton from "./TextToSpeechButton";

interface Message {
  type: "user" | "bot";
  content: string;
  suggestions?: Record<string, string>;
}

interface ChatWindowProps {
  messages: Message[];
  darkMode: boolean;
  onQuestionSubmit: (question: string) => void;
}

export default function ChatWindow({ messages, darkMode, onQuestionSubmit }: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <section className={`w-full flex-1 overflow-y-scroll px-4 ${messages.length > 0 ? "mb-14" : ""}`}>
      <div className="flex flex-col gap-4">
        {messages.length > 0 && messages.map((msg, i) => {
          return (
            <div key={i} className="relative" style={{ alignSelf: msg.type === "user" ? "flex-end" : "flex-start" }}>
              <div
                className={`${
                  msg.type === "user"
                    ? `chat-bubble-user ${darkMode ? "dark" : "light"}`
                    : `chat-bubble-bot ${darkMode ? "dark" : "light"}`
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
                  <>
                    <span
                      dangerouslySetInnerHTML={{
                        __html: msg.content
                          .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
                          .replace(/\n/g, "<br/>"),
                      }}
                    />
                    <TextToSpeechButton text={msg.content} darkMode={darkMode} />
                    {msg.suggestions && Object.keys(msg.suggestions).length > 0 && (
                      <div className={`mt-4 pt-3 divider-thin flex flex-row flex-wrap gap-2 ${
                        darkMode ? "dark" : "light"
                      }`}>
                        {Object.entries(msg.suggestions).map(([text, question], idx) => {
                          // Check if this is a Google or YouTube link
                          const isGoogle = text === "Google" && question.startsWith("http");
                          const isYouTube = text === "YouTube" && question.startsWith("http");
                          
                          if (isGoogle || isYouTube) {
                            return (
                              <a
                                key={idx}
                                href={question}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`ref-link-button ${isGoogle ? "google" : "youtube"} font-extrabold flex gap-0 ${
                                  darkMode ? "dark" : "light"
                                }`}
                                style={isGoogle ? { letterSpacing: 0 } : {}}
                              >
                                {isGoogle ? (
                                  <>
                                    <span style={{ color: "#2563eb" }}>G</span>
                                    <span style={{ color: "#dc2626" }}>o</span>
                                    <span style={{ color: "#fb923c" }}>o</span>
                                    <span style={{ color: "#2563eb" }}>g</span>
                                    <span style={{ color: "#16a34a" }}>l</span>
                                    <span style={{ color: "#dc2626" }}>e</span>
                                  </>
                                ) : (
                                  <>
                                    You<span>Tube</span>
                                  </>
                                )}
                              </a>
                            );
                          }
                          
                          // Regular suggestion button
                          return (
                            <SuggestionButton
                              key={idx}
                              text={text}
                              question={question}
                              onClick={onQuestionSubmit}
                              darkMode={darkMode}
                            />
                          );
                        })}
                      </div>
                    )}
                  </>
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
  );
}

