"use client";

// Shared speech synthesis utility to ensure only one speech plays at a time
export function stopAllSpeech() {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) {
    return;
  }
  window.speechSynthesis.cancel();
}

