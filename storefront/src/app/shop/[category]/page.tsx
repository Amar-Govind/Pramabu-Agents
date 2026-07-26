import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ProductGrid } from "@/components/ProductGrid";
import { categories, getProductsByCategory } from "@/lib/products";

type Props = {
  params: Promise<{ category: string }>;
};

const copy: Record<string, { title: string; description: string }> = {
  oils: {
    title: "Oils",
    description: "Cold processed virgin coconut oil for skin, hair, and daily wellness.",
  },
  soap: {
    title: "Soap",
    description: "Handcrafted organic bars inspired by heritage botanicals.",
  },
  gardening: {
    title: "Gardening",
    description: "Coco pith and coco chips for moisture-rich, healthy plant growth.",
  },
};

export function generateStaticParams() {
  return categories.map((category) => ({ category: category.toLowerCase() }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { category } = await params;
  const meta = copy[category.toLowerCase()];
  if (!meta) return { title: "Shop" };
  return { title: meta.title, description: meta.description };
}

export default async function CategoryPage({ params }: Props) {
  const { category } = await params;
  const key = category.toLowerCase();
  const meta = copy[key];
  if (!meta) notFound();

  const list = getProductsByCategory(meta.title);

  return (
    <div className="mx-auto max-w-site px-5 py-14 md:px-8 md:py-20">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-leaf">Category</p>
      <h1 className="mt-3 font-display text-5xl text-ink">{meta.title}</h1>
      <p className="mt-4 max-w-xl text-base text-ink/70">{meta.description}</p>
      <div className="mt-12">
        <ProductGrid products={list} />
      </div>
    </div>
  );
}
