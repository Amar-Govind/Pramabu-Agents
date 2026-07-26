import productsData from "@/data/products.json";

export type Product = {
  id: number;
  slug: string;
  name: string;
  shortName: string;
  category: "Oils" | "Soap" | "Gardening" | string;
  price: number;
  regularPrice: number;
  image: string;
  images: string[];
  benefits: string[];
  description: string;
  tagline: string;
};

export const products = productsData as Product[];

export const categories = ["Oils", "Soap", "Gardening"] as const;

export function getProduct(slug: string): Product | undefined {
  return products.find((product) => product.slug === slug);
}

export function getProductsByCategory(category: string): Product[] {
  return products.filter(
    (product) => product.category.toLowerCase() === category.toLowerCase()
  );
}

export function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}
