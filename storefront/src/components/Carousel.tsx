"use client";

import { useEffect, useState, type ReactNode } from "react";
import { IconChevronLeft, IconChevronRight } from "@/components/icons";

export function Carousel({
  items,
  autoPlayMs = 0,
  className = "",
  showDots = true,
  ariaLabel = "Carousel",
  variant = "light",
  controls = "auto",
}: {
  items: ReactNode[];
  autoPlayMs?: number;
  className?: string;
  showDots?: boolean;
  ariaLabel?: string;
  variant?: "light" | "dark";
  /** overlay = over content; below = under content (won't cover text) */
  controls?: "auto" | "overlay" | "below";
}) {
  const [index, setIndex] = useState(0);
  const count = items.length;
  const isDark = variant === "dark";
  const placement =
    controls === "auto" ? (isDark ? "below" : "overlay") : controls;

  useEffect(() => {
    if (!autoPlayMs || count <= 1) return;
    const id = window.setInterval(() => {
      setIndex((current) => (current + 1) % count);
    }, autoPlayMs);
    return () => window.clearInterval(id);
  }, [autoPlayMs, count]);

  if (!count) return null;

  const arrowClass =
    placement === "below"
      ? isDark
        ? "border border-gold/50 bg-transparent text-gold-light hover:bg-gold/15"
        : "border border-gold/50 bg-transparent text-forest hover:bg-gold/20"
      : isDark
        ? "border border-gold/30 bg-transparent text-sand/90 hover:bg-white/10"
        : "border border-gold/30 bg-transparent text-forest hover:bg-gold/20";

  const Controls = count > 1 ? (
    <div
      className={
        placement === "below"
          ? "mt-8 flex items-center justify-center gap-4"
          : "pointer-events-none absolute inset-x-0 top-1/2 z-10 flex -translate-y-1/2 justify-between px-3"
      }
    >
      <button
        type="button"
        aria-label="Previous slide"
        onClick={() => setIndex((current) => (current - 1 + count) % count)}
        className={`pointer-events-auto inline-flex h-10 w-10 items-center justify-center rounded-full transition ${arrowClass}`}
      >
        <IconChevronLeft />
      </button>

      {placement === "below" && showDots ? (
        <div className="flex items-center gap-2.5">
          {items.map((_, i) => {
            const active = i === index;
            return (
              <button
                key={i}
                type="button"
                aria-label={`Go to slide ${i + 1}`}
                aria-current={active ? "true" : undefined}
                onClick={() => setIndex(i)}
                className={`h-2.5 w-2.5 rounded-full transition ${
                  active
                    ? "border border-gold bg-gold"
                    : "border border-gold/70 bg-transparent hover:border-gold hover:bg-gold/30"
                }`}
              />
            );
          })}
        </div>
      ) : null}

      <button
        type="button"
        aria-label="Next slide"
        onClick={() => setIndex((current) => (current + 1) % count)}
        className={`pointer-events-auto inline-flex h-10 w-10 items-center justify-center rounded-full transition ${arrowClass}`}
      >
        <IconChevronRight />
      </button>
    </div>
  ) : null;

  return (
    <div className={`relative ${className}`} aria-roledescription="carousel" aria-label={ariaLabel}>
      <div className="overflow-hidden">
        <div
          className="flex transition-transform duration-500 ease-out"
          style={{ transform: `translateX(-${index * 100}%)` }}
        >
          {items.map((item, i) => (
            <div key={i} className="w-full shrink-0" aria-hidden={i !== index}>
              {item}
            </div>
          ))}
        </div>
      </div>

      {Controls}

      {placement === "overlay" && showDots && count > 1 ? (
        <div className="mt-4 flex justify-center gap-2.5">
          {items.map((_, i) => {
            const active = i === index;
            return (
              <button
                key={i}
                type="button"
                aria-label={`Go to slide ${i + 1}`}
                aria-current={active ? "true" : undefined}
                onClick={() => setIndex(i)}
                className={`h-2.5 w-2.5 rounded-full transition ${
                  active
                    ? "border border-gold bg-gold"
                    : "border border-gold/70 bg-transparent hover:border-gold hover:bg-gold/30"
                }`}
              />
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
