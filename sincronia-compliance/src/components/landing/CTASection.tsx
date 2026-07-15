import { useTranslations } from "next-intl";
import { Container } from "@/components/ui/Container";
import { LinkButton } from "@/components/ui/LinkButton";

export function CTASection() {
  const t = useTranslations("cta");

  return (
    <section className="py-24">
      <Container>
        <div className="glow relative overflow-hidden rounded-3xl border border-border-subtle bg-surface-raised/60 px-8 py-16 text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            {t("title")}
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-muted">{t("subtitle")}</p>
          <LinkButton href="/scanner" size="lg" className="mt-8">
            {t("button")}
          </LinkButton>
        </div>
      </Container>
    </section>
  );
}
