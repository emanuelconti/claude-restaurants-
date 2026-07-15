import { useTranslations } from "next-intl";
import { Container } from "@/components/ui/Container";
import { Card } from "@/components/ui/Card";
import {
  Bot,
  Gauge,
  Landmark,
  HeartPulse,
  FileText,
  MessageCircle,
} from "lucide-react";

const icons = [Bot, Gauge, Landmark, HeartPulse, FileText, MessageCircle];

export function FeatureGrid() {
  const t = useTranslations("features");
  const items = t.raw("items") as Array<{ title: string; description: string }>;

  return (
    <section className="border-b border-border-subtle py-24">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-sm font-medium text-accent-soft">
            {t("eyebrow")}
          </span>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            {t("title")}
          </h2>
          <p className="mt-4 text-muted">{t("subtitle")}</p>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item, i) => {
            const Icon = icons[i % icons.length];
            return (
              <Card key={item.title} className="p-6">
                <div className="mb-4 inline-flex size-10 items-center justify-center rounded-lg bg-accent/10 text-accent-soft">
                  <Icon className="size-5" />
                </div>
                <h3 className="font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm text-muted">{item.description}</p>
              </Card>
            );
          })}
        </div>
      </Container>
    </section>
  );
}
