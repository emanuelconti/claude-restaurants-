"use client";

import { useTranslations } from "next-intl";
import { clsx } from "clsx";
import { TOOL_CATALOG } from "@/lib/compliance/catalog";
import { Card } from "@/components/ui/Card";
import {
  MessageCircle,
  Phone,
  CalendarClock,
  Bot,
  Sparkles,
  BarChart3,
  Image as ImageIcon,
  SmilePlus,
  UserSearch,
  Fingerprint,
  Check,
} from "lucide-react";

const TOOL_ICONS: Record<string, typeof MessageCircle> = {
  "whatsapp-ai": MessageCircle,
  "voice-receptionist": Phone,
  "appointment-scheduler": CalendarClock,
  "chatgpt-assistant": Bot,
  "copilot-assistant": Sparkles,
  "crm-ai-scoring": BarChart3,
  "content-generation-ai": ImageIcon,
  "sentiment-emotion-ai": SmilePlus,
  "recruitment-ai": UserSearch,
  "biometric-attendance-ai": Fingerprint,
};

export function ToolSelectionStep({
  selected,
  onToggle,
}: {
  selected: string[];
  onToggle: (toolId: string) => void;
}) {
  const t = useTranslations("scanner.tools");

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="text-2xl font-semibold tracking-tight">{t("title")}</h1>
      <p className="mt-2 text-sm text-muted">{t("subtitle")}</p>

      <div className="mt-8 grid gap-3 sm:grid-cols-2">
        {TOOL_CATALOG.map((tool) => {
          const Icon = TOOL_ICONS[tool.id] ?? Bot;
          const isSelected = selected.includes(tool.id);
          return (
            <Card
              key={tool.id}
              className={clsx(
                "cursor-pointer p-4 transition-colors hover:border-accent/50",
                isSelected && "border-accent bg-accent/10",
              )}
            >
              <button
                type="button"
                onClick={() => onToggle(tool.id)}
                aria-pressed={isSelected}
                className="flex w-full items-start gap-3 text-left"
              >
                <span
                  className={clsx(
                    "flex size-9 shrink-0 items-center justify-center rounded-lg",
                    isSelected
                      ? "bg-accent text-accent-contrast"
                      : "bg-surface text-accent-soft",
                  )}
                >
                  <Icon className="size-4.5" />
                </span>
                <span className="flex-1">
                  <span className="flex items-center gap-2">
                    <span className="text-sm font-semibold">
                      {t(`items.${tool.id}.name`)}
                    </span>
                    <span className="rounded-full border border-border-subtle px-2 py-0.5 text-[10px] text-muted">
                      {t(`categories.${tool.category}`)}
                    </span>
                  </span>
                  <span className="mt-1 block text-xs text-muted">
                    {t(`items.${tool.id}.description`)}
                  </span>
                </span>
                <span
                  className={clsx(
                    "flex size-5 shrink-0 items-center justify-center rounded-full border",
                    isSelected
                      ? "border-accent bg-accent text-accent-contrast"
                      : "border-border-subtle",
                  )}
                >
                  {isSelected && <Check className="size-3.5" />}
                </span>
              </button>
            </Card>
          );
        })}
      </div>

      {selected.length === 0 && (
        <p className="mt-6 text-center text-sm text-muted">
          {t("noneSelected")}
        </p>
      )}
    </div>
  );
}
