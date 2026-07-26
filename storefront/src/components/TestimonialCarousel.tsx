"use client";

import { Carousel } from "@/components/Carousel";
import { IconStar, IconUser } from "@/components/icons";
import { site } from "@/lib/site";

export function TestimonialCarousel() {
  const slides = site.testimonials.map((item) => (
    <blockquote key={item.name} className="mx-auto max-w-3xl px-4 text-center md:px-10">
      <div className="mx-auto mb-5 inline-flex h-12 w-12 items-center justify-center rounded-full bg-gold/20 text-gold-light">
        <IconUser className="h-6 w-6" />
      </div>
      <div className="mb-4 flex justify-center gap-1 text-gold-light">
        {Array.from({ length: 5 }).map((_, i) => (
          <IconStar key={i} className="h-4 w-4" />
        ))}
      </div>
      <p className="font-display text-2xl leading-relaxed text-sand md:text-3xl">
        “{item.quote}”
      </p>
      <footer className="mt-6">
        <p className="text-sm font-semibold text-gold-light">{item.name}</p>
        {"role" in item && item.role ? (
          <p className="mt-1 text-xs text-sand/60">{item.role}</p>
        ) : null}
      </footer>
    </blockquote>
  ));

  return <Carousel items={slides} autoPlayMs={5000} ariaLabel="Customer testimonials" />;
}
