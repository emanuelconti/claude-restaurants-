import { setRequestLocale } from "next-intl/server";
import { Hero } from "@/components/landing/Hero";
import { FeatureGrid } from "@/components/landing/FeatureGrid";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { SpainSection } from "@/components/landing/SpainSection";
import { CTASection } from "@/components/landing/CTASection";

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <>
      <Hero />
      <FeatureGrid />
      <HowItWorks />
      <SpainSection />
      <CTASection />
    </>
  );
}
