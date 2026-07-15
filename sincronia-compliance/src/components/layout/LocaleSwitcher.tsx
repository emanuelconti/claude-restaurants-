"use client";

import { useLocale, useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";
import { useParams } from "next/navigation";

export function LocaleSwitcher() {
  const t = useTranslations("locale");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const params = useParams();

  return (
    <div
      role="group"
      aria-label={t("switchLabel")}
      className="flex items-center rounded-full border border-border-subtle bg-surface p-0.5 text-xs font-medium"
    >
      {routing.locales.map((loc) => (
        <button
          key={loc}
          onClick={() =>
            router.replace(
              // @ts-expect-error -- dynamic route params from usePathname
              { pathname, params },
              { locale: loc },
            )
          }
          aria-current={locale === loc}
          className={`rounded-full px-2.5 py-1 transition-colors ${
            locale === loc
              ? "bg-accent text-accent-contrast"
              : "text-muted hover:text-foreground"
          }`}
        >
          {t(loc)}
        </button>
      ))}
    </div>
  );
}
