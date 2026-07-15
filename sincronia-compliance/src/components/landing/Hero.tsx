import { useTranslations } from "next-intl";
import { Container } from "@/components/ui/Container";
import { LinkButton } from "@/components/ui/LinkButton";
import { Countdown } from "./Countdown";
import { ShieldCheck, ScrollText, FileDown } from "lucide-react";

export function Hero() {
  const t = useTranslations("hero");

  return (
    <section className="relative overflow-hidden border-b border-border-subtle">
      <div className="glow bg-grid absolute inset-0 -z-10" />
      <Container className="flex flex-col items-center gap-8 py-24 text-center sm:py-32">
        <span className="rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-xs font-medium text-accent-soft">
          {t("eyebrow")}
        </span>
        <h1 className="max-w-4xl text-4xl font-semibold tracking-tight text-balance sm:text-6xl">
          {t("headline")}{" "}
          <span className="text-accent">{t("headlineAccent")}</span>
        </h1>
        <p className="max-w-2xl text-lg text-muted text-balance">
          {t("subheadline")}
        </p>
        <div className="flex flex-col items-center gap-3 sm:flex-row">
          <LinkButton href="/scanner" size="lg">
            {t("ctaPrimary")}
          </LinkButton>
          <LinkButton href="#how-it-works" variant="secondary" size="lg">
            {t("ctaSecondary")}
          </LinkButton>
        </div>

        <div className="mt-4 grid gap-3 text-left sm:grid-cols-3">
          {[
            { icon: ScrollText, text: t("trustBadge1") },
            { icon: ShieldCheck, text: t("trustBadge2") },
            { icon: FileDown, text: t("trustBadge3") },
          ].map(({ icon: Icon, text }) => (
            <div
              key={text}
              className="flex items-center gap-2.5 rounded-xl border border-border-subtle bg-surface-raised/50 px-4 py-3 text-xs text-muted"
            >
              <Icon className="size-4 shrink-0 text-accent-soft" />
              {text}
            </div>
          ))}
        </div>

        <div className="mt-10 w-full rounded-2xl border border-border-subtle bg-surface/60 px-6 py-8">
          <Countdown />
        </div>
      </Container>
    </section>
  );
}
