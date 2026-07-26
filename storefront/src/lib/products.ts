import productsData from "@/data/products.json";
import {
  getCollection,
  getCollectionForProductCategory,
  getSubCategory,
} from "@/lib/collections";

export type ProductImage = {
  src: string;
  alt: string;
};

export type Product = {
  id: number;
  slug: string;
  name: string;
  shortName: string;
  category: string;
  price: number;
  regularPrice: number;
  image: string;
  images: ProductImage[];
  benefits: string[];
  description: string;
  tagline: string;
  inStock: boolean;
  rating: number;
  reviewCount: number;
  recommended: string[];
  alsoBought: string[];
};

export const products = productsData as Product[];

export function getProduct(slug: string): Product | undefined {
  return products.find((product) => product.slug === slug);
}

export function getProductsByCategory(category: string): Product[] {
  return products.filter(
    (product) => product.category.toLowerCase() === category.toLowerCase()
  );
}

export function getProductsByCollection(slug: string, subSlug?: string): Product[] {
  if (subSlug) {
    const matched = getSubCategory(slug, subSlug);
    if (!matched) return [];
    return getProductsByCategory(matched.sub.productCategory);
  }

  const collection = getCollection(slug);
  if (!collection) return [];
  return products.filter((product) =>
    collection.productCategories.some(
      (category) => category.toLowerCase() === product.category.toLowerCase()
    )
  );
}

export function getProductsBySlugs(slugs: string[]): Product[] {
  return slugs
    .map((slug) => getProduct(slug))
    .filter((product): product is Product => Boolean(product));
}

export function searchProducts(query: string): Product[] {
  const q = query.trim().toLowerCase();
  if (!q) return products;
  return products.filter((product) => {
    const collection = getCollectionForProductCategory(product.category);
    const childTitles =
      collection?.children.map((child) => child.title).join(" ") ?? "";
    return [
      product.name,
      product.shortName,
      product.category,
      collection?.title ?? "",
      childTitles,
      product.tagline,
      product.description,
    ]
      .join(" ")
      .toLowerCase()
      .includes(q);
  });
}

export function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function discountPercent(product: Product): number | null {
  if (product.regularPrice <= product.price) return null;
  return Math.round(((product.regularPrice - product.price) / product.regularPrice) * 100);
}
