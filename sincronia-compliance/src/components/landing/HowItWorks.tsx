import { useTranslations } from "next-intl";
import { Container } from "@/components/ui/Container";

export function HowItWorks() {
  const t = useTranslations("howItWorks");
  const steps = t.raw("steps") as Array<{ title: string; description: string }>;

  return (
    <section id="how-it-works" className="border-b border-border-subtle py-24">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-sm font-medium text-accent-soft">
            {t("eyebrow")}
          </span>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            {t("title")}
          </h2>
        </div>

        <ol className="mt-14 grid gap-8 sm:grid-cols-3">
          {steps.map((step, i) => (
            <li key={step.title} className="relative">
              <span className="mb-4 flex size-10 items-center justify-center rounded-full border border-accent/30 bg-accent/10 font-mono text-sm font-semibold text-accent-soft">
                {String(i + 1).padStart(2, "0")}
              </span>
              <h3 className="font-semibold">{step.title}</h3>
              <p className="mt-2 text-sm text-muted">{step.description}</p>
            </li>
          ))}
        </ol>
      </Container>
    </section>
  );
}
