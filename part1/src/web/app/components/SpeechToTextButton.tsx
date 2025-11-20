"use client";
import { useState, useEffect, useRef } from "react";

// Type definitions for Web Speech API
interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult: ((this: SpeechRecognition, ev: any) => any) | null;
  onerror: ((this: SpeechRecognition, ev: any) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition;
}

interface SpeechToTextButtonProps {
  onTranscript: (text: string) => void;
  darkMode: boolean;
  disabled?: boolean;
}

export default function SpeechToTextButton({ onTranscript, darkMode, disabled = false }: SpeechToTextButtonProps) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    // Check for browser support
    const SpeechRecognitionClass = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognitionClass) {
      console.warn("Speech recognition not supported in this browser");
      return;
    }

    // Initialize speech recognition
    const recognition = new SpeechRecognitionClass() as SpeechRecognition;
    recognition.continuous = false; // Stop after one utterance
    recognition.interimResults = false; // Only return final results
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript.trim());
      setIsListening(false);
    };

    recognition.onerror = (event: any) => {
      setIsListening(false);
      
      const errorType = event.error;
      
      if (errorType === "not-allowed") {
        // Microphone permission denied
        alert("Microphone access denied. Please enable microphone permissions in your browser settings.");
      } else if (errorType === "network") {
        alert("Speech recognition service is temporarily unavailable. Likely due to the browser blocking access to a https service from a non-https page.");
      } else if (errorType === "audio-capture") {
        // Audio capture error - microphone not available
        alert("Unable to access microphone. Please check your microphone settings.");
      } else if (errorType === "service-not-allowed") {
        // Service not allowed
        alert("Speech recognition service is not available. Please try again later.");
      }
      // Other errors are silently handled - user can try again
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    // Cleanup
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [onTranscript]);

  const handleToggleListening = () => {
    if (!recognitionRef.current) {
      console.warn("Speech recognition not available");
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        // Ignore errors when stopping - recognition might have already ended
      }
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
      } catch (error: any) {
        // Handle common start errors
        if (error?.name === "InvalidStateError" || error?.message?.includes("already started")) {
          // Recognition is already running, just update state
          setIsListening(true);
        } else {
          console.warn("Failed to start speech recognition:", error?.message || error);
          setIsListening(false);
        }
      }
    }
  };

  // Check if speech recognition is supported
  const SpeechRecognitionConstructor = (typeof window !== "undefined") 
    ? ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition)
    : null;

  if (!SpeechRecognitionConstructor || disabled) {
    return null;
  }

  return (
    <button
      type="button"
      onClick={handleToggleListening}
      disabled={disabled}
      className={`icon-button absolute right-14 top-1/2 -translate-y-1/2 ${
        disabled
          ? "disabled"
          : darkMode
          ? "dark"
          : "light"
      } ${isListening ? "listening" : ""}`}
      title={isListening ? "Stop recording" : "Start voice input"}
      aria-label={isListening ? "Stop recording" : "Start voice input"}
    >
      {isListening ? (
        // Microphone icon with pulse animation (recording) - red color
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="currentColor"
          viewBox="0 0 16 16"
          className="animate-pulse"
          style={{ color: '#ef4444' }}
        >
          <path d="M8 1a3 3 0 0 0-3 3v4a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3"/>
          <path d="M5 9.5a.5.5 0 0 0-1 0V11a4 4 0 0 0 8 0V9.5a.5.5 0 0 0-1 0V11a3 3 0 0 1-6 0V9.5z"/>
        </svg>
      ) : (
        // Microphone icon (idle)
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="currentColor"
          viewBox="0 0 16 16"
        >
          <path d="M8 1a3 3 0 0 0-3 3v4a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3"/>
          <path d="M5 9.5a.5.5 0 0 0-1 0V11a4 4 0 0 0 8 0V9.5a.5.5 0 0 0-1 0V11a3 3 0 0 1-6 0V9.5z"/>
        </svg>
      )}
    </button>
  );
}

