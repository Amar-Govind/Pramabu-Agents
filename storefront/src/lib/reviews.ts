import reviewsData from "@/data/reviews.json";

export type Review = {
  id: string;
  productSlug: string;
  author: string;
  rating: number;
  title: string;
  body: string;
  createdAt: string;
};

export const seedReviews = reviewsData as Review[];

export function getSeedReviews(productSlug: string): Review[] {
  return seedReviews
    .filter((review) => review.productSlug === productSlug)
    .sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
}

export function averageRating(reviews: Review[]): number {
  if (!reviews.length) return 0;
  const sum = reviews.reduce((total, review) => total + review.rating, 0);
  return Math.round((sum / reviews.length) * 10) / 10;
}
