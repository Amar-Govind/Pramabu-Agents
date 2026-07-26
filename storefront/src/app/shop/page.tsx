import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { ShopToolbar } from "@/components/ShopToolbar";
import { products } from "@/lib/products";

export const metadata: Metadata = {
  title: "Shop",
  description: "Shop Parambu Organics oils, soaps, and gardening essentials.",
};

export default function ShopPage() {
  return (
    <div className="mx-auto max-w-site px-5 py-12 md:px-8 md:py-16">
      <Breadcrumbs items={[{ label: "Home", href: "/" }, { label: "Shop" }]} />
      <h1 className="mt-4 font-display text-5xl text-ink">All essentials</h1>
      <p className="mt-4 max-w-xl text-base text-ink/70">
        Pure heritage care across oils, handcrafted soaps, and natural growing media.
      </p>
      <div className="mt-10">
        <ShopToolbar products={products} />
      </div>
    </div>
  );
}
