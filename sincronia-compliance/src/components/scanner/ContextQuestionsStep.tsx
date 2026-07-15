"use client";

import { useTranslations } from "next-intl";
import { clsx } from "clsx";
import { getToolDefinition } from "@/lib/compliance/catalog";
import type { ContextFlag, ToolAnswers } from "@/lib/compliance/types";
import { Card } from "@/components/ui/Card";

export function ContextQuestionsStep({
  selectedToolIds,
  answers,
  onAnswer,
}: {
  selectedToolIds: string[];
  answers: Record<string, ToolAnswers>;
  onAnswer: (toolId: string, flag: ContextFlag, value: boolean) => void;
}) {
  const t = useTranslations("scanner.context");
  const toolsT = useTranslations("scanner.tools");

  const toolsWithQuestions = selectedToolIds
    .map((id) => getToolDefinition(id))
    .filter((def): def is NonNullable<typeof def> => !!def && def.ask.length > 0);

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold tracking-tight">{t("title")}</h1>
      <p className="mt-2 text-sm text-muted">{t("subtitle")}</p>

      <div className="mt-8 space-y-4">
        {toolsWithQuestions.map((def) => (
          <Card key={def.id} className="p-5">
            <h2 className="text-sm font-semibold">
              {toolsT(`items.${def.id}.name`)}
            </h2>
            <div className="mt-4 space-y-3">
              {def.ask.map((flag) => (
                <div
                  key={flag}
                  className="flex items-center justify-between gap-4"
                >
                  <p className="text-sm text-muted">
                    {t(`questions.${flag}`)}
                  </p>
                  <div className="flex shrink-0 overflow-hidden rounded-full border border-border-subtle text-xs font-medium">
                    {[true, false].map((option) => {
                      const isActive = (answers[def.id]?.[flag] ?? false) === option;
                      return (
                        <button
                          key={String(option)}
                          type="button"
                          onClick={() => onAnswer(def.id, flag, option)}
                          className={clsx(
                            "px-3.5 py-1.5 transition-colors",
                            isActive
                              ? "bg-accent text-accent-contrast"
                              : "bg-surface text-muted hover:text-foreground",
                          )}
                        >
                          {option ? t("yes") : t("no")}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
