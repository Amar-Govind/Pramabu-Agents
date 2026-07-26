"use client";

import { useMemo, useState } from "react";
import { ProductGrid } from "@/components/ProductGrid";
import { collections } from "@/lib/collections";
import type { Product } from "@/lib/products";

type SortKey = "featured" | "price-asc" | "price-desc" | "name";

export function ShopToolbar({
  products,
  showCategoryFilter = true,
}: {
  products: Product[];
  showCategoryFilter?: boolean;
}) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [sort, setSort] = useState<SortKey>("featured");

  const filtered = useMemo(() => {
    let list = [...products];
    if (category !== "all") {
      const [parent, child] = category.split("/");
      const collection = collections.find((item) => item.slug === parent);
      if (collection) {
        if (child) {
          const sub = collection.children.find((item) => item.slug === child);
          if (sub) {
            list = list.filter(
              (product) =>
                product.category.toLowerCase() === sub.productCategory.toLowerCase()
            );
          }
        } else {
          list = list.filter((product) =>
            collection.productCategories.some(
              (item) => item.toLowerCase() === product.category.toLowerCase()
            )
          );
        }
      }
    }
    if (query.trim()) {
      const q = query.toLowerCase();
      list = list.filter((product) =>
        `${product.name} ${product.tagline} ${product.category}`.toLowerCase().includes(q)
      );
    }
    switch (sort) {
      case "price-asc":
        list.sort((a, b) => a.price - b.price);
        break;
      case "price-desc":
        list.sort((a, b) => b.price - a.price);
        break;
      case "name":
        list.sort((a, b) => a.shortName.localeCompare(b.shortName));
        break;
      default:
        break;
    }
    return list;
  }, [products, category, query, sort]);

  return (
    <div>
      <div className="flex flex-col gap-3 rounded-xl border border-gold/20 bg-white/70 p-4 md:flex-row md:items-center md:justify-between">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Filter products..."
          className="w-full rounded-md border border-forest/15 bg-white px-3 py-2 text-sm outline-none ring-gold focus:ring-2 md:max-w-xs"
        />
        <div className="flex flex-wrap gap-2">
          {showCategoryFilter ? (
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="rounded-md border border-forest/15 bg-white px-3 py-2 text-sm"
            >
              <option value="all">All categories</option>
              {collections.map((collection) => (
                <optgroup key={collection.slug} label={collection.title}>
                  <option value={collection.slug}>All {collection.title}</option>
                  {collection.children.map((child) => (
                    <option
                      key={`${collection.slug}-${child.slug}`}
                      value={`${collection.slug}/${child.slug}`}
                    >
                      {child.title}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          ) : null}
          <select
            value={sort}
            onChange={(event) => setSort(event.target.value as SortKey)}
            className="rounded-md border border-forest/15 bg-white px-3 py-2 text-sm"
          >
            <option value="featured">Featured</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
            <option value="name">Name A–Z</option>
          </select>
        </div>
      </div>
      <p className="mt-4 text-sm text-ink/55">{filtered.length} products</p>
      <div className="mt-6">
        <ProductGrid products={filtered} />
      </div>
    </div>
  );
}
