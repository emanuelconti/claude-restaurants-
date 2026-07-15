import { useTranslations } from "next-intl";
import { clsx } from "clsx";
import type { RiskTier } from "@/lib/compliance/types";

const dotClasses: Record<RiskTier, string> = {
  unacceptable: "bg-risk-unacceptable",
  high: "bg-risk-high",
  limited: "bg-risk-limited",
  minimal: "bg-risk-minimal",
};

const textClasses: Record<RiskTier, string> = {
  unacceptable: "text-risk-unacceptable border-risk-unacceptable/40 bg-risk-unacceptable/10",
  high: "text-risk-high border-risk-high/40 bg-risk-high/10",
  limited: "text-risk-limited border-risk-limited/40 bg-risk-limited/10",
  minimal: "text-risk-minimal border-risk-minimal/40 bg-risk-minimal/10",
};

export function RiskBadge({
  tier,
  size = "md",
}: {
  tier: RiskTier;
  size?: "sm" | "md";
}) {
  const t = useTranslations("riskTiers");
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-2 rounded-full border font-medium",
        textClasses[tier],
        size === "sm" ? "px-2.5 py-1 text-xs" : "px-3.5 py-1.5 text-sm",
      )}
    >
      <span className={clsx("size-2 rounded-full", dotClasses[tier])} />
      {t(`${tier}.label`)}
    </span>
  );
}
