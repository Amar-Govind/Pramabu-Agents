import Image from "next/image";
import Link from "next/link";
import { formatINR, type Product } from "@/lib/products";
import { AddToCartButton } from "@/components/AddToCartButton";

export function ProductCard({ product }: { product: Product }) {
  return (
    <article className="group flex flex-col">
      <Link href={`/product/${product.slug}`} className="block overflow-hidden">
        <div className="relative aspect-[4/5] bg-gradient-to-b from-mist to-sand">
          {product.image ? (
            <Image
              src={product.image}
              alt={product.name}
              fill
              sizes="(max-width: 768px) 50vw, 25vw"
              className="object-contain p-4 transition duration-500 group-hover:scale-[1.03]"
            />
          ) : null}
        </div>
      </Link>
      <div className="mt-4 flex flex-1 flex-col">
        <p className="text-xs uppercase tracking-[0.16em] text-leaf">{product.category}</p>
        <Link href={`/product/${product.slug}`} className="mt-1 font-display text-xl text-ink">
          {product.shortName}
        </Link>
        <p className="mt-2 text-sm text-ink/70">{product.tagline}</p>
        <div className="mt-auto flex items-end justify-between gap-3 pt-4">
          <div>
            <p className="text-base font-semibold text-forest">{formatINR(product.price)}</p>
            {product.regularPrice > product.price ? (
              <p className="text-xs text-ink/45 line-through">
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
