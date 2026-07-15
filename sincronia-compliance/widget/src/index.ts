import { CSS_TEXT } from "./styles";
import { createTranslator, chrome, type Locale } from "./i18n";
import {
  SECTORS,
  EMPLOYEE_RANGES,
  type BusinessInfo,
  type ToolAnswers,
  type ScanResult,
} from "../../src/lib/compliance/types";
import { TOOL_CATALOG, getToolDefinition } from "../../src/lib/compliance/catalog";
import { buildScanResult } from "../../src/lib/compliance/rules";
import { generateComplianceReportPdf, type ReportDict } from "../../src/lib/compliance/report";

type Step = "business" | "tools" | "context" | "results";
const STEPS: Step[] = ["business", "tools", "context", "results"];

interface WidgetState {
  locale: Locale;
  step: Step;
  business: BusinessInfo;
  selectedToolIds: string[];
  answers: Record<string, ToolAnswers>;
  isGeneratingReport: boolean;
}

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  props: Partial<HTMLElementTagNameMap[K]> & { className?: string } = {},
  children: (Node | string)[] = [],
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  Object.assign(node, props);
  for (const child of children) {
    node.append(typeof child === "string" ? document.createTextNode(child) : child);
  }
  return node;
}

function mountWidget(hostEl: HTMLElement) {
  const initialLocale: Locale = hostEl.dataset.locale === "es" ? "es" : "en";

  const shadow = hostEl.attachShadow({ mode: "open" });
  const styleTag = document.createElement("style");
  styleTag.textContent = CSS_TEXT;
  shadow.appendChild(styleTag);

  const root = el("div", { className: "scw-root", role: "region" });
  shadow.appendChild(root);

  const state: WidgetState = {
    locale: initialLocale,
    step: "business",
    business: { name: "", sector: SECTORS[0], employeeRange: EMPLOYEE_RANGES[0] },
    selectedToolIds: [],
    answers: {},
    isGeneratingReport: false,
  };

  function setState(patch: Partial<WidgetState>) {
    Object.assign(state, patch);
    render();
  }

  function render() {
    root.innerHTML = "";
    const t = createTranslator(state.locale);
    const ch = chrome(state.locale);
    root.setAttribute("aria-label", ch.title);

    // Header
    const header = el("div", { className: "scw-header" }, [
      el("div", {}, [
        el("div", { className: "scw-brand" }, [
          "SincronIA",
          el("span", {}, ["Compliance"]),
        ]),
        el("div", { className: "scw-subtitle" }, [ch.subtitle]),
      ]),
      el("button", {
        className: "scw-lang-btn",
        onclick: () => setState({ locale: state.locale === "es" ? "en" : "es" }),
      }, [ch.langToggle]),
    ]);
    root.appendChild(header);

    if (state.step !== "results") {
      const stepIndex = STEPS.indexOf(state.step);
      const steps = el("div", { className: "scw-steps" });
      STEPS.slice(0, -1).forEach((_, i) => {
        steps.appendChild(
          el("div", { className: `scw-step-dot${i <= stepIndex ? " active" : ""}` }),
        );
      });
      root.appendChild(steps);
    }

    const body = el("div", {});
    root.appendChild(body);

    if (state.step === "business") renderBusinessStep(body, t);
    if (state.step === "tools") renderToolsStep(body, t);
    if (state.step === "context") renderContextStep(body, t);
    if (state.step === "results") renderResultsStep(body, t, state.locale);

    if (state.step !== "results") {
      const stepIndex = STEPS.indexOf(state.step);
      const canContinue = state.step !== "tools" || state.selectedToolIds.length > 0;
      const actions = el("div", { className: "scw-actions" }, [
        el("button", {
          className: "scw-btn ghost",
          disabled: stepIndex === 0,
          onclick: () => setState({ step: STEPS[stepIndex - 1] }),
        }, [t("scanner.back")]),
        el("button", {
          className: "scw-btn primary",
          disabled: !canContinue,
          onclick: () => setState({ step: STEPS[stepIndex + 1] }),
        }, [t("scanner.next")]),
      ]);
      root.appendChild(actions);
    }

    const powered = el("div", { className: "scw-powered" }, [
      el("a", { href: "https://sincronia.live", target: "_blank", rel: "noopener" }, [
        ch.poweredBy,
      ]),
    ]);
    root.appendChild(powered);
  }

  function renderBusinessStep(container: HTMLElement, t: ReturnType<typeof createTranslator>) {
    container.appendChild(el("h2", { className: "scw-title" }, [t("scanner.business.title")]));
    container.appendChild(el("p", { className: "scw-desc" }, [t("scanner.business.subtitle")]));

    const nameField = el("div", { className: "scw-field" }, [
      el("label", { className: "scw-label" }, [t("scanner.business.nameLabel")]),
      el("input", {
        className: "scw-input",
        type: "text",
        value: state.business.name,
        placeholder: t("scanner.business.namePlaceholder"),
        oninput: (e: Event) =>
          setState({ business: { ...state.business, name: (e.target as HTMLInputElement).value } }),
      }),
    ]);
    container.appendChild(nameField);

    const sectorField = el("div", { className: "scw-field" }, [
      el("label", { className: "scw-label" }, [t("scanner.business.sectorLabel")]),
      el("div", { className: "scw-grid" }, SECTORS.map((sector) =>
        el("button", {
          className: `scw-card${state.business.sector === sector ? " selected" : ""}`,
          onclick: () => setState({ business: { ...state.business, sector } }),
        }, [t(`scanner.business.sectors.${sector}`)]),
      )),
    ]);
    container.appendChild(sectorField);

    const employeesField = el("div", { className: "scw-field" }, [
      el("label", { className: "scw-label" }, [t("scanner.business.employeesLabel")]),
      el("div", { className: "scw-grid" }, EMPLOYEE_RANGES.map((range) =>
        el("button", {
          className: `scw-card${state.business.employeeRange === range ? " selected" : ""}`,
          onclick: () => setState({ business: { ...state.business, employeeRange: range } }),
        }, [t(`scanner.business.employeeRanges.${range}`)]),
      )),
    ]);
    container.appendChild(employeesField);
  }

  function renderToolsStep(container: HTMLElement, t: ReturnType<typeof createTranslator>) {
    container.appendChild(el("h2", { className: "scw-title" }, [t("scanner.tools.title")]));
    container.appendChild(el("p", { className: "scw-desc" }, [t("scanner.tools.subtitle")]));

    const grid = el("div", { className: "scw-grid" });
    for (const tool of TOOL_CATALOG) {
      const isSelected = state.selectedToolIds.includes(tool.id);
      grid.appendChild(
        el("button", {
          className: `scw-card${isSelected ? " selected" : ""}`,
          onclick: () => {
            const next = isSelected
              ? state.selectedToolIds.filter((id) => id !== tool.id)
              : [...state.selectedToolIds, tool.id];
            setState({ selectedToolIds: next });
          },
        }, [
          el("div", { className: "scw-card-title" }, [
            t(`scanner.tools.items.${tool.id}.name`),
            el("span", { className: "scw-tag" }, [t(`scanner.tools.categories.${tool.category}`)]),
          ]),
          el("div", { className: "scw-card-desc" }, [t(`scanner.tools.items.${tool.id}.description`)]),
        ]),
      );
    }
    container.appendChild(grid);

    if (state.selectedToolIds.length === 0) {
      container.appendChild(
        el("p", { className: "scw-desc scw-center scw-mt-14" }, [
          t("scanner.tools.noneSelected"),
        ]),
      );
    }
  }

  function renderContextStep(container: HTMLElement, t: ReturnType<typeof createTranslator>) {
    container.appendChild(el("h2", { className: "scw-title" }, [t("scanner.context.title")]));
    container.appendChild(el("p", { className: "scw-desc" }, [t("scanner.context.subtitle")]));

    const toolsWithQuestions = state.selectedToolIds
      .map((id) => getToolDefinition(id))
      .filter((def): def is NonNullable<typeof def> => !!def && def.ask.length > 0);

    for (const def of toolsWithQuestions) {
      const block = el("div", { className: "scw-tool-block" }, [
        el("div", { className: "scw-tool-name" }, [t(`scanner.tools.items.${def.id}.name`)]),
      ]);
      for (const flag of def.ask) {
        const current = state.answers[def.id]?.[flag] ?? false;
        const row = el("div", { className: "scw-toggle-row" }, [
          el("span", { className: "scw-toggle-q" }, [t(`scanner.context.questions.${flag}`)]),
          el("div", { className: "scw-toggle-group" }, [true, false].map((option) =>
            el("button", {
              className: `scw-toggle-btn${current === option ? " active" : ""}`,
              onclick: () => {
                const toolAnswers = { ...(state.answers[def.id] ?? {}), [flag]: option };
                setState({ answers: { ...state.answers, [def.id]: toolAnswers } });
              },
            }, [option ? t("scanner.context.yes") : t("scanner.context.no")]),
          )),
        ]);
        block.appendChild(row);
      }
      container.appendChild(block);
    }
  }

  function computeResult(): ScanResult {
    return buildScanResult(
      state.business,
      state.selectedToolIds.map((toolId) => ({ toolId, answers: state.answers[toolId] ?? {} })),
    );
  }

  function renderResultsStep(container: HTMLElement, t: ReturnType<typeof createTranslator>, locale: Locale) {
    const result = computeResult();

    container.appendChild(el("h2", { className: "scw-title scw-center" }, [
      t("scanner.results.title"),
    ]));
    container.appendChild(el("p", { className: "scw-desc scw-center" }, [
      t("scanner.results.subtitle"),
    ]));

    container.appendChild(el("div", { className: "scw-overall" }, [
      el("div", { className: "scw-overall-label" }, [t("scanner.results.overallTitle")]),
      el("span", { className: `scw-badge ${result.overallTier}` }, [
        el("span", { className: "dot" }),
        t(`riskTiers.${result.overallTier}.label`),
      ]),
      el("p", { className: "scw-overall-summary" }, [t(`scanner.results.tierSummary.${result.overallTier}`)]),
    ]));

    if (result.healthDataFlag) {
      container.appendChild(el("div", { className: "scw-alert" }, [
        el("div", { className: "scw-alert-title" }, [t("scanner.results.healthDataAlert.title")]),
        el("div", { className: "scw-alert-body" }, [t("scanner.results.healthDataAlert.body")]),
      ]));
    }

    container.appendChild(el("div", { className: "scw-alert" }, [
      el("div", { className: "scw-alert-title" }, [t("scanner.results.aiLiteracyNote.title")]),
      el("div", { className: "scw-alert-body" }, [t("scanner.results.aiLiteracyNote.body")]),
    ]));

    container.appendChild(el("div", { className: "scw-obl-title" }, [t("scanner.results.toolsTitle")]));
    for (const classification of result.toolClassifications) {
      const block = el("div", { className: "scw-tool-block" });
      block.appendChild(el("div", {
        className: "scw-card-title scw-row-between",
      }, [
        el("span", { className: "scw-tool-name" }, [t(`scanner.tools.items.${classification.toolId}.name`)]),
        el("span", { className: `scw-badge ${classification.tier}` }, [
          el("span", { className: "dot" }),
          t(`riskTiers.${classification.tier}.shortLabel`),
        ]),
      ]));

      const articles = el("div", { className: "scw-articles" });
      for (const code of classification.articles) {
        articles.appendChild(el("span", { className: "scw-article-chip" }, [t(`codes.articles.${code}`)]));
      }
      block.appendChild(articles);

      block.appendChild(el("div", { className: "scw-obl-title" }, [t("scanner.results.obligationsTitle")]));
      for (const code of classification.obligations) {
        block.appendChild(el("div", { className: "scw-obl-item" }, [
          el("div", { className: "scw-obl-label" }, [t(`codes.obligations.${code}.label`)]),
          el("div", { className: "scw-obl-desc" }, [t(`codes.obligations.${code}.description`)]),
        ]));
      }

      for (const code of classification.warnings) {
        block.appendChild(el("div", { className: "scw-warning" }, [`⚠ ${t(`codes.warnings.${code}`)}`]));
      }

      container.appendChild(block);
    }

    container.appendChild(el("div", { className: "scw-obl-title" }, [t("scanner.results.spainTitle")]));
    const spainBlock = el("div", { className: "scw-tool-block" });
    for (const code of result.spainNotes) {
      spainBlock.appendChild(el("div", { className: "scw-obl-item" }, [
        el("div", { className: "scw-obl-label" }, [t(`codes.spainNotes.${code}.label`)]),
        el("div", { className: "scw-obl-desc" }, [t(`codes.spainNotes.${code}.description`)]),
      ]));
    }
    container.appendChild(spainBlock);

    container.appendChild(el("p", { className: "scw-footer-note scw-center" }, [
      t("scanner.results.disclaimer"),
    ]));

    const actions = el("div", { className: "scw-actions scw-actions-center" }, [
      el("button", {
        className: "scw-btn primary",
        disabled: state.isGeneratingReport,
        onclick: () => downloadReport(t, locale, result),
      }, [state.isGeneratingReport ? t("scanner.results.generatingReport") : t("scanner.results.downloadReport")]),
      el("button", {
        className: "scw-btn secondary",
        onclick: () => setState({
          step: "business",
          business: { name: "", sector: SECTORS[0], employeeRange: EMPLOYEE_RANGES[0] },
          selectedToolIds: [],
          answers: {},
        }),
      }, [t("scanner.restart")]),
    ]);
    container.appendChild(actions);
  }

  function downloadReport(t: ReturnType<typeof createTranslator>, locale: Locale, result: ScanResult) {
    setState({ isGeneratingReport: true });
    try {
      const dict: ReportDict = {
        title: t("report.title"),
        generatedOn: t("report.generatedOn"),
        businessSection: t("report.businessSection"),
        sectorField: t("report.sector"),
        employeesField: t("report.employees"),
        toolsSection: t("report.toolsSection"),
        overallRisk: t("report.overallRisk"),
        obligationsLabel: t("report.obligations"),
        legalBasisLabel: t("report.legalBasis"),
        warningsLabel: t("report.warnings"),
        spainModule: t("report.spainModule"),
        footerNote: t("report.footerNote"),
        sectorValue: t(`scanner.business.sectors.${result.business.sector}`),
        employeesValue: t(`scanner.business.employeeRanges.${result.business.employeeRange}`),
        riskTierLabel: (tier) => t(`riskTiers.${tier}.label`),
        toolName: (toolId) => t(`scanner.tools.items.${toolId}.name`),
        articleLabel: (code) => t(`codes.articles.${code}`),
        obligationLabel: (code) => t(`codes.obligations.${code}.label`),
        obligationDescription: (code) => t(`codes.obligations.${code}.description`),
        warningLabel: (code) => t(`codes.warnings.${code}`),
        spainNoteLabel: (code) => t(`codes.spainNotes.${code}.label`),
        spainNoteDescription: (code) => t(`codes.spainNotes.${code}.description`),
        locale,
      };
      const doc = generateComplianceReportPdf(result, dict);
      const filenameBase = result.business.name || "sincronia-compliance";
      doc.save(`${filenameBase.replace(/\s+/g, "-").toLowerCase()}-report-${locale}.pdf`);
    } finally {
      setState({ isGeneratingReport: false });
    }
  }

  render();
}

function init() {
  const hosts = document.querySelectorAll<HTMLElement>("[data-sincronia-compliance-widget]");
  hosts.forEach((hostEl) => {
    if (hostEl.dataset.scwMounted) return;
    hostEl.dataset.scwMounted = "true";
    mountWidget(hostEl);
  });
  const legacyHost = document.getElementById("sincronia-compliance-widget");
  if (legacyHost && !legacyHost.dataset.scwMounted) {
    legacyHost.dataset.scwMounted = "true";
    mountWidget(legacyHost);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
