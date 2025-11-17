"use client";

interface FooterProps {
  darkMode: boolean;
  showFadeIn: boolean;
  urlStatus: "loading" | "success" | "error" | null;
}

export default function Footer({ darkMode, showFadeIn, urlStatus }: FooterProps) {
  if (urlStatus !== "success") {
    return null;
  }

  return (
    <footer 
      className={`mt-4 text-sm text-secondary text-center ${darkMode ? "dark" : "light"}`}
      style={{
        opacity: showFadeIn ? 1 : 0,
        transition: 'opacity 500ms ease-in-out'
      }}
    >
      API: <span className="font-mono">localhost:8080/ask-question</span>
    </footer>
  );
}

