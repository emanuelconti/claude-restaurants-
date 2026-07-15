import { clsx } from "clsx";

export function Card({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className={clsx(
        "rounded-2xl border border-border-subtle bg-surface-raised/60 backdrop-blur-sm",
        className,
      )}
    >
      {children}
    </div>
  );
}
