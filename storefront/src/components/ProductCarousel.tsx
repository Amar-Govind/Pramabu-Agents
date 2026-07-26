"use client";

import { useEffect, useRef, useState } from "react";
import { ProductCard } from "@/components/ProductCard";
import { IconChevronLeft, IconChevronRight } from "@/components/icons";
import type { Product } from "@/lib/products";

export function ProductCarousel({
  title,
  subtitle,
  products,
}: {
  title: string;
  subtitle?: string;
  products: Product[];
}) {
  const scrollerRef = useRef<HTMLDivElement>(null);
  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(true);

  function updateButtons() {
    const el = scrollerRef.current;
    if (!el) return;
    setCanPrev(el.scrollLeft > 8);
    setCanNext(el.scrollLeft + el.clientWidth < el.scrollWidth - 8);
  }

  useEffect(() => {
    updateButtons();
    const el = scrollerRef.current;
    if (!el) return;
    el.addEventListener("scroll", updateButtons, { passive: true });
    window.addEventListener("resize", updateButtons);
    return () => {
      el.removeEventListener("scroll", updateButtons);
      window.removeEventListener("resize", updateButtons);
    };
  }, [products.length]);

  function scrollByCards(direction: -1 | 1) {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollBy({ left: direction * Math.min(el.clientWidth * 0.85, 320), behavior: "smooth" });
  }

  if (!products.length) return null;

  return (
    <section className="mt-16">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div className="max-w-2xl">
          <h2 className="font-display text-3xl text-ink md:text-4xl">{title}</h2>
          {subtitle ? <p className="mt-2 text-sm text-ink/65">{subtitle}</p> : null}
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            aria-label="Previous products"
            disabled={!canPrev}
            onClick={() => scrollByCards(-1)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-gold/40 bg-white text-forest disabled:opacity-35"
          >
            <IconChevronLeft />
          </button>
          <button
            type="button"
            aria-label="Next products"
            disabled={!canNext}
            onClick={() => scrollByCards(1)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-gold/40 bg-white text-forest disabled:opacity-35"
          >
            <IconChevronRight />
          </button>
        </div>
      </div>

      <div
        ref={scrollerRef}
        className="no-scrollbar -mx-5 flex snap-x snap-mandatory gap-4 overflow-x-auto px-5 pb-2 md:mx-0 md:px-0"
      >
        {products.map((product) => (
          <div key={product.slug} className="w-[230px] shrink-0 snap-start sm:w-[250px] md:w-[260px]">
            <ProductCard product={product} />
          </div>
        ))}
      </div>
    </section>
  );
}
