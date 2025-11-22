"use client";

import { useEffect, useRef, useState } from "react";

interface WaveformVisualizerProps {
  listening: boolean;
  darkMode: boolean;
}

export default function WaveformVisualizer({ listening, darkMode }: WaveformVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationFrameRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  // Resize canvas to match container
  useEffect(() => {
    if (!canvasRef.current || !containerRef.current) return;
    
    const resizeCanvas = () => {
      const canvas = canvasRef.current;
      const container = containerRef.current;
      if (!canvas || !container) return;
      
      const rect = container.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = 40;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    return () => window.removeEventListener('resize', resizeCanvas);
  }, [listening]);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted || !listening) {
      // Clean up when not listening
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
        mediaStreamRef.current = null;
      }
      if (audioContextRef.current && audioContextRef.current.state !== "closed") {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
      analyserRef.current = null;
      return;
    }

    // Initialize audio context and start visualization
    const initAudio = async () => {
      try {
        // Get microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaStreamRef.current = stream;

        // Create audio context
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        audioContextRef.current = audioContext;

        // Create analyser node
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 512; // Larger == more bars
        analyser.smoothingTimeConstant = 0.8; // Keep higher to avoid minor noise showing up
        analyserRef.current = analyser;

        // Connect microphone to analyser
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);

        // Start visualization loop
        visualize();
      } catch (error) {
        console.error("Error accessing microphone:", error);
      }
    };

    initAudio();

    // Cleanup function
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
        mediaStreamRef.current = null;
      }
      if (audioContextRef.current && audioContextRef.current.state !== "closed") {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
      analyserRef.current = null;
    };
  }, [listening, isMounted]);

  const visualize = () => {
    if (!canvasRef.current || !analyserRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (!listening || !analyserRef.current) {
        return;
      }

      animationFrameRef.current = requestAnimationFrame(draw);

      // Get frequency data (volume/amplitude for each frequency bin)
      analyser.getByteFrequencyData(dataArray);

      // Clear canvas with input field background color
      ctx.fillStyle = darkMode ? "#27272a" : "#f4f4f5"; // zinc-800 and zinc-100
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Number of bars to display (use a subset of the frequency data for cleaner visualization)
      const barCount = Math.min(100, bufferLength);
      const barWidth = canvas.width / barCount;
      const centerY = canvas.height / 2;
      
      const noiseThreshold = 30; // ranges from 0-255
      const minBarHeight = 2;  // prevent tiny bars from showing

      // Draw vertical bars
      for (let i = 0; i < barCount; i++) {
        // Sample frequency data (use more data points for smoother visualization)
        const dataIndex = Math.floor((i / barCount) * bufferLength);
        let barValue = dataArray[dataIndex];
        
        if (barValue < noiseThreshold) {
          barValue = 0;
        } else {
          barValue = ((barValue - noiseThreshold) / (255 - noiseThreshold)) * 255;
        }
        
        let barHeight = (barValue / 255) * canvas.height;
        
        // prevent tiny bars from showing
        if (barHeight > 0 && barHeight < minBarHeight) {
          barHeight = 0;
        }
        
        // Calculate bar position
        const x = i * barWidth;
        
        if (barHeight > 0) {
          // Draw bar from center, extending up and down
          ctx.fillStyle = darkMode ? "#e36a24" : "#de5607"; // Dark orange color
          ctx.fillRect(x, centerY - barHeight / 2, barWidth - 1, barHeight);
        }
      }
    };

    draw();
  };

  // Check if Web Audio API is supported
  if (!isMounted || !listening) {
    return null;
  }

  if (typeof window === "undefined" || !window.AudioContext && !(window as any).webkitAudioContext) {
    return null;
  }

  return (
    <div 
      ref={containerRef}
      className={`absolute left-0 ml-12 top-1/2 -translate-y-1/2 flex items-center justify-start pointer-events-none z-10 ${darkMode ? "bg-zinc-800" : "bg-zinc-100"}`}
      style={{ 
        height: '40px',
        width: '70%',
        minWidth: '200px',
        maxWidth: '550px'
      }}
    >
      <canvas
        ref={canvasRef}
        width={400}
        height={40}
        className="w-full"
      />
    </div>
  );
}

