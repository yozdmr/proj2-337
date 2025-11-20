"use client";

import { useState, useEffect, useRef } from "react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";



interface SpeechToTextButtonProps {
  disabled: boolean;
  darkMode: boolean;
  onTranscript?: (transcript: string) => void;
}


export default function SpeechToTextButton({ disabled, darkMode, onTranscript }: SpeechToTextButtonProps) {
  const [isMounted, setIsMounted] = useState(false);
  const [previousListening, setPreviousListening] = useState(false);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const transcriptRef = useRef<string>("");
  
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition();

  // Keep transcript ref in sync
  useEffect(() => {
    transcriptRef.current = transcript;
  }, [transcript]);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Auto-submit after 1.5 seconds of silence
  useEffect(() => {
    // Clear any existing timeout
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }

    // Only set timeout if we're currently listening
    if (listening) {
      silenceTimeoutRef.current = setTimeout(() => {
        // Use ref to get latest transcript value
        const currentTranscript = transcriptRef.current;
        if (listening) {
          // Stop listening first
          SpeechRecognition.stopListening();
          
          // If transcript is not empty, submit it
          if (currentTranscript.trim() && onTranscript) {
            onTranscript(currentTranscript);
            resetTranscript();
          } else {
            // If transcript is empty, just reset
            resetTranscript();
          }
        }
      }, 1500); // 1.5 seconds
    }

    // Cleanup timeout on unmount or when listening stops
    return () => {
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
        silenceTimeoutRef.current = null;
      }
    };
  }, [transcript, listening, onTranscript, resetTranscript]);

  // Handle transcript when listening stops
  useEffect(() => {
    if (previousListening && !listening) {
      if (transcript.trim() && onTranscript) {
        // Listening just stopped, send the transcript
        onTranscript(transcript);
        resetTranscript();
      } else {
        // Empty transcript, just reset
        resetTranscript();
      }
    }
    setPreviousListening(listening);
  }, [listening, transcript, previousListening, onTranscript, resetTranscript]);

  const handleToggleListening = () => {
    if (listening) {
      // Stop listening - transcript will be sent via useEffect
      SpeechRecognition.stopListening();
    } else {
      // Start listening
      resetTranscript();
      SpeechRecognition.startListening({ continuous: true });
    }
  };

  // Ensure consistent render during SSR and initial client render
  if (!isMounted) {
    return (
      <div className="flex justify-center items-center"></div>
    );
  }

  if (!browserSupportsSpeechRecognition) {
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
      } ${listening ? "listening" : ""}`}
      title={listening ? "Stop recording" : "Start voice input"}
      aria-label={listening ? "Stop recording" : "Start voice input"}
    >
      {listening ? (
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
