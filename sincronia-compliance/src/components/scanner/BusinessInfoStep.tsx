"use client";

import { useTranslations } from "next-intl";
import { clsx } from "clsx";
import { SECTORS, EMPLOYEE_RANGES, type BusinessInfo } from "@/lib/compliance/types";
import { Card } from "@/components/ui/Card";

export function BusinessInfoStep({
  value,
  onChange,
}: {
  value: BusinessInfo;
  onChange: (value: BusinessInfo) => void;
}) {
  const t = useTranslations("scanner.business");

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold tracking-tight">{t("title")}</h1>
      <p className="mt-2 text-sm text-muted">{t("subtitle")}</p>

      <div className="mt-8 space-y-8">
        <div>
          <label className="mb-2 block text-sm font-medium" htmlFor="business-name">
            {t("nameLabel")}
          </label>
          <input
            id="business-name"
            type="text"
            value={value.name}
            onChange={(e) => onChange({ ...value, name: e.target.value })}
            placeholder={t("namePlaceholder")}
            className="w-full rounded-xl border border-border-subtle bg-surface px-4 py-3 text-sm outline-none focus:border-accent"
          />
        </div>

        <div>
          <span className="mb-3 block text-sm font-medium">{t("sectorLabel")}</span>
          <div className="grid gap-2.5 sm:grid-cols-2">
            {SECTORS.map((sector) => (
              <Card
                key={sector}
                className={clsx(
                  "cursor-pointer p-4 text-sm transition-colors hover:border-accent/50",
                  value.sector === sector && "border-accent bg-accent/10",
                )}
              >
                <button
                  type="button"
                  onClick={() => onChange({ ...value, sector })}
                  className="w-full text-left"
                >
                  {t(`sectors.${sector}`)}
                </button>
              </Card>
            ))}
          </div>
        </div>

        <div>
          <span className="mb-3 block text-sm font-medium">
            {t("employeesLabel")}
          </span>
          <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
            {EMPLOYEE_RANGES.map((range) => (
              <Card
                key={range}
                className={clsx(
                  "cursor-pointer p-3 text-center text-xs font-medium transition-colors hover:border-accent/50",
                  value.employeeRange === range && "border-accent bg-accent/10",
                )}
              >
                <button
                  type="button"
                  onClick={() => onChange({ ...value, employeeRange: range })}
                  className="w-full"
                >
                  {t(`employeeRanges.${range}`)}
                </button>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
