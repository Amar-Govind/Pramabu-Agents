import Image from "next/image";
import Link from "next/link";
import { ProductGrid } from "@/components/ProductGrid";
import { products } from "@/lib/products";

const heroImage =
  "https://parambu.in/wp-content/uploads/2026/01/Paramu_VirginCoconut_oil.png";

const featured = products.filter((product) =>
  ["virgin-coconut-oil", "neem-handcrafted-organic-soap", "coco-pith-low-ec-2", "rose-soap"].includes(
    product.slug
  )
);

export default function HomePage() {
  return (
    <>
      <section className="relative min-h-[92vh] overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(64,145,108,0.28),transparent_42%),linear-gradient(120deg,#1b4332_0%,#2d6a4f_48%,#1b4332_100%)]" />
          <div className="absolute inset-y-0 right-0 w-full md:w-[58%]">
            <Image
              src={heroImage}
              alt="Parambu Organics virgin coconut oil"
              fill
              priority
              className="object-contain object-right-bottom opacity-95 mix-blend-screen animate-drift md:object-center"
              sizes="(max-width: 768px) 100vw, 58vw"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-[#1b4332] via-[#1b4332]/55 to-transparent md:via-[#1b4332]/25" />
          </div>
        </div>

        <div className="relative mx-auto flex min-h-[92vh] max-w-site flex-col justify-center px-5 py-20 md:px-8">
          <p className="animate-rise font-display text-5xl leading-none text-sand sm:text-6xl md:text-7xl lg:text-8xl">
            Parambu Organics
          </p>
          <h1 className="animate-rise-delay mt-6 max-w-xl font-display text-3xl leading-tight text-sand/95 md:text-4xl">
            Everyday pure & natural.
          </h1>
          <p className="animate-rise-delay-2 mt-5 max-w-md text-base leading-relaxed text-sand/80 md:text-lg">
            Handcrafted soaps, cold-pressed coconut oil, and coco growing media
            for homes that choose clean living.
          </p>
          <div className="animate-rise-delay-2 mt-9 flex flex-wrap gap-3">
            <Link
              href="/shop"
              className="rounded-md bg-sand px-6 py-3 text-sm font-semibold text-forest transition hover:bg-white"
            >
              Shop essentials
            </Link>
            <Link
              href="/shop/soap"
              className="rounded-md border border-sand/40 px-6 py-3 text-sm font-semibold text-sand transition hover:border-sand hover:bg-sand/10"
            >
              Explore soaps
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-site px-5 py-20 md:px-8">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-leaf">
            Shop by category
          </p>
          <h2 className="mt-3 font-display text-4xl text-ink md:text-5xl">
            Oils. Soap. Gardening.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-ink/70">
            Three essentials for daily nourishment — skin, hair, and soil.
          </p>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            {
              href: "/shop/oils",
              title: "Oils",
              copy: "Cold processed virgin coconut oil for everyday wellness.",
            },
            {
              href: "/shop/soap",
              title: "Soap",
              copy: "Heritage herbal bars cured slowly for a gentle cleanse.",
            },
            {
              href: "/shop/gardening",
              title: "Gardening",
              copy: "Coco pith and chips that help plants hold moisture and thrive.",
            },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="border-t border-forest/20 pt-5 transition hover:border-leaf"
            >
              <h3 className="font-display text-3xl text-forest">{item.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink/70">{item.copy}</p>
            </Link>
          ))}
        </div>
      </section>

      <div className="leaf-rule mx-auto max-w-site" />

      <section className="mx-auto max-w-site px-5 py-20 md:px-8">
        <div className="mb-10 max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-leaf">
            Featured
          </p>
          <h2 className="mt-3 font-display text-4xl text-ink md:text-5xl">
            Start with these
          </h2>
        </div>
        <ProductGrid products={featured} />
      </section>
    </>
  );
}
