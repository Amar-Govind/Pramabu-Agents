"use client";

import Image from "next/image";
import Link from "next/link";
import { Carousel } from "@/components/Carousel";
import { site } from "@/lib/site";

export function HeroCarousel() {
  const slides = site.banners.map((banner) => (
    <section key={banner.href + banner.title} className="relative min-h-[88vh] overflow-hidden">
      <div className="absolute inset-0">
        <Image
          src={banner.image}
          alt={banner.title}
          fill
          priority
          className="object-cover"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-forest via-forest/78 to-forest/20" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(201,162,39,0.28),transparent_40%)]" />
      </div>

      <div className="relative mx-auto flex min-h-[88vh] max-w-site flex-col justify-center px-5 py-20 md:px-8">
        <Image
          src={site.logo}
          alt="Parambu Organics golden logo"
          width={88}
          height={88}
          className="h-20 w-20 object-contain md:h-24 md:w-24"
          priority
        />
        <p className="mt-5 font-display text-5xl leading-none text-gold-light sm:text-6xl md:text-7xl lg:text-8xl">
          Parambu Organics
        </p>
        <h1 className="mt-6 max-w-xl font-display text-3xl leading-tight text-sand md:text-4xl">
          {banner.title}
        </h1>
        <p className="mt-5 max-w-md text-base leading-relaxed text-sand/85 md:text-lg">
          {banner.subtitle}
        </p>
        <div className="mt-9 flex flex-wrap gap-3">
          <Link
            href={banner.href}
            className="rounded-md bg-gold px-6 py-3 text-sm font-semibold text-ink transition hover:bg-gold-light"
          >
            {banner.cta}
          </Link>
          <Link
            href="/shop"
            className="rounded-md border border-gold/50 px-6 py-3 text-sm font-semibold text-gold-light transition hover:bg-gold/10"
          >
            Browse shop
          </Link>
        </div>
      </div>
    </section>
  ));

  return (
    <Carousel
      items={slides}
      autoPlayMs={6500}
      showDots
      ariaLabel="Homepage banners"
      className="[&>div:last-child]:absolute [&>div:last-child]:bottom-6 [&>div:last-child]:left-0 [&>div:last-child]:right-0 [&>div:last-child]:mt-0"
    />
  );
}
