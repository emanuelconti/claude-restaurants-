import { useTranslations } from "next-intl";
import { Container } from "@/components/ui/Container";
import { Card } from "@/components/ui/Card";
import { Landmark, FlaskConical, Stethoscope } from "lucide-react";

export function SpainSection() {
  const t = useTranslations("spainSection");

  const blocks = [
    { icon: Landmark, title: t("aesiaTitle"), body: t("aesiaBody") },
    { icon: FlaskConical, title: t("sandboxTitle"), body: t("sandboxBody") },
    { icon: Stethoscope, title: t("aepdTitle"), body: t("aepdBody") },
  ];

  return (
    <section className="border-b border-border-subtle bg-surface/30 py-24">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-sm font-medium text-accent-soft">
            {t("eyebrow")}
          </span>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            {t("title")}
          </h2>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-3">
          {blocks.map(({ icon: Icon, title, body }) => (
            <Card key={title} className="p-6">
              <div className="mb-4 inline-flex size-10 items-center justify-center rounded-lg bg-accent/10 text-accent-soft">
                <Icon className="size-5" />
              </div>
              <h3 className="font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-muted">{body}</p>
            </Card>
          ))}
        </div>
      </Container>
    </section>
  );
}
