"use client";

import { IconHeart } from "@/components/icons";
import { useWishlist } from "@/store/wishlist";

export function WishlistButton({
  slug,
  className = "",
}: {
  slug: string;
  className?: string;
}) {
  const slugs = useWishlist((state) => state.slugs);
  const toggle = useWishlist((state) => state.toggle);
  const active = slugs.includes(slug);

  return (
    <button
      type="button"
      aria-label={active ? "Remove from wishlist" : "Add to wishlist"}
      onClick={(event) => {
        event.preventDefault();
        event.stopPropagation();
        toggle(slug);
      }}
      className={`relative z-20 inline-flex h-10 w-10 items-center justify-center rounded-full border shadow-soft transition ${
        active
          ? "border-gold bg-gold text-ink"
          : "border-gold/50 bg-white text-gold-deep hover:bg-gold hover:text-ink"
      } ${className}`}
    >
      <IconHeart className="h-[18px] w-[18px]" filled={active} />
    </button>
  );
}
