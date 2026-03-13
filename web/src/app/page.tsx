"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ToolEvent, MorningBrief, PipelinePhase } from "@/types";
import { ToolFeed } from "@/components/ToolFeed";
import { BriefView } from "@/components/BriefView";
import { ChatInput } from "@/components/ChatInput";
import { Header } from "@/components/Header";

export default function Home() {
  const [phase, setPhase] = useState<PipelinePhase>("idle");
  const [tools, setTools] = useState<ToolEvent[]>([]);
  const [brief, setBrief] = useState<MorningBrief | null>(null);
  const [activeToolCount, setActiveToolCount] = useState(0);
  const abortRef = useRef<AbortController | null>(null);

  const handleSubmit = useCallback(async (message: string) => {
    if (phase === "collecting" || phase === "searching" || phase === "building")
      return;

    setPhase("collecting");
    setTools([]);
    setBrief(null);
    setActiveToolCount(0);

    abortRef.current = new AbortController();

    try {
      const res = await fetch("/api/brief", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
        signal: abortRef.current.signal,
      });

      const reader = res.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const data = JSON.parse(line.slice(6));

          if (data.type === "tool") {
            const toolEvent: ToolEvent = {
              id: data.id,
              tool: data.tool,
              icon: data.icon,
              status: data.status,
              message: data.message,
              detail: data.detail,
              timestamp: data.timestamp,
            };
            setTools((prev) => [...prev, toolEvent]);
            setActiveToolCount((c) => c + 1);

            // Update phase based on tool type
            if (data.tool === "Claude") {
              setPhase("building");
            } else if (
              data.tool === "x_search" ||
              data.tool === "Hacker News" ||
              data.tool === "Reddit" ||
              data.tool === "GitHub" ||
              data.tool === "RSS"
            ) {
              setPhase("searching");
            }
          } else if (data.type === "tool_update") {
            setTools((prev) =>
              prev.map((t) =>
                t.id === data.id ? { ...t, status: data.status } : t
              )
            );
            if (data.status === "done") {
              setActiveToolCount((c) => Math.max(0, c - 1));
            }
          } else if (data.type === "brief") {
            setBrief(data.brief);
            setPhase("done");
          }
        }
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      console.error("Stream error:", err);
      setPhase("idle");
    }
  }, [phase]);

  const handleReset = useCallback(() => {
    abortRef.current?.abort();
    setPhase("idle");
    setTools([]);
    setBrief(null);
    setActiveToolCount(0);
  }, []);

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      {/* Ambient glow */}
      <div
        className={`ambient-glow ${phase !== "idle" ? "active" : ""}`}
        style={{ top: "-200px", right: "-200px" }}
      />
      <div
        className={`ambient-glow ${phase === "building" || phase === "done" ? "active" : ""}`}
        style={{ bottom: "-300px", left: "-200px" }}
      />

      <div className="relative z-10 flex h-screen flex-col">
        <Header phase={phase} activeToolCount={activeToolCount} />

        <div className="flex flex-1 overflow-hidden">
          {/* Left panel — Tool Activity Feed */}
          <motion.div
            className="flex flex-col border-r"
            style={{ borderColor: "var(--border)" }}
            initial={{ width: "100%" }}
            animate={{
              width: phase === "done" && brief ? "380px" : "100%",
            }}
            transition={{ duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
          >
            {phase === "idle" ? (
              <IdleScreen onSubmit={handleSubmit} />
            ) : (
              <>
                <div className="flex-1 overflow-y-auto px-6 py-4">
                  <ToolFeed tools={tools} />
                </div>
                {phase !== "done" && (
                  <div className="px-6 py-4">
                    <PhaseIndicator phase={phase} />
                  </div>
                )}
              </>
            )}

            {phase === "done" && (
              <div className="border-t px-4 py-3" style={{ borderColor: "var(--border)" }}>
                <button
                  onClick={handleReset}
                  className="w-full rounded-lg px-4 py-2 text-sm font-medium transition-colors"
                  style={{
                    background: "var(--bg-elevated)",
                    color: "var(--text-secondary)",
                    border: "1px solid var(--border)",
                  }}
                >
                  New Brief
                </button>
              </div>
            )}
          </motion.div>

          {/* Right panel — Brief */}
          <AnimatePresence>
            {phase === "done" && brief && (
              <motion.div
                className="flex-1 overflow-y-auto"
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 40 }}
                transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
              >
                <BriefView brief={brief} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

function IdleScreen({ onSubmit }: { onSubmit: (msg: string) => void }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-8">
      <motion.div
        className="mb-12 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
      >
        <h1
          className="mb-3 text-5xl font-light tracking-tight"
          style={{ fontFamily: "var(--font-serif)", color: "var(--amber)" }}
        >
          nightshift
        </h1>
        <p
          className="text-lg"
          style={{ color: "var(--text-secondary)", fontFamily: "var(--font-sans)" }}
        >
          your overnight AI intelligence brief
        </p>
      </motion.div>

      <motion.div
        className="w-full max-w-xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 0.8,
          delay: 0.15,
          ease: [0.23, 1, 0.32, 1],
        }}
      >
        <ChatInput onSubmit={onSubmit} />
      </motion.div>

      <motion.div
        className="mt-8 flex flex-wrap justify-center gap-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        {[
          "What happened in AI overnight?",
          "Trending in vibecoding",
          "AI drama & hot takes",
        ].map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSubmit(suggestion)}
            className="rounded-full px-4 py-2 text-sm transition-all hover:scale-105"
            style={{
              background: "var(--bg-elevated)",
              color: "var(--text-secondary)",
              border: "1px solid var(--border)",
              fontFamily: "var(--font-mono)",
            }}
          >
            {suggestion}
          </button>
        ))}
      </motion.div>
    </div>
  );
}

function PhaseIndicator({ phase }: { phase: PipelinePhase }) {
  const labels: Record<string, string> = {
    collecting: "Fetching newsletters...",
    searching: "Searching sources...",
    building: "Building your brief...",
  };

  return (
    <div className="flex items-center gap-3">
      <div className="relative h-2 w-2">
        <span
          className="absolute inset-0 rounded-full"
          style={{ background: "var(--amber)" }}
        />
        <span
          className="absolute inset-0 animate-ping rounded-full"
          style={{ background: "var(--amber)", opacity: 0.6 }}
        />
      </div>
      <span
        className="cursor-blink text-sm"
        style={{
          color: "var(--text-secondary)",
          fontFamily: "var(--font-mono)",
        }}
      >
        {labels[phase] || "Working..."}
      </span>
    </div>
  );
}
