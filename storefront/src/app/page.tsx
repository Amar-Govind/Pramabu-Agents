import Image from "next/image";
import Link from "next/link";
import { HeroCarousel } from "@/components/HeroCarousel";
import { ProductCarousel } from "@/components/ProductCarousel";
import { TestimonialCarousel } from "@/components/TestimonialCarousel";
import {
  IconLeaf,
  IconShield,
  IconSpark,
  IconTruck,
} from "@/components/icons";
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

const recommended = products.filter((product) =>
  [
    "manjistha-soap",
    "coconut-oil-soap",
    "nalangu-maavu-soap",
    "coco-pith-high-ec-2",
    "green-gram-soap",
    "vetpalai-soap",
  ].includes(product.slug)
);

export default function HomePage() {
  const subBanners = site.banners.slice(1);

  return (
    <>
      <HeroCarousel />

      <section className="mx-auto max-w-site px-5 py-14 md:px-8">
        <div className="grid gap-4 md:grid-cols-3">
          {[
            { icon: IconLeaf, text: "Handcrafted & cold-processed" },
            { icon: IconSpark, text: "Pure heritage botanicals" },
            { icon: IconShield, text: "Trusted by Indian homes" },
          ].map(({ icon: Icon, text }) => (
            <div key={text} className="flex items-start gap-3 border-t-2 border-gold pt-4">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-gold/15 text-gold-deep">
                <Icon />
              </span>
              <p className="pt-2 text-sm font-semibold text-forest">{text}</p>
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
            Hair Care. Skin Care. Gardening.
          </h2>
        </div>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {site.categoryTiles.map((tile) => (
            <Link key={tile.href} href={tile.href} className="group overflow-hidden rounded-xl">
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
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">
              Spotlight
            </p>
            <h2 className="mt-2 font-display text-4xl text-ink">Seasonal picks</h2>
          </div>
        </div>
        <div className="grid gap-5 md:grid-cols-3">
          {subBanners.map((banner) => (
            <Link
              key={banner.href + banner.title}
              href={banner.href}
              className="group relative min-h-[260px] overflow-hidden rounded-xl"
            >
              <Image
                src={banner.image}
                alt={banner.title}
                fill
                className="object-cover transition duration-500 group-hover:scale-[1.03]"
                sizes="(max-width: 768px) 100vw, 33vw"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-forest/90 via-forest/35 to-transparent" />
              <div className="relative flex h-full min-h-[260px] flex-col justify-end p-5">
                <h3 className="font-display text-2xl text-gold-light">{banner.title}</h3>
                <p className="mt-2 text-sm text-sand/85">{banner.subtitle}</p>
                <span className="mt-4 inline-flex w-fit rounded-md bg-gold px-3 py-2 text-xs font-semibold text-ink">
                  {banner.cta}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <div className="gold-rule mx-auto max-w-site" />

      <section className="mx-auto max-w-site px-5 py-16 md:px-8">
        <ProductCarousel
          title="Bestsellers"
          subtitle="Loved by families and gardeners."
          products={featured}
        />
        <ProductCarousel
          title="Recommended for you"
          subtitle="Curated next picks based on popular Parambu routines."
          products={recommended}
        />
      </section>

      <section className="bg-forest py-16 text-sand">
        <div className="mx-auto max-w-site px-5 md:px-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-light">
            Testimonials
          </p>
          <h2 className="mt-3 font-display text-4xl text-gold-light">What customers say</h2>
          <div className="mt-10">
            <TestimonialCarousel />
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            {[
              { icon: IconTruck, text: "Pan-India shipping" },
              { icon: IconShield, text: "Secure payments" },
              { icon: IconLeaf, text: "Pure & natural care" },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3 rounded-lg border border-gold/30 px-4 py-3">
                <Icon className="text-gold-light" />
                <span className="text-sm font-medium">{text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
