import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { AddToCartButton } from "@/components/AddToCartButton";
import { formatINR, getProduct, products } from "@/lib/products";

type Props = {
  params: Promise<{ slug: string }>;
};

export function generateStaticParams() {
  return products.map((product) => ({ slug: product.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const product = getProduct(slug);
  if (!product) return { title: "Product" };
  return {
    title: product.name,
    description: product.description.slice(0, 155),
  };
}

export default async function ProductPage({ params }: Props) {
  const { slug } = await params;
  const product = getProduct(slug);
  if (!product) notFound();

  return (
    <div className="mx-auto grid max-w-site gap-10 px-5 py-14 md:grid-cols-2 md:gap-14 md:px-8 md:py-20">
      <div className="relative aspect-[4/5] overflow-hidden bg-gradient-to-b from-mist to-sand animate-fade">
        {product.image ? (
          <Image
            src={product.image}
            alt={product.name}
            fill
            priority
            className="object-contain p-8"
            sizes="(max-width: 768px) 100vw, 50vw"
          />
        ) : null}
      </div>

      <div className="animate-rise">
        <Link
          href={`/shop/${product.category.toLowerCase()}`}
          className="text-xs font-semibold uppercase tracking-[0.18em] text-leaf"
        >
          {product.category}
        </Link>
        <h1 className="mt-3 font-display text-4xl text-ink md:text-5xl">{product.name}</h1>
        <p className="mt-4 text-lg text-ink/70">{product.tagline}</p>

        <div className="mt-6 flex items-baseline gap-3">
          <p className="text-2xl font-semibold text-forest">{formatINR(product.price)}</p>
          {product.regularPrice > product.price ? (
            <p className="text-sm text-ink/45 line-through">
              {formatINR(product.regularPrice)}
            </p>
          ) : null}
        </div>

        <p className="mt-8 text-base leading-relaxed text-ink/75">{product.description}</p>

        {product.benefits.length ? (
          <ul className="mt-8 space-y-2 border-t border-forest/15 pt-6 text-sm text-ink/80">
            {product.benefits.map((benefit) => (
              <li key={benefit} className="flex gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-moss" />
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        ) : null}

        <div className="mt-10 flex flex-wrap items-center gap-4">
          <AddToCartButton product={product} />
          <Link href="/cart" className="text-sm font-semibold text-forest underline-offset-4 hover:underline">
            View cart
          </Link>
        </div>
      </div>
    </div>
  );
}
