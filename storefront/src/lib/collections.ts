export type SubCategory = {
  slug: string;
  title: string;
  description: string;
  productCategory: string;
  aliases?: string[];
};

export type Collection = {
  slug: string;
  title: string;
  description: string;
  productCategories: string[];
  aliases?: string[];
  image: string;
  copy: string;
  children: SubCategory[];
};

export const collections: Collection[] = [
  {
    slug: "hair-care",
    title: "Hair Care",
    description: "Nourishing hair essentials rooted in pure coconut care.",
    productCategories: ["Oils"],
    aliases: ["hair"],
    image: "/categories/category-oils.png",
    copy: "Oils and more for soft, nourished hair",
    children: [
      {
        slug: "oils",
        title: "Oils",
        description: "Cold processed virgin coconut oil for hair and everyday wellness.",
        productCategory: "Oils",
        aliases: ["oil"],
      },
      // Future Hair Care items can be added here
    ],
  },
  {
    slug: "skin-care",
    title: "Skin Care",
    description: "Gentle daily care crafted with heritage botanicals.",
    productCategories: ["Soap"],
    aliases: ["skin"],
    image: "/categories/category-soap.png",
    copy: "Soaps and more for gentle daily skin care",
    children: [
      {
        slug: "soap",
        title: "Soap",
        description: "Handcrafted organic soaps inspired by heritage botanicals.",
        productCategory: "Soap",
        aliases: ["soaps"],
      },
      // Future Skin Care items can be added here
    ],
  },
  {
    slug: "gardening",
    title: "Gardening",
    description: "Natural growing media for healthier plants and terrace gardens.",
    productCategories: ["Gardening"],
    aliases: ["garden"],
    image: "/categories/category-gardening.png",
    copy: "Cocopeat and more for thriving gardens",
    children: [
      {
        slug: "cocopeat",
        title: "Cocopeat",
        description: "Coco pith and coco chips for moisture-rich, healthy plant growth.",
        productCategory: "Gardening",
        aliases: ["coco", "coco-peat", "coco-pith"],
      },
      // Future Gardening items can be added here
    ],
  },
];

export function getCollection(slug: string): Collection | undefined {
  const key = slug.toLowerCase();
  return collections.find(
    (collection) =>
      collection.slug === key || collection.aliases?.includes(key)
  );
}

export function getSubCategory(
  collectionSlug: string,
  subSlug: string
): { collection: Collection; sub: SubCategory } | undefined {
  const collection = getCollection(collectionSlug);
  if (!collection) return undefined;
  const key = subSlug.toLowerCase();
  const sub = collection.children.find(
    (child) => child.slug === key || child.aliases?.includes(key)
  );
  if (!sub) return undefined;
  return { collection, sub };
}

export function getCollectionForProductCategory(category: string): Collection | undefined {
  const key = category.toLowerCase();
  return collections.find((collection) =>
    collection.children.some(
      (child) => child.productCategory.toLowerCase() === key
    ) ||
    collection.productCategories.some((item) => item.toLowerCase() === key)
  );
}

export function getSubCategoryForProductCategory(
  category: string
): { collection: Collection; sub: SubCategory } | undefined {
  const key = category.toLowerCase();
  for (const collection of collections) {
    const sub = collection.children.find(
      (child) => child.productCategory.toLowerCase() === key
    );
    if (sub) return { collection, sub };
  }
  return undefined;
}
