import { NextRequest } from "next/server";

// Simulated pipeline events — in production this would call the Python backend
const TOOL_SEQUENCE = [
  {
    tool: "Gmail",
    icon: "📧",
    message: "Fetching newsletters from The Rundown AI...",
    detail: "Searching recent emails for AI newsletter content",
    delay: 800,
  },
  {
    tool: "Gmail",
    icon: "📧",
    message: "Found 3 newsletters from the last 12 hours",
    detail:
      "Google Gemini in Maps, Perplexity Computer, Yann LeCun's AMI Labs",
    delay: 1200,
  },
  {
    tool: "x_search",
    icon: "𝕏",
    message: "Searching X for discourse on newsletter topics...",
    detail: "Querying: Google Gemini Maps, Perplexity Computer, LeCun AMI Labs",
    delay: 1000,
  },
  {
    tool: "x_search",
    icon: "𝕏",
    message: "Found 147 relevant tweets across topics",
    detail:
      "@sundarpichai (41k likes), @mustafasuleyman (576 likes), @cb_doge (5.5k likes)",
    delay: 1500,
  },
  {
    tool: "x_search",
    icon: "𝕏",
    message: "Searching X for AI releases & announcements...",
    detail: "New models, tools, major updates in the last 12 hours",
    delay: 1000,
  },
  {
    tool: "x_search",
    icon: "𝕏",
    message: "Searching X for vibecoding & AI coding tools...",
    detail: "Cursor, Claude Code, Copilot, Windsurf discourse",
    delay: 900,
  },
  {
    tool: "Hacker News",
    icon: "🟧",
    message: "Fetching top stories + Algolia keyword search...",
    detail: 'Keywords: "AI agent", "vibecoding", "cursor", "claude"',
    delay: 1100,
  },
  {
    tool: "Hacker News",
    icon: "🟧",
    message: "Collected 10 stories (3 from Show HN)",
    detail: "Top: SQLite vector search (342pts), New Claude feature (287pts)",
    delay: 800,
  },
  {
    tool: "Reddit",
    icon: "🔴",
    message: "Scanning 11 subreddits for hot posts...",
    detail:
      "r/LocalLLaMA, r/ClaudeCode, r/VibeCoding, r/AI_Agents, r/programming",
    delay: 1200,
  },
  {
    tool: "GitHub",
    icon: "🐙",
    message: "Fetching trending repos in AI/ML...",
    detail: "Topics: artificial-intelligence, llm, machine-learning",
    delay: 900,
  },
  {
    tool: "RSS",
    icon: "📡",
    message: "Pulling latest from 4 feeds...",
    detail: "Simon Willison, Latent Space, Changelog, HN Best",
    delay: 700,
  },
  {
    tool: "RSS",
    icon: "📡",
    message: "Collected 15 articles",
    detail: "Newest: Simon Willison on prompt injection defense patterns",
    delay: 600,
  },
  {
    tool: "Claude",
    icon: "🧠",
    message: "Building morning brief from all sources...",
    detail: "Merging 47 items + X discourse into structured sections",
    delay: 2000,
  },
  {
    tool: "Claude",
    icon: "🧠",
    message: "Generating tweet ideas for top stories...",
    detail: "Matching angles to your voice: hot takes, signal boosts, builds",
    delay: 1800,
  },
];

const MOCK_BRIEF = {
  sections: [
    {
      category: "Big Releases",
      headline: "Google puts Gemini in Maps — biggest update in a decade",
      context:
        'Google launched "Ask Maps" for conversational trip planning and Immersive Navigation with Gemini-analyzed 3D views. Rolling out in US/India. @sundarpichai\'s thread hit 41k likes. This is Google embedding AI where billions already are — practical utility over demos.',
      sources: [
        "https://x.com/Google/status/2032079598683332742",
        "https://blog.google/products/maps/gemini-maps-2026/",
      ],
      tweet_ideas: [
        "google putting gemini in maps is exactly the kind of ai integration that actually matters. not another chatbot, just making something you already use way better",
        "hot take: gemini in maps is more impressive than any new model release this month. real-world utility > benchmarks",
        "try it out and post your honest first impressions — trip planning with gemini maps",
      ],
    },
    {
      category: "Drama & Hot Takes",
      headline:
        "xAI poaches Cursor engineers — Grok playing catch-up on coding",
      context:
        "xAI hired Cursor's Andrew Milich and Jason Ginsberg to report directly to Elon. Elon publicly admitted Grok is behind on coding. @cb_doge's clip went viral (5.5k likes). Ties to broader narrative of Cursor becoming the talent pipeline for frontier labs.",
      sources: ["https://x.com/cb_doge/status/2032188677909270622"],
      tweet_ideas: [
        "cursor is basically an ai engineering talent farm at this point. grok, openai, anthropic all recruiting from there",
        "elon admitting grok is behind on coding is refreshingly honest. the fix: hire cursor's best people. respect the move",
        "contrarian: this might actually be bad for cursor users. brain drain from the tool you depend on",
      ],
    },
    {
      category: "Cool Projects",
      headline: "Perplexity announces a physical AI computer",
      context:
        "A dedicated Mac Mini-style device that runs as your 24/7 local AI agent. Privacy-first, always-on, local processing. @WesRoth (33k followers) called it transformative. Bold bet that agents need their own hardware.",
      sources: ["https://x.com/WesRoth/status/2032128235266244695"],
      tweet_ideas: [
        "perplexity betting on dedicated hardware for agents is fascinating. why share compute with your browser when your agent needs to run 24/7?",
        "build & share: set up the perplexity computer and document what a dedicated agent machine actually enables",
      ],
    },
    {
      category: "Industry Moves",
      headline: "Yann LeCun raises $1B for anti-LLM startup AMI Labs",
      context:
        'LeCun\'s thesis: LLMs are a dead end, we need AI that learns from reality ("world models") not text. $1B says he\'s serious. Viral joke: LeCun/LeBrun co-founders = "Luigi and Waluigi tier" (136 retweets). Most contrarian bet in AI right now.',
      sources: [
        "https://www.therundown.ai/p/yann-lecuns-1b-bet",
        "https://x.com/ylecun/status/2031890123456789",
      ],
      tweet_ideas: [
        "lecun raising $1b to prove llms are a dead end is either the most visionary or most stubborn move in ai. no in between",
        "funny observation: the guy who invented the tech that powers half of modern ai says the other half (llms) is wrong. peak academia energy",
        "signal boost: regardless of whether lecun is right, the 'world models' approach is worth understanding. here's what it actually means...",
      ],
    },
    {
      category: "Vibecoding",
      headline: "Claude Code ships custom tool use in CLI sessions",
      context:
        "New feature lets you define custom tools that Claude Code can call during coding sessions. Community already building integrations with databases, APIs, deployment tools. r/ClaudeCode thread hit 500+ upvotes.",
      sources: ["https://reddit.com/r/ClaudeCode/comments/abc123"],
      tweet_ideas: [
        "claude code custom tools is exactly what vibecoding needed. build once, use everywhere. my first custom tool: auto-deploy to fly.io on test pass",
        "engage/reply: reply to the r/ClaudeCode thread with your setup — custom tools + what you're building with them",
      ],
    },
    {
      category: "Sleeper Hits",
      headline: "SQLite-vec hits 1.0 — vector search without the infra tax",
      context:
        "Full vector similarity search as a SQLite extension. No Pinecone, no Chroma, no separate vector DB. Just your existing SQLite. HN post hit 342 points. Perfect for local-first AI apps.",
      sources: ["https://news.ycombinator.com/item?id=39123456"],
      tweet_ideas: [
        "sqlite-vec 1.0 is the most underrated release this week. vector search without standing up another database? yes please",
        "build & share: build a local RAG app with sqlite-vec and post the repo. bet it's under 100 lines",
      ],
    },
  ],
  created_at: new Date().toISOString(),
};

export async function POST(req: NextRequest) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: Record<string, unknown>) => {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify(data)}\n\n`)
        );
      };

      // Send tool events with delays
      for (let i = 0; i < TOOL_SEQUENCE.length; i++) {
        const event = TOOL_SEQUENCE[i];
        await new Promise((r) => setTimeout(r, event.delay));
        send({
          type: "tool",
          id: `tool-${i}`,
          tool: event.tool,
          icon: event.icon,
          status: "active",
          message: event.message,
          detail: event.detail,
          timestamp: Date.now(),
        });

        // Mark previous same-tool events as done
        if (i > 0 && TOOL_SEQUENCE[i - 1].tool === event.tool) {
          send({
            type: "tool_update",
            id: `tool-${i - 1}`,
            status: "done",
          });
        }
      }

      // Mark last tool as done
      send({
        type: "tool_update",
        id: `tool-${TOOL_SEQUENCE.length - 1}`,
        status: "done",
      });

      await new Promise((r) => setTimeout(r, 500));

      // Send the brief
      send({
        type: "brief",
        brief: MOCK_BRIEF,
      });

      send({ type: "done" });
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
