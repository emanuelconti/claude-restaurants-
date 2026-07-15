import { useTranslations } from "next-intl";
import { AlertTriangle } from "lucide-react";
import type { ToolClassification } from "@/lib/compliance/types";
import { Card } from "@/components/ui/Card";
import { RiskBadge } from "./RiskBadge";

export function ToolResultCard({
  classification,
}: {
  classification: ToolClassification;
}) {
  const toolsT = useTranslations("scanner.tools");
  const resultsT = useTranslations("scanner.results");
  const codesT = useTranslations("codes");

  return (
    <Card className="p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold">
          {toolsT(`items.${classification.toolId}.name`)}
        </h3>
        <RiskBadge tier={classification.tier} size="sm" />
      </div>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {classification.articles.map((code) => (
          <span
            key={code}
            className="rounded-full border border-border-subtle bg-surface px-2.5 py-1 text-[11px] text-muted"
          >
            {codesT(`articles.${code}`)}
          </span>
        ))}
      </div>

      <div className="mt-4">
        <h4 className="text-xs font-semibold uppercase tracking-wide text-muted">
          {resultsT("obligationsTitle")}
        </h4>
        <ul className="mt-2 space-y-2">
          {classification.obligations.map((code) => (
            <li key={code} className="text-sm">
              <span className="font-medium">
                {codesT(`obligations.${code}.label`)}
              </span>
              <span className="block text-xs text-muted">
                {codesT(`obligations.${code}.description`)}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {classification.warnings.length > 0 && (
        <div className="mt-4 space-y-2 rounded-xl border border-risk-limited/30 bg-risk-limited/5 p-3">
          {classification.warnings.map((code) => (
            <div key={code} className="flex gap-2 text-xs text-muted">
              <AlertTriangle className="mt-0.5 size-3.5 shrink-0 text-risk-limited" />
              <span>{codesT(`warnings.${code}`)}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
