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
      className={`${fullWidth ? "w-full" : "w-auto"} rounded-xl border px-4 py-2 text-sm text-left transition-colors hover:border-orange-500 ${
        darkMode
          ? "bg-zinc-800 border-zinc-700 text-zinc-100 hover:bg-zinc-700"
          : "bg-zinc-100 border-zinc-300 text-zinc-900 hover:bg-zinc-200"
      }`}
    >
      {text}
    </button>
  );
}

