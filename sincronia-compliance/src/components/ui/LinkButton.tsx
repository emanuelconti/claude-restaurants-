import { Link } from "@/i18n/navigation";
import { buttonClasses, type ButtonSize, type ButtonVariant } from "./Button";

type LinkButtonProps = React.ComponentProps<typeof Link> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export function LinkButton({
  className,
  variant = "primary",
  size = "md",
  ...props
}: LinkButtonProps) {
  return (
    <Link className={buttonClasses(variant, size, className)} {...props} />
  );
}
