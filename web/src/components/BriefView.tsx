"use client";

import { motion } from "framer-motion";
import { MorningBrief, BriefSection } from "@/types";

interface BriefViewProps {
  brief: MorningBrief;
}

const CATEGORY_COLORS: Record<string, string> = {
  "Big Releases": "var(--amber)",
  "Drama & Hot Takes": "var(--red)",
  "Cool Projects": "var(--cyan)",
  "Industry Moves": "var(--indigo)",
  Vibecoding: "var(--green)",
  "Sleeper Hits": "var(--amber-dim)",
};

function getCategoryColor(category: string): string {
  return CATEGORY_COLORS[category] || "var(--amber)";
}

export function BriefView({ brief }: BriefViewProps) {
  return (
    <div className="px-8 py-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h2
          className="text-3xl font-light tracking-tight"
          style={{
            fontFamily: "var(--font-serif)",
            color: "var(--text-primary)",
          }}
        >
          Morning Brief
        </h2>
        <p
          className="mt-1 text-sm"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text-muted)",
          }}
        >
          {new Date(brief.created_at).toLocaleDateString("en-US", {
            weekday: "long",
            month: "long",
            day: "numeric",
          })}
        </p>
      </motion.div>

      <div className="space-y-6">
        {brief.sections.map((section, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: 0.5,
              delay: 0.1 + i * 0.08,
              ease: [0.23, 1, 0.32, 1],
            }}
          >
            <SectionCard section={section} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function SectionCard({ section }: { section: BriefSection }) {
  const accentColor = getCategoryColor(section.category);

  return (
    <div
      className="rounded-xl p-5 transition-colors"
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
      }}
    >
      {/* Category tag */}
      <div className="mb-3 flex items-center gap-2">
        <span
          className="inline-block h-1.5 w-1.5 rounded-full"
          style={{ background: accentColor }}
        />
        <span
          className="text-xs font-semibold uppercase tracking-wider"
          style={{
            fontFamily: "var(--font-mono)",
            color: accentColor,
          }}
        >
          {section.category}
        </span>
      </div>

      {/* Headline */}
      <h3
        className="mb-2 text-lg font-medium leading-snug"
        style={{
          color: "var(--text-primary)",
          fontFamily: "var(--font-sans)",
        }}
      >
        {section.headline}
      </h3>

      {/* Context */}
      <p
        className="mb-4 text-sm leading-relaxed"
        style={{
          color: "var(--text-secondary)",
          fontFamily: "var(--font-sans)",
        }}
      >
        {section.context}
      </p>

      {/* Tweet Ideas */}
      {section.tweet_ideas.length > 0 && (
        <div className="mb-3">
          <span
            className="mb-2 block text-xs font-medium uppercase tracking-wider"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--text-muted)",
            }}
          >
            Tweet angles
          </span>
          <div className="space-y-2">
            {section.tweet_ideas.map((idea, j) => (
              <div
                key={j}
                className="flex items-start gap-2 rounded-lg px-3 py-2 text-sm transition-colors hover:brightness-110 cursor-pointer"
                style={{
                  background: "var(--bg-elevated)",
                  color: "var(--text-secondary)",
                  fontFamily: "var(--font-sans)",
                }}
              >
                <span style={{ color: "var(--text-muted)" }} className="mt-0.5 select-none">
                  &rsaquo;
                </span>
                <span>{idea}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sources */}
      {section.sources.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {section.sources.map((src, k) => {
            let label = "link";
            try {
              const url = new URL(src);
              label = url.hostname.replace("www.", "").split(".")[0];
            } catch {
              /* noop */
            }
            return (
              <a
                key={k}
                href={src}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-md px-2 py-1 text-xs transition-colors hover:brightness-125"
                style={{
                  background: "var(--bg-surface)",
                  color: "var(--text-muted)",
                  fontFamily: "var(--font-mono)",
                  border: "1px solid var(--border)",
                }}
              >
                {label}
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
}
