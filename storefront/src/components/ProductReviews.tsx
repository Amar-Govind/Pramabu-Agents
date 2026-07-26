"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { StarRating } from "@/components/StarRating";
import {
  averageRating,
  getSeedReviews,
  type Review,
} from "@/lib/reviews";

const storageKey = (slug: string) => `parambu-reviews:${slug}`;

function readLocalReviews(slug: string): Review[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(storageKey(slug));
    if (!raw) return [];
    const parsed = JSON.parse(raw) as Review[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeLocalReviews(slug: string, reviews: Review[]) {
  window.localStorage.setItem(storageKey(slug), JSON.stringify(reviews));
}

export function ProductReviews({
  productSlug,
  fallbackRating,
  fallbackCount,
}: {
  productSlug: string;
  fallbackRating: number;
  fallbackCount: number;
}) {
  const seed = useMemo(() => getSeedReviews(productSlug), [productSlug]);
  const [localReviews, setLocalReviews] = useState<Review[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const [author, setAuthor] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [rating, setRating] = useState(5);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    setLocalReviews(readLocalReviews(productSlug));
    setHydrated(true);
  }, [productSlug]);

  const reviews = useMemo(
    () =>
      [...localReviews, ...seed].sort((a, b) =>
        a.createdAt < b.createdAt ? 1 : -1
      ),
    [localReviews, seed]
  );

  const avg = reviews.length ? averageRating(reviews) : fallbackRating;
  const count = reviews.length || fallbackCount;

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!author.trim() || !body.trim() || rating < 1) return;

    const review: Review = {
      id: `local-${Date.now()}`,
      productSlug,
      author: author.trim(),
      rating,
      title: title.trim() || "Customer review",
      body: body.trim(),
      createdAt: new Date().toISOString().slice(0, 10),
    };

    const next = [review, ...localReviews];
    setLocalReviews(next);
    writeLocalReviews(productSlug, next);
    setAuthor("");
    setTitle("");
    setBody("");
    setRating(5);
    setSubmitted(true);
  }

  return (
    <section id="reviews" className="mt-16 scroll-mt-28 border-t border-gold/20 pt-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">
            Reviews
          </p>
          <h2 className="mt-2 font-display text-3xl text-ink md:text-4xl">
            Customer ratings
          </h2>
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end gap-2">
            <StarRating value={avg} />
            <span className="text-lg font-semibold text-forest">{avg.toFixed(1)}</span>
          </div>
          <p className="mt-1 text-sm text-ink/55">
            {hydrated ? `${count} review${count === 1 ? "" : "s"}` : `${fallbackCount} reviews`}
          </p>
        </div>
      </div>

      <div className="mt-10 grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <ul className="space-y-5">
          {reviews.length ? (
            reviews.map((review) => (
              <li
                key={review.id}
                className="rounded-xl border border-gold/20 bg-white/70 p-5"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <StarRating value={review.rating} size="sm" />
                  <time className="text-xs text-ink/45" dateTime={review.createdAt}>
                    {review.createdAt}
                  </time>
                </div>
                <p className="mt-3 font-semibold text-ink">{review.title}</p>
                <p className="mt-2 text-sm leading-relaxed text-ink/70">{review.body}</p>
                <p className="mt-3 text-xs font-medium text-forest">{review.author}</p>
              </li>
            ))
          ) : (
            <li className="rounded-xl border border-dashed border-gold/30 bg-white/50 p-6 text-sm text-ink/60">
              No written reviews yet. Be the first to rate this product.
            </li>
          )}
        </ul>

        <form
          onSubmit={onSubmit}
          className="h-fit space-y-4 rounded-xl border border-gold/25 bg-white/80 p-5 md:p-6"
        >
          <h3 className="font-display text-2xl text-ink">Write a review</h3>
          <p className="text-sm text-ink/60">
            Share how this product worked for you. Reviews are saved on this device for the demo.
          </p>

          <div>
            <p className="mb-2 text-sm text-ink/70">Your rating</p>
            <StarRating value={rating} interactive onChange={setRating} size="lg" />
          </div>

          <label className="block text-sm">
            <span className="mb-1.5 block text-ink/70">Name</span>
            <input
              required
              value={author}
              onChange={(event) => setAuthor(event.target.value)}
              className="w-full rounded-md border border-forest/15 bg-white px-3 py-2.5 outline-none ring-gold focus:ring-2"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1.5 block text-ink/70">Title</span>
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Optional"
              className="w-full rounded-md border border-forest/15 bg-white px-3 py-2.5 outline-none ring-gold focus:ring-2"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1.5 block text-ink/70">Review</span>
            <textarea
              required
              rows={4}
              value={body}
              onChange={(event) => setBody(event.target.value)}
              className="w-full resize-y rounded-md border border-forest/15 bg-white px-3 py-2.5 outline-none ring-gold focus:ring-2"
            />
          </label>

          <button
            type="submit"
            className="w-full rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink hover:bg-gold-light"
          >
            Submit review
          </button>
          {submitted ? (
            <p className="text-xs text-forest">Thanks — your review was added.</p>
          ) : null}
        </form>
      </div>
    </section>
  );
}
