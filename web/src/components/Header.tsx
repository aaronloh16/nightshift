"use client";

import { motion, AnimatePresence } from "framer-motion";
import { PipelinePhase } from "@/types";

interface HeaderProps {
  phase: PipelinePhase;
  activeToolCount: number;
}

export function Header({ phase, activeToolCount }: HeaderProps) {
  const isWorking =
    phase === "collecting" || phase === "searching" || phase === "building";

  return (
    <header
      className="flex items-center justify-between px-6 py-3"
      style={{
        borderBottom: "1px solid var(--border)",
        background: "rgba(6, 6, 11, 0.8)",
        backdropFilter: "blur(12px)",
      }}
    >
      <div className="flex items-center gap-3">
        <div className="relative">
          <div
            className="h-2 w-2 rounded-full transition-all duration-700"
            style={{
              background: isWorking
                ? "var(--amber)"
                : phase === "done"
                  ? "var(--green)"
                  : "var(--text-muted)",
              boxShadow: isWorking
                ? "0 0 12px var(--amber-glow-strong), 0 0 4px var(--amber)"
                : phase === "done"
                  ? "0 0 8px var(--green-glow)"
                  : "none",
            }}
          />
          {isWorking && (
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{ background: "var(--amber)" }}
              animate={{ scale: [1, 2.5], opacity: [0.6, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
            />
          )}
        </div>
        <span
          className="text-[11px] font-semibold uppercase"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text-secondary)",
            letterSpacing: "0.15em",
          }}
        >
          nightshift
        </span>
      </div>

      <AnimatePresence mode="wait">
        {isWorking && (
          <motion.div
            className="flex items-center gap-2.5"
            initial={{ opacity: 0, x: 8 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 8 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex gap-0.5">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="h-1 w-1 rounded-full"
                  style={{ background: "var(--amber-dim)" }}
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{
                    duration: 1.2,
                    repeat: Infinity,
                    delay: i * 0.15,
                  }}
                />
              ))}
            </div>
            <span
              className="text-[10px] tabular-nums"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--text-muted)",
              }}
            >
              {activeToolCount} active
            </span>
          </motion.div>
        )}
        {phase === "done" && (
          <motion.div
            initial={{ opacity: 0, x: 8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <span
              className="text-[10px]"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--green)",
              }}
            >
              brief ready
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
