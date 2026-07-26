import Image from "next/image";
import Link from "next/link";
import { ProductGrid } from "@/components/ProductGrid";
import { products } from "@/lib/products";
import { site } from "@/lib/site";

const featured = products.filter((product) =>
  [
    "virgin-coconut-oil",
    "neem-handcrafted-organic-soap",
    "rose-soap",
    "coco-pith-low-ec-2",
    "charcoal-soap",
    "vetpalai-soap",
    "coco-chips-low-ec-2",
    "green-gram-soap",
  ].includes(product.slug)
);

export default function HomePage() {
  const [hero, ...restBanners] = site.banners;

  return (
    <>
      <section className="relative min-h-[92vh] overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src={hero.image}
            alt={hero.title}
            fill
            priority
            className="object-cover"
            sizes="100vw"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-forest via-forest/80 to-forest/25" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(201,162,39,0.28),transparent_40%)]" />
        </div>

        <div className="relative mx-auto flex min-h-[92vh] max-w-site flex-col justify-center px-5 py-20 md:px-8">
          <Image
            src={site.logo}
            alt="Parambu Organics golden logo"
            width={88}
            height={88}
            className="animate-rise h-20 w-20 object-contain md:h-24 md:w-24"
            priority
          />
          <p className="animate-rise mt-5 font-display text-5xl leading-none text-gold-light sm:text-6xl md:text-7xl lg:text-8xl">
            Parambu Organics
          </p>
          <h1 className="animate-rise-delay mt-6 max-w-xl font-display text-3xl leading-tight text-sand md:text-4xl">
            {site.tagline}.
          </h1>
          <p className="animate-rise-delay-2 mt-5 max-w-md text-base leading-relaxed text-sand/85 md:text-lg">
            {hero.subtitle}
          </p>
          <div className="animate-rise-delay-2 mt-9 flex flex-wrap gap-3">
            <Link
              href="/shop"
              className="rounded-md bg-gold px-6 py-3 text-sm font-semibold text-ink transition hover:bg-gold-light"
            >
              Shop essentials
            </Link>
            <Link
              href={hero.href}
              className="rounded-md border border-gold/50 px-6 py-3 text-sm font-semibold text-gold-light transition hover:bg-gold/10"
            >
              {hero.cta}
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-site px-5 py-14 md:px-8">
        <div className="grid gap-4 md:grid-cols-3">
          {[
            "Handcrafted & cold-processed",
            "Pure heritage botanicals",
            "Trusted by Indian homes",
          ].map((item) => (
            <div key={item} className="border-t-2 border-gold pt-4 text-sm font-semibold text-forest">
              {item}
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-site px-5 pb-8 md:px-8">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">
            Shop by category
          </p>
          <h2 className="mt-3 font-display text-4xl text-ink md:text-5xl">
            Oils. Soap. Gardening.
          </h2>
        </div>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {site.categoryTiles.map((tile) => (
            <Link key={tile.href} href={tile.href} className="group overflow-hidden">
              <div className="relative aspect-[4/5] bg-mist">
                <Image
                  src={tile.image}
                  alt={tile.title}
                  fill
                  className="object-cover transition duration-500 group-hover:scale-[1.03]"
                  sizes="(max-width: 768px) 100vw, 33vw"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-forest/85 via-forest/20 to-transparent" />
                <div className="absolute inset-x-0 bottom-0 p-5">
                  <h3 className="font-display text-3xl text-gold-light">{tile.title}</h3>
                  <p className="mt-2 text-sm text-sand/85">{tile.copy}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-site px-5 py-10 md:px-8">
        <div className="grid gap-5 md:grid-cols-2">
          {restBanners.map((banner) => (
            <Link key={banner.href} href={banner.href} className="group relative min-h-[280px] overflow-hidden">
              <Image
                src={banner.image}
                alt={banner.title}
                fill
                className="object-cover transition duration-500 group-hover:scale-[1.03]"
                sizes="(max-width: 768px) 100vw, 50vw"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-forest/85 to-forest/20" />
              <div className="relative flex h-full min-h-[280px] flex-col justify-end p-6 md:p-8">
                <h3 className="font-display text-3xl text-gold-light">{banner.title}</h3>
                <p className="mt-2 max-w-sm text-sm text-sand/85">{banner.subtitle}</p>
                <span className="mt-5 inline-flex w-fit rounded-md bg-gold px-4 py-2 text-sm font-semibold text-ink">
                  {banner.cta}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <div className="gold-rule mx-auto max-w-site" />

      <section className="mx-auto max-w-site px-5 py-20 md:px-8">
        <div className="mb-10 max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">
            Bestsellers
          </p>
          <h2 className="mt-3 font-display text-4xl text-ink md:text-5xl">
            Loved by families & gardeners
          </h2>
        </div>
        <ProductGrid products={featured} />
      </section>

      <section className="bg-forest py-16 text-sand">
        <div className="mx-auto max-w-site px-5 md:px-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-light">
            Testimonials
          </p>
          <h2 className="mt-3 font-display text-4xl text-gold-light">What customers say</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {site.testimonials.map((item) => (
              <blockquote key={item.name} className="border-t border-gold/40 pt-5">
                <p className="text-sm leading-relaxed text-sand/85">“{item.quote}”</p>
                <footer className="mt-4 text-sm font-semibold text-gold-light">{item.name}</footer>
              </blockquote>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
