import { setRequestLocale } from "next-intl/server";
import { ScannerWizard } from "@/components/scanner/ScannerWizard";

export default async function ScannerPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return <ScannerWizard />;
}
