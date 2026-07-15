import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { Container } from "@/components/ui/Container";

export function Footer() {
  const t = useTranslations("footer");
  const nav = useTranslations("nav");
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-border-subtle bg-surface/40">
      <Container className="grid gap-10 py-14 sm:grid-cols-2 lg:grid-cols-4">
        <div className="lg:col-span-2">
          <span className="text-lg font-semibold tracking-tight">
            {nav("brand")}
            <span className="text-accent">{nav("product")}</span>
          </span>
          <p className="mt-3 max-w-sm text-sm text-muted">{t("tagline")}</p>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-foreground">
            {t("product")}
          </h3>
          <ul className="mt-3 space-y-2 text-sm text-muted">
            <li>
              <Link href="/scanner" className="hover:text-foreground">
                {t("scanner")}
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-foreground">
            {t("legal")}
          </h3>
          <ul className="mt-3 space-y-2 text-sm text-muted">
            <li>{t("disclaimerShort")}</li>
          </ul>
        </div>
      </Container>
      <Container className="border-t border-border-subtle py-6 text-xs text-muted">
        © {year} SincronIA. {t("rights")}
      </Container>
    </footer>
  );
}
