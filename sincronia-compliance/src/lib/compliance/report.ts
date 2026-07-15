import { jsPDF } from "jspdf";
import type { RiskTier, ScanResult } from "./types";

export interface ReportDict {
  title: string;
  generatedOn: string;
  businessSection: string;
  sectorField: string;
  employeesField: string;
  toolsSection: string;
  overallRisk: string;
  obligationsLabel: string;
  legalBasisLabel: string;
  warningsLabel: string;
  spainModule: string;
  footerNote: string;
  sectorValue: string;
  employeesValue: string;
  riskTierLabel: (tier: RiskTier) => string;
  toolName: (toolId: string) => string;
  articleLabel: (code: string) => string;
  obligationLabel: (code: string) => string;
  obligationDescription: (code: string) => string;
  warningLabel: (code: string) => string;
  spainNoteLabel: (code: string) => string;
  spainNoteDescription: (code: string) => string;
  locale: string;
}

const PAGE_MARGIN = 18;
const PAGE_WIDTH = 210;
const PAGE_HEIGHT = 297;
const CONTENT_WIDTH = PAGE_WIDTH - PAGE_MARGIN * 2;
const ACCENT: [number, number, number] = [79, 107, 255];
const MUTED: [number, number, number] = [110, 118, 138];
const INK: [number, number, number] = [20, 24, 33];

export function generateComplianceReportPdf(
  result: ScanResult,
  dict: ReportDict,
): jsPDF {
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  let y = PAGE_MARGIN;

  const ensureSpace = (needed: number) => {
    if (y + needed > PAGE_HEIGHT - PAGE_MARGIN) {
      doc.addPage();
      y = PAGE_MARGIN;
    }
  };

  const writeParagraph = (
    text: string,
    { size = 10, color = INK, lineHeight = 5, bold = false }: {
      size?: number;
      color?: [number, number, number];
      lineHeight?: number;
      bold?: boolean;
    } = {},
  ) => {
    doc.setFont("helvetica", bold ? "bold" : "normal");
    doc.setFontSize(size);
    doc.setTextColor(...color);
    const lines = doc.splitTextToSize(text, CONTENT_WIDTH) as string[];
    ensureSpace(lines.length * lineHeight);
    doc.text(lines, PAGE_MARGIN, y);
    y += lines.length * lineHeight;
  };

  const sectionTitle = (text: string) => {
    ensureSpace(14);
    y += 4;
    doc.setDrawColor(...ACCENT);
    doc.setLineWidth(0.6);
    doc.line(PAGE_MARGIN, y, PAGE_MARGIN + 10, y);
    y += 6;
    writeParagraph(text, { size: 13, bold: true });
    y += 1;
  };

  // Header
  doc.setFillColor(...ACCENT);
  doc.rect(0, 0, PAGE_WIDTH, 3, "F");
  y += 4;
  writeParagraph("SincronIA Compliance", { size: 11, color: ACCENT, bold: true });
  writeParagraph(dict.title, { size: 18, bold: true });
  writeParagraph(
    `${dict.generatedOn}: ${new Date().toLocaleDateString(dict.locale)}`,
    { size: 9, color: MUTED },
  );
  y += 2;

  // Business section
  sectionTitle(dict.businessSection);
  if (result.business.name) {
    writeParagraph(result.business.name, { size: 12, bold: true });
  }
  writeParagraph(`${dict.sectorField}: ${dict.sectorValue}`, { size: 10, color: MUTED });
  writeParagraph(`${dict.employeesField}: ${dict.employeesValue}`, { size: 10, color: MUTED });

  // Overall risk
  sectionTitle(dict.overallRisk);
  writeParagraph(dict.riskTierLabel(result.overallTier), { size: 12, bold: true });

  // Tools
  sectionTitle(dict.toolsSection);
  for (const classification of result.toolClassifications) {
    ensureSpace(16);
    writeParagraph(dict.toolName(classification.toolId), { size: 12, bold: true });
    writeParagraph(dict.riskTierLabel(classification.tier), { size: 9, color: ACCENT, bold: true });

    if (classification.articles.length > 0) {
      writeParagraph(dict.legalBasisLabel + ":", { size: 9, bold: true, color: MUTED });
      for (const code of classification.articles) {
        writeParagraph(`• ${dict.articleLabel(code)}`, { size: 9, color: MUTED });
      }
    }

    if (classification.obligations.length > 0) {
      writeParagraph(dict.obligationsLabel + ":", { size: 9, bold: true, color: MUTED });
      for (const code of classification.obligations) {
        writeParagraph(`• ${dict.obligationLabel(code)}`, { size: 9.5, bold: true });
        writeParagraph(dict.obligationDescription(code), { size: 9, color: MUTED });
      }
    }

    if (classification.warnings.length > 0) {
      writeParagraph(dict.warningsLabel + ":", { size: 9, bold: true, color: MUTED });
      for (const code of classification.warnings) {
        writeParagraph(`⚠ ${dict.warningLabel(code)}`, { size: 9, color: MUTED });
      }
    }
    y += 3;
  }

  // Spain module
  sectionTitle(dict.spainModule);
  for (const code of result.spainNotes) {
    writeParagraph(dict.spainNoteLabel(code), { size: 10.5, bold: true });
    writeParagraph(dict.spainNoteDescription(code), { size: 9, color: MUTED });
    y += 2;
  }

  // Footer note on every page
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(7.5);
    doc.setTextColor(...MUTED);
    const footerLines = doc.splitTextToSize(dict.footerNote, CONTENT_WIDTH) as string[];
    doc.text(footerLines, PAGE_MARGIN, PAGE_HEIGHT - 12);
    doc.text(String(i), PAGE_WIDTH - PAGE_MARGIN, PAGE_HEIGHT - 12, { align: "right" });
  }

  return doc;
}
