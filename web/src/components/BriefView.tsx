"use client";

import { motion } from "framer-motion";
import { MorningBrief, BriefSection } from "@/types";

interface BriefViewProps {
  brief: MorningBrief;
}

const CATEGORY_STYLES: Record<string, { color: string; glow: string }> = {
  "Big Releases": { color: "var(--amber)", glow: "var(--amber-glow)" },
  "Drama & Hot Takes": { color: "var(--red)", glow: "var(--red-glow)" },
  "Cool Projects": { color: "var(--cyan)", glow: "var(--cyan-glow)" },
  "Industry Moves": { color: "var(--indigo)", glow: "var(--indigo-glow)" },
  Vibecoding: { color: "var(--green)", glow: "var(--green-glow)" },
  "Sleeper Hits": { color: "var(--amber-dim)", glow: "var(--amber-glow)" },
};

function getCategoryStyle(category: string) {
  return (
    CATEGORY_STYLES[category] || {
      color: "var(--amber)",
      glow: "var(--amber-glow)",
    }
  );
}

export function BriefView({ brief }: BriefViewProps) {
  const dateStr = new Date(brief.created_at).toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="px-8 py-8">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
        className="mb-10"
      >
        <p
          className="mb-1 text-[10px] font-semibold uppercase"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--amber-dim)",
            letterSpacing: "0.15em",
          }}
        >
          {dateStr}
        </p>
        <h2
          className="text-4xl font-medium tracking-tight"
          style={{
            fontFamily: "var(--font-serif)",
            color: "var(--text-primary)",
            lineHeight: 1.15,
          }}
        >
          Morning Brief
        </h2>
        <div
          className="mt-4 h-px w-16"
          style={{
            background:
              "linear-gradient(90deg, var(--amber-dim), transparent)",
          }}
        />
      </motion.div>

      <div className="space-y-5">
        {brief.sections.map((section, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: 0.5,
              delay: 0.15 + i * 0.1,
              ease: [0.23, 1, 0.32, 1],
            }}
          >
            <SectionCard section={section} index={i} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function SectionCard({
  section,
  index,
}: {
  section: BriefSection;
  index: number;
}) {
  const style = getCategoryStyle(section.category);

  return (
    <div
      className="card-glow rounded-2xl p-6 transition-colors duration-300 hover:brightness-[1.02]"
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
      }}
    >
      {/* Category tag */}
      <div className="mb-3 flex items-center gap-2.5">
        <span
          className="inline-block h-1.5 w-1.5 rounded-full"
          style={{
            background: style.color,
            boxShadow: `0 0 6px ${style.glow}`,
          }}
        />
        <span
          className="text-[10px] font-semibold uppercase"
          style={{
            fontFamily: "var(--font-mono)",
            color: style.color,
            letterSpacing: "0.1em",
          }}
        >
          {section.category}
        </span>
        <div className="flex-1" />
        <span
          className="text-[9px]"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text-muted)",
          }}
        >
          #{index + 1}
        </span>
      </div>

      {/* Headline */}
      <h3
        className="mb-3 text-[17px] font-semibold leading-snug"
        style={{
          color: "var(--text-primary)",
          fontFamily: "var(--font-sans)",
        }}
      >
        {section.headline}
      </h3>

      {/* Context */}
      <p
        className="mb-5 text-[13px] leading-[1.7]"
        style={{
          color: "var(--text-secondary)",
          fontFamily: "var(--font-sans)",
        }}
      >
        {section.context}
      </p>

      {/* Tweet Ideas */}
      {section.tweet_ideas.length > 0 && (
        <div className="mb-4">
          <div className="mb-2.5 flex items-center gap-2">
            <div
              className="h-px flex-1"
              style={{ background: "var(--border)" }}
            />
            <span
              className="text-[9px] font-medium uppercase"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--text-muted)",
                letterSpacing: "0.12em",
              }}
            >
              tweet angles
            </span>
            <div
              className="h-px flex-1"
              style={{ background: "var(--border)" }}
            />
          </div>
          <div className="space-y-1.5">
            {section.tweet_ideas.map((idea, j) => (
              <div
                key={j}
                className="group/idea flex items-start gap-2.5 rounded-xl px-3.5 py-2.5 text-[13px] transition-all duration-200 cursor-pointer"
                style={{
                  background: "var(--bg-elevated)",
                  color: "var(--text-secondary)",
                  fontFamily: "var(--font-sans)",
                  border: "1px solid transparent",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "var(--border-active)";
                  e.currentTarget.style.background = "var(--bg-card-hover)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "transparent";
                  e.currentTarget.style.background = "var(--bg-elevated)";
                }}
              >
                <span
                  className="mt-px select-none text-[11px] transition-colors"
                  style={{ color: "var(--text-muted)" }}
                >
                  &rsaquo;
                </span>
                <span className="leading-relaxed">{idea}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sources */}
      {section.sources.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
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
                className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-[10px] transition-all duration-200 hover:brightness-150"
                style={{
                  background: "var(--bg-surface)",
                  color: "var(--text-muted)",
                  fontFamily: "var(--font-mono)",
                  border: "1px solid var(--border)",
                }}
              >
                <svg
                  width="8"
                  height="8"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
                {label}
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
}
