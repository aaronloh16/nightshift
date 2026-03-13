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
    <div className="relative space-y-1">
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

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.35, ease: [0.23, 1, 0.32, 1] }}
      className={`group rounded-lg px-4 py-3 transition-colors ${isActive ? "tool-active" : ""}`}
      style={{
        background: isActive ? "var(--bg-elevated)" : "transparent",
        border: isActive ? "1px solid var(--border-active)" : "1px solid transparent",
      }}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="mt-0.5 flex-shrink-0 text-lg leading-none">
          {tool.icon}
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span
              className="text-xs font-medium uppercase tracking-wider"
              style={{
                fontFamily: "var(--font-mono)",
                color: isActive ? "var(--amber)" : isDone ? "var(--text-muted)" : "var(--text-secondary)",
              }}
            >
              {tool.tool}
            </span>

            {isActive && (
              <motion.span
                className="inline-block h-1.5 w-1.5 rounded-full"
                style={{ background: "var(--amber)" }}
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ duration: 1.2, repeat: Infinity }}
              />
            )}

            {isDone && (
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="var(--green)"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            )}
          </div>

          <p
            className="mt-0.5 text-sm leading-relaxed"
            style={{
              color: isDone ? "var(--text-muted)" : "var(--text-primary)",
              fontFamily: "var(--font-sans)",
            }}
          >
            {tool.message}
          </p>

          {tool.detail && (
            <p
              className="mt-0.5 text-xs leading-relaxed"
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
