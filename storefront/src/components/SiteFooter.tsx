import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="mt-20 border-t border-forest/10 bg-forest text-sand">
      <div className="mx-auto grid max-w-site gap-10 px-5 py-14 md:grid-cols-[1.4fr_1fr_1fr] md:px-8">
        <div>
          <p className="font-display text-3xl">Parambu Organics</p>
          <p className="mt-3 max-w-sm text-sm leading-relaxed text-sand/80">
            Everyday pure & natural care — handcrafted soaps, cold-pressed oils,
            and coco growing media for healthier homes and gardens.
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sand/60">
            Shop
          </p>
          <div className="mt-4 flex flex-col gap-2 text-sm">
            <Link href="/shop/oils" className="hover:text-white">
              Oils
            </Link>
            <Link href="/shop/soap" className="hover:text-white">
              Soap
            </Link>
            <Link href="/shop/gardening" className="hover:text-white">
              Gardening
            </Link>
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sand/60">
            Note
          </p>
          <p className="mt-4 text-sm leading-relaxed text-sand/80">
            Custom storefront MVP. Checkout comes next. Live store remains at{" "}
            <a
              href="https://parambu.in"
              className="underline decoration-sand/40 underline-offset-4 hover:text-white"
              target="_blank"
              rel="noreferrer"
            >
              parambu.in
            </a>
            .
          </p>
        </div>
      </div>
    </footer>
  );
}
