"use client";

interface SuggestionButtonProps {
  text: string;
  question: string;
  onClick: (question: string) => void;
  darkMode: boolean;
  fullWidth?: boolean;
}

export default function SuggestionButton({ text, question, onClick, darkMode, fullWidth = false }: SuggestionButtonProps) {
  return (
    <button
      type="button"
      onClick={() => onClick(question)}
      className={`suggestion-button ${darkMode ? "dark" : "light"} ${fullWidth ? "full-width" : ""}`}
    >
      {text}
    </button>
  );
}

