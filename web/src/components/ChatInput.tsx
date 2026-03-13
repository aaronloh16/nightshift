"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";

interface ChatInputProps {
  onSubmit: (message: string) => void;
}

export function ChatInput({ onSubmit }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const msg = value.trim();
    if (!msg) return;
    onSubmit(msg);
    setValue("");
  };

  return (
    <form onSubmit={handleSubmit} className="relative group">
      {/* Glow ring on focus */}
      <motion.div
        className="absolute -inset-px rounded-2xl pointer-events-none"
        style={{
          background: "linear-gradient(135deg, var(--amber-glow) 0%, transparent 50%, var(--indigo-glow) 100%)",
        }}
        animate={{ opacity: focused ? 1 : 0 }}
        transition={{ duration: 0.3 }}
      />
      <div
        className="relative rounded-2xl transition-all"
        style={{
          background: "var(--bg-elevated)",
          border: `1px solid ${focused ? "var(--border-hover)" : "var(--border)"}`,
        }}
      >
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="what happened overnight?"
          className="w-full bg-transparent py-4 pl-5 pr-14 text-[15px] outline-none placeholder:text-[var(--text-muted)]"
          style={{
            color: "var(--text-primary)",
            fontFamily: "var(--font-sans)",
          }}
        />
        <button
          type="submit"
          disabled={!value.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 rounded-xl p-2.5 transition-all disabled:opacity-20"
          style={{
            color: "var(--amber)",
            background: value.trim() ? "var(--amber-subtle)" : "transparent",
          }}
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </form>
  );
}
