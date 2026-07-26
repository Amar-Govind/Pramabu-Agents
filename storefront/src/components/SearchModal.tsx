"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { formatINR, searchProducts } from "@/lib/products";
import { useUI } from "@/store/ui";

export function SearchModal() {
  const open = useUI((state) => state.searchOpen);
  const closeSearch = useUI((state) => state.closeSearch);
  const [query, setQuery] = useState("");

  const results = useMemo(() => searchProducts(query).slice(0, 8), [query]);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeSearch();
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [open, closeSearch]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[70]">
      <button type="button" className="absolute inset-0 bg-ink/45" aria-label="Close search" onClick={closeSearch} />
      <div className="relative mx-auto mt-16 w-[min(720px,92vw)] rounded-xl bg-[#fffaf0] p-5 shadow-soft animate-rise">
        <input
          autoFocus
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search soaps, oils, gardening..."
          className="w-full rounded-md border border-gold/30 bg-white px-4 py-3 text-sm outline-none ring-gold focus:ring-2"
        />
        <ul className="mt-4 max-h-[50vh] space-y-2 overflow-y-auto">
          {results.map((product) => (
            <li key={product.slug}>
              <Link
                href={`/product/${product.slug}`}
                onClick={closeSearch}
                className="flex items-center gap-3 rounded-md p-2 hover:bg-mist"
              >
                <span className="relative h-12 w-12 overflow-hidden bg-mist">
                  {product.image ? (
                    <Image src={product.image} alt={product.shortName} fill className="object-contain p-1" sizes="48px" />
                  ) : null}
                </span>
                <span className="flex-1">
                  <span className="block text-sm font-medium text-ink">{product.shortName}</span>
                  <span className="block text-xs text-ink/55">{product.category}</span>
                </span>
                <span className="text-sm font-semibold text-forest">{formatINR(product.price)}</span>
              </Link>
            </li>
          ))}
          {!results.length ? <li className="p-3 text-sm text-ink/60">No matches found.</li> : null}
        </ul>
      </div>
    </div>
  );
}
