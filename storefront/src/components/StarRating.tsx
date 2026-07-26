"use client";

import { IconStar } from "@/components/icons";

export function StarRating({
  value,
  max = 5,
  size = "md",
  interactive = false,
  onChange,
  label = "Rating",
}: {
  value: number;
  max?: number;
  size?: "sm" | "md" | "lg";
  interactive?: boolean;
  onChange?: (value: number) => void;
  label?: string;
}) {
  const sizeClass = size === "sm" ? "h-3.5 w-3.5" : size === "lg" ? "h-6 w-6" : "h-4 w-4";

  return (
    <div className="inline-flex items-center gap-0.5" role={interactive ? "radiogroup" : "img"} aria-label={`${label}: ${value} of ${max}`}>
      {Array.from({ length: max }, (_, index) => {
        const starValue = index + 1;
        const filled = starValue <= Math.round(value);
        if (!interactive) {
          return (
            <IconStar
              key={starValue}
              className={`${sizeClass} ${filled ? "text-gold" : "text-forest/20"}`}
            />
          );
        }
        return (
          <button
            key={starValue}
            type="button"
            role="radio"
            aria-checked={starValue === value}
            aria-label={`${starValue} star${starValue === 1 ? "" : "s"}`}
            onClick={() => onChange?.(starValue)}
            className="rounded-sm p-0.5 transition hover:scale-110"
          >
            <IconStar
              className={`${sizeClass} ${starValue <= value ? "text-gold" : "text-forest/20"}`}
            />
          </button>
        );
      })}
    </div>
  );
}
