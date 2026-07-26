import { IconCart, IconCheck, IconShield, IconTruck } from "@/components/icons";

const steps = [
  { key: "cart", label: "Cart", icon: IconCart },
  { key: "details", label: "Details", icon: IconTruck },
  { key: "payment", label: "Payment", icon: IconShield },
] as const;

export function CheckoutSteps({ current }: { current: "cart" | "details" | "payment" }) {
  const currentIndex = steps.findIndex((step) => step.key === current);

  return (
    <ol className="grid grid-cols-3 gap-2 rounded-xl border border-gold/25 bg-white/80 p-3">
      {steps.map((step, index) => {
        const Icon = step.icon;
        const done = index < currentIndex;
        const active = index === currentIndex;
        return (
          <li
            key={step.key}
            className={`flex items-center justify-center gap-2 rounded-md px-2 py-2 text-xs font-semibold sm:text-sm ${
              active
                ? "bg-gold text-ink"
                : done
                  ? "bg-forest text-sand"
                  : "bg-mist text-ink/50"
            }`}
          >
            {done ? <IconCheck className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
            <span>{step.label}</span>
          </li>
        );
      })}
    </ol>
  );
}
