import { getToolDefinition } from "./catalog";
import {
  type BusinessInfo,
  type ContextFlag,
  CONTEXT_FLAGS,
  HEALTH_SECTORS,
  type RiskTier,
  RISK_TIER_ORDER,
  type ScanResult,
  type ToolAnswers,
  type ToolClassification,
} from "./types";

function resolveFlags(
  toolId: string,
  answers: ToolAnswers,
): Record<ContextFlag, boolean> {
  const def = getToolDefinition(toolId);
  const flags = Object.fromEntries(
    CONTEXT_FLAGS.map((flag) => [flag, false]),
  ) as Record<ContextFlag, boolean>;

  if (!def) return flags;

  for (const flag of CONTEXT_FLAGS) {
    if (def.locked[flag] !== undefined) {
      flags[flag] = def.locked[flag]!;
    } else if (def.ask.includes(flag)) {
      flags[flag] = answers[flag] ?? false;
    }
  }
  return flags;
}

/**
 * Deterministic classification against Regulation (EU) 2024/1689 (the EU AI
 * Act). This is preliminary, informational guidance — not legal advice.
 */
export function classifyTool(
  toolId: string,
  answers: ToolAnswers,
  business: BusinessInfo,
): ToolClassification {
  const def = getToolDefinition(toolId);
  const flags = resolveFlags(toolId, answers);
  const isBiometric = def?.category === "biometric";
  const isSyntheticContent = def?.category === "content";

  const articles = new Set<string>();
  const obligations = new Set<string>();
  const warnings = new Set<string>();

  // Cross-cutting obligation regardless of risk tier (Art. 4).
  articles.add("ART_4");
  obligations.add("AI_LITERACY");

  const finalize = (tier: RiskTier): ToolClassification => ({
    toolId,
    tier,
    articles: Array.from(articles),
    obligations: Array.from(obligations),
    warnings: Array.from(warnings),
  });

  // 1. Unacceptable risk — prohibited practices (Art. 5).
  if (flags.emotionAnalysis && flags.employeeUse) {
    articles.add("ART_5_1_F");
    obligations.add("PROHIBITED_STOP_USE");
    warnings.add("WARN_VERIFY_EXCEPTION");
    return finalize("unacceptable");
  }

  // 2. High risk (Annex III).
  let isHighRisk = false;

  if (flags.employeeUse && (def?.category === "hr" || flags.automatedDecision)) {
    isHighRisk = true;
    articles.add("ANNEX_III_4");
    obligations.add("HIGH_RISK_DEPLOYER_OBLIGATIONS");
    obligations.add("HIGH_RISK_HUMAN_OVERSIGHT");
    obligations.add("HIGH_RISK_LOGGING");
    warnings.add("WARN_HUMAN_REVIEW_RECOMMENDED");
  }

  if (isBiometric) {
    isHighRisk = true;
    articles.add("ANNEX_III_1");
    obligations.add("HIGH_RISK_DEPLOYER_OBLIGATIONS");
    obligations.add("HIGH_RISK_HUMAN_OVERSIGHT");
    warnings.add("WARN_BIOMETRIC_VERIFICATION_SCOPE");
  }

  if (
    flags.automatedDecision &&
    def?.category === "crm" &&
    business.sector === "financial-insurance-services"
  ) {
    isHighRisk = true;
    articles.add("ANNEX_III_5");
    obligations.add("HIGH_RISK_DEPLOYER_OBLIGATIONS");
    obligations.add("HIGH_RISK_FRIA");
    warnings.add("WARN_HUMAN_REVIEW_RECOMMENDED");
  }

  if (isHighRisk) {
    return finalize("high");
  }

  // 3. Limited risk — transparency obligations (Art. 50).
  let isLimited = false;

  if (flags.customerFacing) {
    isLimited = true;
    articles.add("ART_50_1");
    obligations.add("TRANSPARENCY_DISCLOSE_AI");
  }

  if (isSyntheticContent) {
    isLimited = true;
    articles.add("ART_50_4");
    obligations.add("TRANSPARENCY_LABEL_SYNTHETIC");
  }

  if (flags.emotionAnalysis) {
    isLimited = true;
    articles.add("ART_50_3");
    obligations.add("TRANSPARENCY_EMOTION_NOTICE");
  }

  if (flags.automatedDecision) {
    warnings.add("WARN_HUMAN_REVIEW_RECOMMENDED");
  }

  if (isLimited) {
    return finalize("limited");
  }

  // 4. Minimal risk.
  obligations.add("VOLUNTARY_CODE_CONDUCT");
  if (def?.category === "general-assistant" || def?.category === "productivity") {
    warnings.add("WARN_GPAI_PROVIDER_OBLIGATIONS");
  }
  return finalize("minimal");
}

export function buildScanResult(
  business: BusinessInfo,
  selections: Array<{ toolId: string; answers: ToolAnswers }>,
): ScanResult {
  const toolClassifications = selections.map(({ toolId, answers }) =>
    classifyTool(toolId, answers, business),
  );

  const overallTier = toolClassifications.reduce<RiskTier>(
    (highest, classification) =>
      RISK_TIER_ORDER[classification.tier] > RISK_TIER_ORDER[highest]
        ? classification.tier
        : highest,
    "minimal",
  );

  const healthDataFlag = HEALTH_SECTORS.includes(business.sector);
  const spainNotes = ["SPAIN_AESIA_INFO"];
  if (healthDataFlag) spainNotes.push("SPAIN_AEPD_HEALTH");

  return {
    business,
    toolClassifications,
    overallTier,
    healthDataFlag,
    spainNotes,
  };
}
