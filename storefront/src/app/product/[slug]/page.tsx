import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { AlsoBought } from "@/components/AlsoBought";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { ProductGallery } from "@/components/ProductGallery";
import { ProductPurchasePanel } from "@/components/ProductPurchasePanel";
import { ProductRail } from "@/components/ProductRail";
import {
  getProduct,
  getProductsBySlugs,
  products,
} from "@/lib/products";

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

  const recommended = getProductsBySlugs(product.recommended);
  const alsoBought = getProductsBySlugs(product.alsoBought);

  return (
    <div className="mx-auto max-w-site px-5 py-12 md:px-8 md:py-16">
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Shop", href: "/shop" },
          { label: product.category, href: `/shop/${product.category.toLowerCase()}` },
          { label: product.shortName },
        ]}
      />

      <div className="mt-8 grid gap-10 md:grid-cols-2 md:gap-14">
        <ProductGallery images={product.images} name={product.name} />

        <div className="animate-rise">
          <Link
            href={`/shop/${product.category.toLowerCase()}`}
            className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep"
          >
            {product.category}
          </Link>
          <h1 className="mt-3 font-display text-4xl text-ink md:text-5xl">{product.name}</h1>
          <p className="mt-4 text-lg text-ink/70">{product.tagline}</p>

          <div className="mt-8">
            <ProductPurchasePanel product={product} />
          </div>

          <p className="mt-8 text-base leading-relaxed text-ink/75">{product.description}</p>

          {product.benefits.length ? (
            <ul className="mt-8 space-y-2 border-t border-gold/20 pt-6 text-sm text-ink/80">
              {product.benefits.map((benefit) => (
                <li key={benefit} className="flex gap-2">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-gold" />
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </div>

      <AlsoBought product={product} related={alsoBought} />

      <ProductRail
        title="Recommended for you"
        subtitle="Similar picks based on this product."
        products={recommended}
      />
    </div>
  );
}
