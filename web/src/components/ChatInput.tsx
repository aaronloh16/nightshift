"use client";

import { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSubmit: (message: string) => void;
}

export function ChatInput({ onSubmit }: ChatInputProps) {
  const [value, setValue] = useState("");
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
    <form onSubmit={handleSubmit} className="relative">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="what happened overnight?"
        className="w-full rounded-xl py-4 pl-5 pr-14 text-base outline-none transition-all focus:ring-1 placeholder:text-[var(--text-muted)]"
        style={{
          background: "var(--bg-elevated)",
          color: "var(--text-primary)",
          border: "1px solid var(--border)",
          fontFamily: "var(--font-sans)",
        }}
      />
      <button
        type="submit"
        disabled={!value.trim()}
        className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 transition-all disabled:opacity-30"
        style={{ color: "var(--amber)" }}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
      </button>
    </form>
  );
}
