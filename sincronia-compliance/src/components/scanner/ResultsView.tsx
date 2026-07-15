import { useTranslations } from "next-intl";
import { HeartPulse, GraduationCap, FileDown, RotateCcw } from "lucide-react";
import type { ScanResult } from "@/lib/compliance/types";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { RiskBadge } from "./RiskBadge";
import { ToolResultCard } from "./ToolResultCard";
import { SpainModulePanel } from "./SpainModulePanel";

export function ResultsView({
  result,
  onDownload,
  isGeneratingReport,
  onRestart,
}: {
  result: ScanResult;
  onDownload: () => void;
  isGeneratingReport: boolean;
  onRestart: () => void;
}) {
  const t = useTranslations("scanner.results");
  const scannerT = useTranslations("scanner");

  return (
    <div className="mx-auto max-w-4xl">
      <div className="text-center">
        <h1 className="text-2xl font-semibold tracking-tight">{t("title")}</h1>
        <p className="mt-2 text-sm text-muted">{t("subtitle")}</p>
      </div>

      <Card className="mt-8 p-6 text-center">
        <p className="text-xs font-medium uppercase tracking-wide text-muted">
          {t("overallTitle")}
        </p>
        <div className="mt-3 flex justify-center">
          <RiskBadge tier={result.overallTier} />
        </div>
        <p className="mx-auto mt-3 max-w-lg text-sm text-muted">
          {t(`tierSummary.${result.overallTier}`)}
        </p>
      </Card>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {result.healthDataFlag && (
          <Card className="border-risk-high/30 bg-risk-high/5 p-5">
            <div className="flex items-center gap-2.5">
              <HeartPulse className="size-4.5 text-risk-high" />
              <h3 className="text-sm font-semibold">
                {t("healthDataAlert.title")}
              </h3>
            </div>
            <p className="mt-2 text-xs text-muted">
              {t("healthDataAlert.body")}
            </p>
          </Card>
        )}
        <Card className="p-5">
          <div className="flex items-center gap-2.5">
            <GraduationCap className="size-4.5 text-accent-soft" />
            <h3 className="text-sm font-semibold">
              {t("aiLiteracyNote.title")}
            </h3>
          </div>
          <p className="mt-2 text-xs text-muted">{t("aiLiteracyNote.body")}</p>
        </Card>
      </div>

      <h2 className="mt-10 text-lg font-semibold">{t("toolsTitle")}</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {result.toolClassifications.map((classification) => (
          <ToolResultCard key={classification.toolId} classification={classification} />
        ))}
      </div>

      <div className="mt-6">
        <SpainModulePanel notes={result.spainNotes} />
      </div>

      <p className="mt-6 text-center text-xs text-muted">{t("disclaimer")}</p>

      <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
        <Button size="lg" onClick={onDownload} disabled={isGeneratingReport}>
          <FileDown className="size-4" />
          {isGeneratingReport ? t("generatingReport") : t("downloadReport")}
        </Button>
        <Button size="lg" variant="secondary" onClick={onRestart}>
          <RotateCcw className="size-4" />
          {scannerT("restart")}
        </Button>
      </div>
    </div>
  );
}
