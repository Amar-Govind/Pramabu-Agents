"use client";

import Image from "next/image";
import { useState } from "react";
import type { ProductImage } from "@/lib/products";

export function ProductGallery({
  images,
  name,
}: {
  images: ProductImage[];
  name: string;
}) {
  const gallery = images.length
    ? images
    : [{ src: "/brand/logo-gold.png", alt: name }];
  const [active, setActive] = useState(0);
  const current = gallery[Math.min(active, gallery.length - 1)];

  return (
    <div>
      <div className="relative aspect-[4/5] overflow-hidden bg-gradient-to-b from-mist to-sand">
        <Image
          key={current.src}
          src={current.src}
          alt={current.alt || name}
          fill
          priority
          className="object-contain p-6 animate-fade"
          sizes="(max-width: 768px) 100vw, 50vw"
        />
      </div>
      {gallery.length > 1 ? (
        <div className="mt-4 grid grid-cols-4 gap-3 sm:grid-cols-5">
          {gallery.map((image, index) => (
            <button
              key={`${image.src}-${index}`}
              type="button"
              onClick={() => setActive(index)}
              className={`relative aspect-square overflow-hidden border transition ${
                index === active
                  ? "border-gold ring-1 ring-gold"
                  : "border-forest/10 hover:border-gold/60"
              }`}
              aria-label={`View image ${index + 1}`}
            >
              <Image
                src={image.src}
                alt={image.alt || `${name} ${index + 1}`}
                fill
                className="object-contain p-1.5"
                sizes="96px"
              />
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
