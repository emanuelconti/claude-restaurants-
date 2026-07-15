export const SECTORS = [
  "dental-clinic",
  "medical-clinic",
  "beauty-salon",
  "pharmacy",
  "legal-professional-services",
  "financial-insurance-services",
  "retail-hospitality",
  "other-local-services",
] as const;
export type Sector = (typeof SECTORS)[number];

export const EMPLOYEE_RANGES = ["solo", "small", "medium", "large"] as const;
export type EmployeeRange = (typeof EMPLOYEE_RANGES)[number];

export const HEALTH_SECTORS: Sector[] = ["dental-clinic", "medical-clinic"];

export const TOOL_CATEGORIES = [
  "conversational",
  "voice",
  "scheduling",
  "general-assistant",
  "productivity",
  "crm",
  "content",
  "analytics",
  "hr",
  "biometric",
] as const;
export type ToolCategory = (typeof TOOL_CATEGORIES)[number];

/** Context questions that can be asked about a selected tool. */
export const CONTEXT_FLAGS = [
  "employeeUse",
  "automatedDecision",
  "emotionAnalysis",
  "customerFacing",
] as const;
export type ContextFlag = (typeof CONTEXT_FLAGS)[number];

/**
 * "locked" flags are implied by the nature of the tool and are not asked
 * in the questionnaire. "ask" flags are surfaced as toggles for the user.
 * Any flag not listed defaults to `false`.
 */
export interface ToolDefinition {
  id: string;
  category: ToolCategory;
  locked: Partial<Record<ContextFlag, boolean>>;
  ask: ContextFlag[];
}

export type ToolAnswers = Partial<Record<ContextFlag, boolean>>;

export interface BusinessInfo {
  name: string;
  sector: Sector;
  employeeRange: EmployeeRange;
}

export const RISK_TIERS = ["unacceptable", "high", "limited", "minimal"] as const;
export type RiskTier = (typeof RISK_TIERS)[number];

export const RISK_TIER_ORDER: Record<RiskTier, number> = {
  unacceptable: 3,
  high: 2,
  limited: 1,
  minimal: 0,
};

export interface ToolClassification {
  toolId: string;
  tier: RiskTier;
  articles: string[];
  obligations: string[];
  warnings: string[];
}

export interface ScanResult {
  business: BusinessInfo;
  toolClassifications: ToolClassification[];
  overallTier: RiskTier;
  healthDataFlag: boolean;
  spainNotes: string[];
}
