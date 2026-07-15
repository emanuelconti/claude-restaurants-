import type { ToolDefinition } from "./types";

/**
 * AI tools commonly adopted by Spanish SMEs (clinics, salons, pharmacies,
 * local services). Display copy lives in messages/*.json under
 * scanner.tools.items.<id>; this file only encodes the facts the rules
 * engine needs to classify each tool.
 */
export const TOOL_CATALOG: ToolDefinition[] = [
  {
    id: "whatsapp-ai",
    category: "conversational",
    locked: { customerFacing: true },
    ask: ["automatedDecision", "emotionAnalysis"],
  },
  {
    id: "voice-receptionist",
    category: "voice",
    locked: { customerFacing: true },
    ask: ["automatedDecision", "emotionAnalysis"],
  },
  {
    id: "appointment-scheduler",
    category: "scheduling",
    locked: { customerFacing: true },
    ask: ["automatedDecision"],
  },
  {
    id: "chatgpt-assistant",
    category: "general-assistant",
    locked: {},
    ask: ["employeeUse", "customerFacing"],
  },
  {
    id: "copilot-assistant",
    category: "productivity",
    locked: {},
    ask: ["employeeUse", "customerFacing"],
  },
  {
    id: "crm-ai-scoring",
    category: "crm",
    locked: {},
    ask: ["automatedDecision", "employeeUse"],
  },
  {
    id: "content-generation-ai",
    category: "content",
    locked: { customerFacing: true },
    ask: [],
  },
  {
    id: "sentiment-emotion-ai",
    category: "analytics",
    locked: { emotionAnalysis: true },
    ask: ["employeeUse", "customerFacing"],
  },
  {
    id: "recruitment-ai",
    category: "hr",
    locked: { employeeUse: true, automatedDecision: true },
    ask: [],
  },
  {
    id: "biometric-attendance-ai",
    category: "biometric",
    locked: { employeeUse: true },
    ask: [],
  },
];

export function getToolDefinition(id: string): ToolDefinition | undefined {
  return TOOL_CATALOG.find((tool) => tool.id === id);
}
