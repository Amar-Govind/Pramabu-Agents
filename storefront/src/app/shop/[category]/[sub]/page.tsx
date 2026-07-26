import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { ShopToolbar } from "@/components/ShopToolbar";
import { collections, getSubCategory } from "@/lib/collections";
import { getProductsByCollection } from "@/lib/products";

type Props = {
  params: Promise<{ category: string; sub: string }>;
};

export function generateStaticParams() {
  const params: { category: string; sub: string }[] = [];
  for (const collection of collections) {
    for (const child of collection.children) {
      params.push({ category: collection.slug, sub: child.slug });
      for (const alias of child.aliases ?? []) {
        params.push({ category: collection.slug, sub: alias });
      }
    }
  }
  // Support legacy top-level aliases via redirects from category page;
  // also allow /shop/oils style via middleware-like redirects in category aliases.
  return params;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { category, sub } = await params;
  const matched = getSubCategory(category, sub);
  if (!matched) return { title: "Shop" };
  return {
    title: `${matched.sub.title} · ${matched.collection.title}`,
    description: matched.sub.description,
  };
}

export default async function SubCategoryPage({ params }: Props) {
  const { category, sub } = await params;
  const matched = getSubCategory(category, sub);
  if (!matched) notFound();

  const { collection, sub: child } = matched;

  if (category.toLowerCase() !== collection.slug || sub.toLowerCase() !== child.slug) {
    redirect(`/shop/${collection.slug}/${child.slug}`);
  }

  const list = getProductsByCollection(collection.slug, child.slug);

  return (
    <div className="mx-auto max-w-site px-5 py-12 md:px-8 md:py-16">
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Shop", href: "/shop" },
          { label: collection.title, href: `/shop/${collection.slug}` },
          { label: child.title },
        ]}
      />
      <p className="mt-4 text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">
        {collection.title}
      </p>
      <h1 className="mt-2 font-display text-5xl text-ink">{child.title}</h1>
      <p className="mt-4 max-w-xl text-base text-ink/70">{child.description}</p>

      <div className="mt-8 flex flex-wrap gap-2">
        <Link
          href={`/shop/${collection.slug}`}
          className="rounded-full border border-gold/40 px-4 py-2 text-sm font-medium text-ink/80 hover:bg-gold/15"
        >
          All
        </Link>
        {collection.children.map((item) => (
          <Link
            key={item.slug}
            href={`/shop/${collection.slug}/${item.slug}`}
            className={`rounded-full px-4 py-2 text-sm font-semibold ${
              item.slug === child.slug
                ? "bg-gold text-ink"
                : "border border-gold/40 text-ink/80 hover:bg-gold/15"
            }`}
          >
            {item.title}
          </Link>
        ))}
      </div>

      <div className="mt-10">
        <ShopToolbar products={list} showCategoryFilter={false} />
      </div>
    </div>
  );
}
