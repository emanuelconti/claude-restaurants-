import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { Container } from "@/components/ui/Container";
import { LocaleSwitcher } from "./LocaleSwitcher";
import { LinkButton } from "@/components/ui/LinkButton";

export function Header() {
  const t = useTranslations("nav");

  return (
    <header className="sticky top-0 z-50 border-b border-border-subtle bg-background/80 backdrop-blur-md">
      <Container className="flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-lg font-semibold tracking-tight">
            {t("brand")}
            <span className="text-accent">{t("product")}</span>
          </span>
        </Link>
        <div className="flex items-center gap-3">
          <LocaleSwitcher />
          <LinkButton href="/scanner" size="md" className="hidden sm:inline-flex">
            {t("start")}
          </LinkButton>
        </div>
      </Container>
    </header>
  );
}
