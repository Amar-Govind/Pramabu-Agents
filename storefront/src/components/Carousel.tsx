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
}: {
  items: ReactNode[];
  autoPlayMs?: number;
  className?: string;
  showDots?: boolean;
  ariaLabel?: string;
  variant?: "light" | "dark";
}) {
  const [index, setIndex] = useState(0);
  const count = items.length;
  const isDark = variant === "dark";

  useEffect(() => {
    if (!autoPlayMs || count <= 1) return;
    const id = window.setInterval(() => {
      setIndex((current) => (current + 1) % count);
    }, autoPlayMs);
    return () => window.clearInterval(id);
  }, [autoPlayMs, count]);

  if (!count) return null;

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

      {count > 1 ? (
        <>
          <button
            type="button"
            aria-label="Previous slide"
            onClick={() => setIndex((current) => (current - 1 + count) % count)}
            className={`absolute left-3 top-1/2 z-10 inline-flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full border shadow-soft transition ${
              isDark
                ? "border-gold/40 bg-white/20 text-sand backdrop-blur-sm hover:bg-white/35"
                : "border-gold/40 bg-white/50 text-forest backdrop-blur-sm hover:bg-gold/80"
            }`}
          >
            <IconChevronLeft />
          </button>
          <button
            type="button"
            aria-label="Next slide"
            onClick={() => setIndex((current) => (current + 1) % count)}
            className={`absolute right-3 top-1/2 z-10 inline-flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full border shadow-soft transition ${
              isDark
                ? "border-gold/40 bg-white/20 text-sand backdrop-blur-sm hover:bg-white/35"
                : "border-gold/40 bg-white/50 text-forest backdrop-blur-sm hover:bg-gold/80"
            }`}
          >
            <IconChevronRight />
          </button>
        </>
      ) : null}

      {showDots && count > 1 ? (
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
                    : isDark
                      ? "border border-gold/70 bg-transparent hover:border-gold hover:bg-gold/30"
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
