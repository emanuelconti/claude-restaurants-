import es from "../../messages/es.json";
import en from "../../messages/en.json";

export type Locale = "es" | "en";

const DICTS = { es, en } as const;

const WIDGET_CHROME = {
  es: {
    title: "Escáner de cumplimiento IA",
    subtitle: "Un producto de SincronIA",
    poweredBy: "Creado con SincronIA Compliance",
    langToggle: "EN",
  },
  en: {
    title: "AI compliance scanner",
    subtitle: "A SincronIA product",
    poweredBy: "Built with SincronIA Compliance",
    langToggle: "ES",
  },
} as const;

function get(obj: unknown, path: string): unknown {
  return path
    .split(".")
    .reduce<unknown>(
      (acc, key) =>
        acc && typeof acc === "object" ? (acc as Record<string, unknown>)[key] : undefined,
      obj,
    );
}

export function createTranslator(locale: Locale) {
  const dict = DICTS[locale];
  return function t(path: string, vars?: Record<string, string | number>): string {
    let value = get(dict, path);
    if (typeof value !== "string") {
      value = path;
    }
    let str = value as string;
    if (vars) {
      for (const [key, val] of Object.entries(vars)) {
        str = str.replace(`{${key}}`, String(val));
      }
    }
    return str;
  };
}

export function raw(locale: Locale, path: string): unknown {
  return get(DICTS[locale], path);
}

export function chrome(locale: Locale) {
  return WIDGET_CHROME[locale];
}
