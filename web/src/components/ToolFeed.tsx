"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ToolEvent } from "@/types";
import { useRef, useEffect } from "react";

interface ToolFeedProps {
  tools: ToolEvent[];
}

export function ToolFeed({ tools }: ToolFeedProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [tools.length]);

  return (
    <div className="relative space-y-0.5">
      <div className="scan-line" />
      <AnimatePresence initial={false}>
        {tools.map((tool) => (
          <ToolRow key={tool.id} tool={tool} />
        ))}
      </AnimatePresence>
      <div ref={bottomRef} />
    </div>
  );
}

function ToolRow({ tool }: { tool: ToolEvent }) {
  const isActive = tool.status === "active";
  const isDone = tool.status === "done";
  const isError = tool.status === "error";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8, filter: "blur(4px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
      className={`group rounded-xl px-4 py-3 ${isActive ? "tool-active" : ""}`}
      style={{
        background: isActive
          ? "var(--bg-elevated)"
          : "transparent",
        border: isActive
          ? "1px solid var(--border-active)"
          : "1px solid transparent",
      }}
    >
      <div className="flex items-start gap-3">
        {/* Icon with status ring */}
        <div className="relative mt-0.5 flex-shrink-0">
          <span className="text-base leading-none">{tool.icon}</span>
          {isActive && (
            <motion.div
              className="absolute -inset-1.5 rounded-full"
              style={{ border: "1px solid var(--amber-glow-strong)" }}
              animate={{ scale: [1, 1.3], opacity: [0.5, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
          )}
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span
              className="text-[10px] font-semibold uppercase"
              style={{
                fontFamily: "var(--font-mono)",
                letterSpacing: "0.08em",
                color: isActive
                  ? "var(--amber)"
                  : isDone
                    ? "var(--text-muted)"
                    : isError
                      ? "var(--red)"
                      : "var(--text-secondary)",
              }}
            >
              {tool.tool}
            </span>

            {isActive && (
              <motion.span
                className="inline-block h-1 w-1 rounded-full"
                style={{ background: "var(--amber)" }}
                animate={{ opacity: [1, 0.2, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            )}

            {isDone && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 400, damping: 15 }}
              >
                <svg
                  width="10"
                  height="10"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="var(--green)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </motion.div>
            )}

            {/* Timestamp */}
            <span
              className="ml-auto text-[9px] opacity-0 group-hover:opacity-100 transition-opacity"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--text-muted)",
              }}
            >
              {new Date(tool.timestamp).toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: false,
              })}
            </span>
          </div>

          <p
            className="mt-0.5 text-[13px] leading-relaxed"
            style={{
              color: isDone ? "var(--text-muted)" : "var(--text-primary)",
              fontFamily: "var(--font-sans)",
            }}
          >
            {tool.message}
          </p>

          {tool.detail && (
            <p
              className="mt-0.5 text-[11px] leading-relaxed"
              style={{
                color: "var(--text-muted)",
                fontFamily: "var(--font-mono)",
              }}
            >
              {tool.detail}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
