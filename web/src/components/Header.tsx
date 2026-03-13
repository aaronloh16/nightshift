"use client";

import { motion, AnimatePresence } from "framer-motion";
import { PipelinePhase } from "@/types";

interface HeaderProps {
  phase: PipelinePhase;
  activeToolCount: number;
}

export function Header({ phase, activeToolCount }: HeaderProps) {
  const isWorking = phase === "collecting" || phase === "searching" || phase === "building";

  return (
    <header
      className="flex items-center justify-between px-6 py-4 border-b"
      style={{ borderColor: "var(--border)", background: "var(--bg-surface)" }}
    >
      <div className="flex items-center gap-3">
        <div
          className="h-2 w-2 rounded-full transition-colors duration-500"
          style={{
            background: isWorking
              ? "var(--amber)"
              : phase === "done"
                ? "var(--green)"
                : "var(--text-muted)",
            boxShadow: isWorking
              ? "0 0 8px var(--amber-glow-strong)"
              : "none",
          }}
        />
        <span
          className="text-sm font-semibold tracking-wide uppercase"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text-secondary)",
            letterSpacing: "0.1em",
          }}
        >
          nightshift
        </span>
      </div>

      <AnimatePresence>
        {isWorking && (
          <motion.div
            className="flex items-center gap-2"
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
          >
            <span
              className="text-xs tabular-nums"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--amber-dim)",
              }}
            >
              {activeToolCount} active
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
