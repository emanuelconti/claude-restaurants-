"use client";

import { useSyncExternalStore } from "react";
import { useTranslations } from "next-intl";

const TARGET = new Date("2026-08-02T00:00:00+02:00").getTime();

type TimeLeft = {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  expired: boolean;
};

// useSyncExternalStore requires getSnapshot to return a stable reference
// while nothing has actually changed, otherwise React treats every render
// as a store mutation and loops forever. Cache by the current second.
let cachedSnapshot: TimeLeft | null = null;
let cachedSecond = -1;

function computeTimeLeft(): TimeLeft {
  const diff = Math.max(0, TARGET - Date.now());
  const second = Math.floor(diff / 1000);
  if (cachedSnapshot === null || second !== cachedSecond) {
    cachedSecond = second;
    cachedSnapshot = {
      days: Math.floor(diff / (1000 * 60 * 60 * 24)),
      hours: Math.floor((diff / (1000 * 60 * 60)) % 24),
      minutes: Math.floor((diff / (1000 * 60)) % 60),
      seconds: second % 60,
      expired: diff <= 0,
    };
  }
  return cachedSnapshot;
}

function subscribe(callback: () => void) {
  const id = setInterval(callback, 1000);
  return () => clearInterval(id);
}

function getServerSnapshot(): TimeLeft | null {
  return null;
}

export function Countdown() {
  const t = useTranslations("countdown");
  const time = useSyncExternalStore(subscribe, computeTimeLeft, getServerSnapshot);

  const units: Array<{ key: "days" | "hours" | "minutes" | "seconds"; label: string }> = [
    { key: "days", label: t("days") },
    { key: "hours", label: t("hours") },
    { key: "minutes", label: t("minutes") },
    { key: "seconds", label: t("seconds") },
  ];

  return (
    <div className="flex flex-col items-center gap-4">
      <p className="text-center text-sm text-muted">
        {t("label")} · <span className="text-foreground">{t("date")}</span>
      </p>
      {time?.expired ? (
        <p className="text-sm font-medium text-risk-high">{t("expired")}</p>
      ) : (
        <div
          className="flex gap-3 sm:gap-5"
          role="timer"
          aria-live="polite"
          suppressHydrationWarning
        >
          {units.map((unit) => (
            <div
              key={unit.key}
              className="flex w-16 flex-col items-center gap-1 rounded-xl border border-border-subtle bg-surface-raised/70 py-3 sm:w-20"
            >
              <span className="font-mono text-2xl font-semibold tabular-nums sm:text-3xl">
                {time ? String(time[unit.key]).padStart(2, "0") : "--"}
              </span>
              <span className="text-[10px] uppercase tracking-wide text-muted">
                {unit.label}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
