import { useTranslations } from "next-intl";
import { clsx } from "clsx";

const STEP_COUNT = 4;

export function StepIndicator({ current }: { current: number }) {
  const t = useTranslations("scanner");

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="flex items-center gap-2">
        {Array.from({ length: STEP_COUNT }).map((_, i) => (
          <span
            key={i}
            className={clsx(
              "h-1.5 w-10 rounded-full transition-colors",
              i < current ? "bg-accent" : "bg-border-subtle",
            )}
          />
        ))}
      </div>
      <p className="text-xs text-muted">
        {t("stepLabel", { current, total: STEP_COUNT })}
      </p>
    </div>
  );
}
