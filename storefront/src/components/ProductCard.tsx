import Image from "next/image";
import Link from "next/link";
import { AddToCartButton } from "@/components/AddToCartButton";
import { WishlistButton } from "@/components/WishlistButton";
import { IconStar } from "@/components/icons";
import { getSubCategoryForProductCategory } from "@/lib/collections";
import { discountPercent, formatINR, type Product } from "@/lib/products";

export function ProductCard({ product }: { product: Product }) {
  const discount = discountPercent(product);
  const matched = getSubCategoryForProductCategory(product.category);

  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-xl border border-forest/10 bg-white/70 shadow-soft">
      <div className="relative overflow-hidden bg-gradient-to-b from-mist to-sand">
        <Link href={`/product/${product.slug}`} className="block">
          <div className="relative aspect-[4/5]">
            {product.image ? (
              <Image
                src={product.image}
                alt={product.name}
                fill
                sizes="(max-width: 768px) 50vw, 25vw"
                className="object-contain p-4 transition duration-500 group-hover:scale-[1.04]"
              />
            ) : null}
          </div>
        </Link>
        <div className="pointer-events-none absolute left-3 top-3 z-20 flex flex-col gap-2">
          {discount ? (
            <span className="bg-gold px-2 py-1 text-[11px] font-bold text-ink shadow-soft">
              -{discount}%
            </span>
          ) : null}
        </div>
        <div className="absolute right-3 top-3 z-30">
          <WishlistButton slug={product.slug} />
        </div>
      </div>

      <div className="flex flex-1 flex-col p-4">
        <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-gold-deep">
          {matched
            ? `${matched.collection.title} · ${matched.sub.title}`
            : product.category}
        </p>
        <Link
          href={`/product/${product.slug}`}
          className="mt-1 font-display text-xl leading-snug text-ink hover:text-forest"
        >
          {product.shortName}
        </Link>
        <p className="mt-2 line-clamp-2 text-sm text-ink/65">{product.tagline}</p>
        <p className="mt-2 inline-flex items-center gap-1 text-xs text-ink/55">
          <IconStar className="h-3.5 w-3.5 text-gold" />
          {product.rating.toFixed(1)} · {product.reviewCount} reviews
        </p>
        <div className="mt-auto flex items-end justify-between gap-3 pt-4">
          <div>
            <p className="text-base font-semibold text-forest">{formatINR(product.price)}</p>
            {product.regularPrice > product.price ? (
              <p className="text-xs text-ink/40 line-through">
                {formatINR(product.regularPrice)}
              </p>
            ) : null}
          </div>
          <AddToCartButton product={product} className="px-3 py-2" />
        </div>
      </div>
    </article>
  );
}
