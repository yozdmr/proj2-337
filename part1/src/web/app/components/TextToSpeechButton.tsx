"use client";
import { useState, useEffect, useRef } from "react";
import { stopAllSpeech } from "./useTextToSpeech";

interface TextToSpeechButtonProps {
  text: string;
  darkMode: boolean;
}

export default function TextToSpeechButton({ text, darkMode }: TextToSpeechButtonProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);

  // Initialize speech synthesis
  useEffect(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      synthRef.current = window.speechSynthesis;
    }

    // Cleanup: stop speech when component unmounts
    return () => {
      if (synthRef.current && utteranceRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);

  // Stop any ongoing speech when text changes
  useEffect(() => {
    stopAllSpeech();
    setIsPlaying(false);
    setIsPaused(false);
  }, [text]);

  const handleToggleSpeech = () => {
    if (!synthRef.current) {
      console.warn("Speech synthesis not supported");
      return;
    }

    // If currently playing, pause it
    if (isPlaying && !isPaused) {
      synthRef.current.pause();
      setIsPaused(true);
      return;
    }

    // If paused, resume it
    if (isPaused) {
      synthRef.current.resume();
      setIsPaused(false);
      return;
    }

    // If not playing, start new speech
    // Stop any existing speech first (from this or other instances)
    stopAllSpeech();
    setIsPlaying(false);
    setIsPaused(false);

    // Strip HTML tags, markdown formatting, and decode HTML entities for clean text
    const cleanText = text
      .replace(/<[^>]*>/g, "") // Remove HTML tags
      .replace(/\*\*(.+?)\*\*/g, "$1") // Remove markdown bold (**text**)
      .replace(/\*(.+?)\*/g, "$1") // Remove markdown italic (*text*)
      .replace(/`(.+?)`/g, "$1") // Remove markdown code (`text`)
      .replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1") // Remove markdown links ([text](url))
      .replace(/&nbsp;/g, " ") // Replace &nbsp; with space
      .replace(/&amp;/g, "&") // Replace &amp; with &
      .replace(/&lt;/g, "<") // Replace &lt; with <
      .replace(/&gt;/g, ">") // Replace &gt; with >
      .replace(/&quot;/g, '"') // Replace &quot; with "
      .replace(/&#39;/g, "'") // Replace &#39; with '
      .replace(/\n+/g, " ") // Replace newlines with spaces
      .replace(/\s+/g, " ") // Replace multiple spaces with single space
      .trim();

    if (!cleanText) {
      return;
    }

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0; // Normal speed
    utterance.pitch = 1.0; // Normal pitch
    utterance.volume = 1.0; // Full volume

    utterance.onstart = () => {
      setIsPlaying(true);
      setIsPaused(false);
    };

    utterance.onend = () => {
      setIsPlaying(false);
      setIsPaused(false);
      utteranceRef.current = null;
    };

    utterance.onerror = (error) => {
      // Only log actual errors, not intentional stops (canceled/interrupted)
      if (error.error !== "canceled" && error.error !== "interrupted") {
        console.error("Speech synthesis error:", error);
      }
      setIsPlaying(false);
      setIsPaused(false);
      utteranceRef.current = null;
    };

    utteranceRef.current = utterance;
    synthRef.current.speak(utterance);
  };

  const handleStop = () => {
    stopAllSpeech();
    setIsPlaying(false);
    setIsPaused(false);
    utteranceRef.current = null;
  };

  // Check if speech synthesis is supported
  if (typeof window === "undefined" || !("speechSynthesis" in window)) {
    return null;
  }

  return (
    <div className="mt-2">
      <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-3xl border ${
        darkMode ? "border-zinc-600" : "border-zinc-300"
      }`}>
        <button
          onClick={handleToggleSpeech}
          className={`icon-button stt ${darkMode ? "dark" : "light"}`}
          title={isPaused ? "Resume" : isPlaying ? "Pause" : "Play"}
          aria-label={isPaused ? "Resume speech" : isPlaying ? "Pause speech" : "Play speech"}
        >
          {isPaused ? (
            // Play icon (resume)
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              fill="currentColor"
              viewBox="0 0 16 16"
            >
              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M6.79 5.093A.5.5 0 0 0 6 5.5v5a.5.5 0 0 0 .79.407l3.5-2.5a.5.5 0 0 0 0-.814z" />
            </svg>
          ) : isPlaying ? (
            // Pause icon
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              fill="currentColor"
              viewBox="0 0 16 16"
            >
              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M6.25 5C5.56 5 5 5.56 5 6.25v3.5a1.25 1.25 0 1 0 2.5 0v-3.5C7.5 5.56 6.94 5 6.25 5m3.5 0c-.69 0-1.25.56-1.25 1.25v3.5a1.25 1.25 0 1 0 2.5 0v-3.5C11 5.56 10.44 5 9.75 5" />
            </svg>
          ) : (
            // Volume-up icon (when starting from beginning)
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              fill="currentColor"
              viewBox="0 0 16 16"
            >
              <path d="M11.536 14.01A8.47 8.47 0 0 0 14.026 8a8.47 8.47 0 0 0-2.49-6.01l-.708.707A7.48 7.48 0 0 1 13.025 8c0 2.071-.84 3.946-2.197 5.303z"/>
              <path d="M10.121 12.596A6.48 6.48 0 0 0 12.025 8a6.48 6.48 0 0 0-1.904-4.596l-.707.707A5.48 5.48 0 0 1 11.025 8a5.48 5.48 0 0 1-1.61 3.89z"/>
              <path d="M8.707 11.182A4.5 4.5 0 0 0 10.025 8a4.5 4.5 0 0 0-1.318-3.182L8 5.525A3.5 3.5 0 0 1 9.025 8 3.5 3.5 0 0 1 8 10.475zM6.717 3.55A.5.5 0 0 1 7 4v8a.5.5 0 0 1-.812.39L3.825 10.5H1.5A.5.5 0 0 1 1 10V6a.5.5 0 0 1 .5-.5h2.325l2.363-1.89a.5.5 0 0 1 .529-.06"/>
            </svg>
          )}
        </button>
        <button
          onClick={handleStop}
          disabled={!isPlaying}
          className={`icon-button stt-stop ${darkMode ? "dark" : "light"} ${!isPlaying ? "disabled" : ""}`}
          title="Stop"
          aria-label="Stop speech"
        >
          {/* Stop icon */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            fill="currentColor"
            viewBox="0 0 16 16"
          >
            <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M6.5 5A1.5 1.5 0 0 0 5 6.5v3A1.5 1.5 0 0 0 6.5 11h3A1.5 1.5 0 0 0 11 9.5v-3A1.5 1.5 0 0 0 9.5 5z" />
          </svg>
        </button>
      </div>
    </div>
  );
}

