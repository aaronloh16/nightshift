export type ToolStatus = "idle" | "active" | "done" | "error";

export interface ToolEvent {
  id: string;
  tool: string;
  icon: string;
  status: ToolStatus;
  message: string;
  detail?: string;
  timestamp: number;
}

export interface BriefSection {
  category: string;
  headline: string;
  context: string;
  sources: string[];
  tweet_ideas: string[];
}

export interface MorningBrief {
  sections: BriefSection[];
  created_at: string;
  smart_summary?: string;
}

export type PipelinePhase =
  | "idle"
  | "collecting"
  | "searching"
  | "building"
  | "done";
