"use client";

import { useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Container } from "@/components/ui/Container";
import { Button } from "@/components/ui/Button";
import { StepIndicator } from "./StepIndicator";
import { BusinessInfoStep } from "./BusinessInfoStep";
import { ToolSelectionStep } from "./ToolSelectionStep";
import { ContextQuestionsStep } from "./ContextQuestionsStep";
import { ResultsView } from "./ResultsView";
import { buildScanResult } from "@/lib/compliance/rules";
import {
  SECTORS,
  EMPLOYEE_RANGES,
  type BusinessInfo,
  type ContextFlag,
  type ToolAnswers,
} from "@/lib/compliance/types";
import { generateComplianceReportPdf, type ReportDict } from "@/lib/compliance/report";

type Step = "business" | "tools" | "context" | "results";
const STEPS: Step[] = ["business", "tools", "context", "results"];

const DEFAULT_BUSINESS: BusinessInfo = {
  name: "",
  sector: SECTORS[0],
  employeeRange: EMPLOYEE_RANGES[0],
};

export function ScannerWizard() {
  const t = useTranslations("scanner");
  const businessT = useTranslations("scanner.business");
  const toolsT = useTranslations("scanner.tools");
  const reportT = useTranslations("report");
  const riskTiersT = useTranslations("riskTiers");
  const codesT = useTranslations("codes");
  const locale = useLocale();

  const [step, setStep] = useState<Step>("business");
  const [business, setBusiness] = useState<BusinessInfo>(DEFAULT_BUSINESS);
  const [selectedToolIds, setSelectedToolIds] = useState<string[]>([]);
  const [answers, setAnswers] = useState<Record<string, ToolAnswers>>({});
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  const stepIndex = STEPS.indexOf(step);

  const scanResult = useMemo(() => {
    if (step !== "results") return null;
    return buildScanResult(
      business,
      selectedToolIds.map((toolId) => ({
        toolId,
        answers: answers[toolId] ?? {},
      })),
    );
  }, [step, business, selectedToolIds, answers]);

  const toggleTool = (toolId: string) => {
    setSelectedToolIds((prev) =>
      prev.includes(toolId) ? prev.filter((id) => id !== toolId) : [...prev, toolId],
    );
  };

  const setAnswer = (toolId: string, flag: ContextFlag, value: boolean) => {
    setAnswers((prev) => ({
      ...prev,
      [toolId]: { ...prev[toolId], [flag]: value },
    }));
  };

  const goNext = () => {
    const nextIndex = stepIndex + 1;
    if (nextIndex < STEPS.length) setStep(STEPS[nextIndex]);
  };

  const goBack = () => {
    const prevIndex = stepIndex - 1;
    if (prevIndex >= 0) setStep(STEPS[prevIndex]);
  };

  const restart = () => {
    setBusiness(DEFAULT_BUSINESS);
    setSelectedToolIds([]);
    setAnswers({});
    setStep("business");
  };

  const canContinue = step !== "tools" || selectedToolIds.length > 0;

  const handleDownload = async () => {
    if (!scanResult) return;
    setIsGeneratingReport(true);
    try {
      const dict: ReportDict = {
        title: reportT("title"),
        generatedOn: reportT("generatedOn"),
        businessSection: reportT("businessSection"),
        sectorField: reportT("sector"),
        employeesField: reportT("employees"),
        toolsSection: reportT("toolsSection"),
        overallRisk: reportT("overallRisk"),
        obligationsLabel: reportT("obligations"),
        legalBasisLabel: reportT("legalBasis"),
        warningsLabel: reportT("warnings"),
        spainModule: reportT("spainModule"),
        footerNote: reportT("footerNote"),
        sectorValue: businessT(`sectors.${scanResult.business.sector}`),
        employeesValue: businessT(`employeeRanges.${scanResult.business.employeeRange}`),
        riskTierLabel: (tier) => riskTiersT(`${tier}.label`),
        toolName: (toolId) => toolsT(`items.${toolId}.name`),
        articleLabel: (code) => codesT(`articles.${code}`),
        obligationLabel: (code) => codesT(`obligations.${code}.label`),
        obligationDescription: (code) => codesT(`obligations.${code}.description`),
        warningLabel: (code) => codesT(`warnings.${code}`),
        spainNoteLabel: (code) => codesT(`spainNotes.${code}.label`),
        spainNoteDescription: (code) => codesT(`spainNotes.${code}.description`),
        locale,
      };
      const doc = generateComplianceReportPdf(scanResult, dict);
      const filenameBase = scanResult.business.name || "sincronia-compliance";
      doc.save(`${filenameBase.replace(/\s+/g, "-").toLowerCase()}-report-${locale}.pdf`);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  return (
    <Container className="py-16">
      {step !== "results" && (
        <div className="mb-10 flex justify-center">
          <StepIndicator current={stepIndex + 1} />
        </div>
      )}

      {step === "business" && (
        <BusinessInfoStep value={business} onChange={setBusiness} />
      )}
      {step === "tools" && (
        <ToolSelectionStep selected={selectedToolIds} onToggle={toggleTool} />
      )}
      {step === "context" && (
        <ContextQuestionsStep
          selectedToolIds={selectedToolIds}
          answers={answers}
          onAnswer={setAnswer}
        />
      )}
      {step === "results" && scanResult && (
        <ResultsView
          result={scanResult}
          onDownload={handleDownload}
          isGeneratingReport={isGeneratingReport}
          onRestart={restart}
        />
      )}

      {step !== "results" && (
        <div className="mx-auto mt-10 flex max-w-2xl items-center justify-between">
          <Button
            variant="ghost"
            onClick={goBack}
            disabled={stepIndex === 0}
            className="disabled:invisible"
          >
            {t("back")}
          </Button>
          <Button onClick={goNext} disabled={!canContinue}>
            {t("next")}
          </Button>
        </div>
      )}
    </Container>
  );
}
