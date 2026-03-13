"use client";

import { useState, useRef, useCallback } from "react";
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

  const handleSubmit = useCallback(
    async (message: string) => {
      if (
        phase === "collecting" ||
        phase === "searching" ||
        phase === "building"
      )
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
    },
    [phase]
  );

  const handleReset = useCallback(() => {
    abortRef.current?.abort();
    setPhase("idle");
    setTools([]);
    setBrief(null);
    setActiveToolCount(0);
  }, []);

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      {/* Ambient glows */}
      <div
        className={`ambient-glow ${phase !== "idle" ? "active" : ""}`}
        style={{ top: "-250px", right: "-250px" }}
      />
      <div
        className={`ambient-glow-secondary ${phase === "building" || phase === "done" ? "active" : ""}`}
        style={{ bottom: "-200px", left: "-200px" }}
      />

      <div className="relative z-10 flex h-screen flex-col">
        <Header phase={phase} activeToolCount={activeToolCount} />

        <div className="flex flex-1 overflow-hidden">
          {/* Left panel — Tool Activity Feed */}
          <motion.div
            className="flex flex-col"
            style={{
              borderRight:
                phase === "done" && brief
                  ? "1px solid var(--border)"
                  : "none",
            }}
            initial={{ width: "100%" }}
            animate={{
              width: phase === "done" && brief ? "400px" : "100%",
            }}
            transition={{ duration: 0.7, ease: [0.23, 1, 0.32, 1] }}
          >
            {phase === "idle" ? (
              <IdleScreen onSubmit={handleSubmit} />
            ) : (
              <>
                <div className="flex-1 overflow-y-auto px-6 py-5">
                  <ToolFeed tools={tools} />
                </div>
                {phase !== "done" && (
                  <motion.div
                    className="px-6 py-4"
                    style={{
                      borderTop: "1px solid var(--border)",
                      background: "var(--bg-surface)",
                    }}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <PhaseIndicator phase={phase} />
                  </motion.div>
                )}
              </>
            )}

            {phase === "done" && (
              <motion.div
                className="px-4 py-3"
                style={{
                  borderTop: "1px solid var(--border)",
                  background: "var(--bg-surface)",
                }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <button
                  onClick={handleReset}
                  className="w-full rounded-xl px-4 py-2.5 text-[13px] font-medium transition-all duration-200"
                  style={{
                    background: "var(--bg-elevated)",
                    color: "var(--text-secondary)",
                    border: "1px solid var(--border)",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = "var(--border-hover)";
                    e.currentTarget.style.color = "var(--text-primary)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = "var(--border)";
                    e.currentTarget.style.color = "var(--text-secondary)";
                  }}
                >
                  New Brief
                </button>
              </motion.div>
            )}
          </motion.div>

          {/* Right panel — Brief */}
          <AnimatePresence>
            {phase === "done" && brief && (
              <motion.div
                className="flex-1 overflow-y-auto"
                initial={{ opacity: 0, x: 60 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 60 }}
                transition={{
                  duration: 0.6,
                  ease: [0.23, 1, 0.32, 1],
                  delay: 0.1,
                }}
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
      {/* Title block */}
      <motion.div
        className="mb-14 text-center"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: [0.23, 1, 0.32, 1] }}
      >
        <motion.div
          className="mx-auto mb-6 h-px w-12"
          style={{
            background:
              "linear-gradient(90deg, transparent, var(--amber-dim), transparent)",
          }}
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 48, opacity: 1 }}
          transition={{ duration: 1.2, delay: 0.3 }}
        />
        <h1
          className="text-gradient-amber mb-3 text-6xl font-medium tracking-tight"
          style={{ fontFamily: "var(--font-serif)" }}
        >
          nightshift
        </h1>
        <p
          className="text-[15px]"
          style={{
            color: "var(--text-muted)",
            fontFamily: "var(--font-sans)",
            letterSpacing: "0.01em",
          }}
        >
          your overnight AI intelligence brief
        </p>
      </motion.div>

      {/* Input */}
      <motion.div
        className="w-full max-w-lg"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 0.8,
          delay: 0.2,
          ease: [0.23, 1, 0.32, 1],
        }}
      >
        <ChatInput onSubmit={onSubmit} />
      </motion.div>

      {/* Suggestions */}
      <motion.div
        className="mt-8 flex flex-wrap justify-center gap-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.8 }}
      >
        {[
          "What happened in AI overnight?",
          "Trending in vibecoding",
          "AI drama & hot takes",
        ].map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSubmit(suggestion)}
            className="rounded-full px-4 py-2 text-[12px] transition-all duration-200 hover:scale-[1.03]"
            style={{
              background: "var(--bg-elevated)",
              color: "var(--text-muted)",
              border: "1px solid var(--border)",
              fontFamily: "var(--font-mono)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "var(--border-active)";
              e.currentTarget.style.color = "var(--text-secondary)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "var(--border)";
              e.currentTarget.style.color = "var(--text-muted)";
            }}
          >
            {suggestion}
          </button>
        ))}
      </motion.div>

      {/* Subtle bottom credits */}
      <motion.p
        className="absolute bottom-6 text-[10px]"
        style={{
          fontFamily: "var(--font-mono)",
          color: "var(--text-muted)",
          opacity: 0.5,
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.5 }}
        transition={{ delay: 1, duration: 1 }}
      >
        powered by claude + composio
      </motion.p>
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
      <div className="relative h-1.5 w-1.5">
        <span
          className="absolute inset-0 rounded-full"
          style={{ background: "var(--amber)" }}
        />
        <motion.span
          className="absolute inset-0 rounded-full"
          style={{ background: "var(--amber)" }}
          animate={{ scale: [1, 2.5], opacity: [0.6, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
        />
      </div>
      <span
        className="cursor-blink text-[12px]"
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
