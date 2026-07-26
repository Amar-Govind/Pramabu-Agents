export type Collection = {
  slug: string;
  title: string;
  shortLabel: string;
  description: string;
  productCategories: string[];
  aliases?: string[];
  image: string;
  copy: string;
};

export const collections: Collection[] = [
  {
    slug: "hair-care",
    title: "Hair Care",
    shortLabel: "Oils",
    description: "Cold processed virgin coconut oil for hair and everyday wellness.",
    productCategories: ["Oils"],
    aliases: ["oils", "oil"],
    image: "/categories/category-oils.png",
    copy: "Oils for soft, nourished hair",
  },
  {
    slug: "skin-care",
    title: "Skin Care",
    shortLabel: "Soap",
    description: "Handcrafted organic soaps inspired by heritage botanicals.",
    productCategories: ["Soap"],
    aliases: ["soap", "soaps"],
    image: "/categories/category-soap.png",
    copy: "Soaps for gentle daily skin care",
  },
  {
    slug: "gardening",
    title: "Gardening",
    shortLabel: "Cocopeat",
    description: "Coco pith and coco chips for moisture-rich, healthy plant growth.",
    productCategories: ["Gardening"],
    aliases: ["coco", "cocopeat", "coco-peat"],
    image: "/categories/category-gardening.png",
    copy: "Cocopeat for thriving gardens",
  },
];

export function getCollection(slug: string): Collection | undefined {
  const key = slug.toLowerCase();
  return collections.find(
    (collection) =>
      collection.slug === key || collection.aliases?.includes(key)
  );
}

export function getCollectionForProductCategory(category: string): Collection | undefined {
  const key = category.toLowerCase();
  return collections.find((collection) =>
    collection.productCategories.some((item) => item.toLowerCase() === key)
  );
}
