import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { ShopToolbar } from "@/components/ShopToolbar";
import { collections, getCollection } from "@/lib/collections";
import { getProductsByCollection } from "@/lib/products";

type Props = {
  params: Promise<{ category: string }>;
};

export function generateStaticParams() {
  const params = collections.map((collection) => ({ category: collection.slug }));
  for (const collection of collections) {
    for (const alias of collection.aliases ?? []) {
      params.push({ category: alias });
    }
  }
  return params;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { category } = await params;
  const collection = getCollection(category);
  if (!collection) return { title: "Shop" };
  return { title: collection.title, description: collection.description };
}

export default async function CategoryPage({ params }: Props) {
  const { category } = await params;
  const collection = getCollection(category);
  if (!collection) notFound();

  if (category.toLowerCase() !== collection.slug) {
    redirect(`/shop/${collection.slug}`);
  }

  const list = getProductsByCollection(collection.slug);

  return (
    <div className="mx-auto max-w-site px-5 py-12 md:px-8 md:py-16">
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Shop", href: "/shop" },
          { label: collection.title },
        ]}
      />
      <h1 className="mt-4 font-display text-5xl text-ink">{collection.title}</h1>
      <p className="mt-4 max-w-xl text-base text-ink/70">{collection.description}</p>

      <div className="mt-8 flex flex-wrap gap-2">
        <Link
          href={`/shop/${collection.slug}`}
          className="rounded-full bg-gold px-4 py-2 text-sm font-semibold text-ink"
        >
          All
        </Link>
        {collection.children.map((child) => (
          <Link
            key={child.slug}
            href={`/shop/${collection.slug}/${child.slug}`}
            className="rounded-full border border-gold/40 px-4 py-2 text-sm font-medium text-ink/80 hover:bg-gold/15"
          >
            {child.title}
          </Link>
        ))}
      </div>

      <div className="mt-10">
        <ShopToolbar products={list} showCategoryFilter={false} />
      </div>
    </div>
  );
}
