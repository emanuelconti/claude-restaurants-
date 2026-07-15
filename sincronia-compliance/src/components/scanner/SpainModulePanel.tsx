import { useTranslations } from "next-intl";
import { Landmark } from "lucide-react";
import { Card } from "@/components/ui/Card";

export function SpainModulePanel({ notes }: { notes: string[] }) {
  const resultsT = useTranslations("scanner.results");
  const codesT = useTranslations("codes");

  return (
    <Card className="p-5">
      <div className="flex items-center gap-2.5">
        <Landmark className="size-4.5 text-accent-soft" />
        <h3 className="text-sm font-semibold">{resultsT("spainTitle")}</h3>
      </div>
      <div className="mt-4 space-y-4">
        {notes.map((code) => (
          <div key={code}>
            <p className="text-sm font-medium">
              {codesT(`spainNotes.${code}.label`)}
            </p>
            <p className="mt-1 text-xs text-muted">
              {codesT(`spainNotes.${code}.description`)}
            </p>
          </div>
        ))}
      </div>
    </Card>
  );
}
