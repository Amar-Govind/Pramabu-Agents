import Image from "next/image";
import Link from "next/link";
import { NewsletterForm } from "@/components/NewsletterForm";
import { collections } from "@/lib/collections";

export function SiteFooter() {
  return (
    <footer className="mt-20 border-t border-gold/25 bg-forest text-sand">
      <div className="mx-auto grid max-w-site gap-10 px-5 py-14 md:grid-cols-[1.3fr_1fr_1fr_1fr] md:px-8">
        <div>
          <div className="flex items-center gap-3">
            <Image
              src="/brand/logo-gold.png"
              alt="Parambu Organics"
              width={48}
              height={48}
              className="h-12 w-12 object-contain"
            />
            <p className="font-display text-3xl text-gold-light">Parambu Organics</p>
          </div>
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-sand/80">
            Everyday pure & natural care — hair care oils, skin care soaps,
            and cocopeat for healthier homes and gardens.
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-light">Shop</p>
          <div className="mt-4 flex flex-col gap-2 text-sm">
            <Link href="/shop" className="hover:text-gold-light">All products</Link>
            {collections.map((collection) => (
              <Link
                key={collection.slug}
                href={`/shop/${collection.slug}`}
                className="hover:text-gold-light"
              >
                {collection.title}
                <span className="ml-1 text-sand/50">({collection.shortLabel})</span>
              </Link>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-light">Help</p>
          <div className="mt-4 flex flex-col gap-2 text-sm text-sand/80">
            <span>Shipping across India</span>
            <span>Secure payments</span>
            <span>Easy support via WhatsApp</span>
            <a href="https://parambu.in" className="hover:text-gold-light" target="_blank" rel="noreferrer">
              Live store: parambu.in
            </a>
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-light">Stay close</p>
          <p className="mt-4 text-sm text-sand/80">
            Get natural living tips and new drops.
          </p>
          <NewsletterForm />
        </div>
      </div>
      <div className="border-t border-sand/10 px-5 py-4 text-center text-xs text-sand/55 md:px-8">
        © {new Date().getFullYear()} Parambu Organics. All rights reserved.
      </div>
    </footer>
  );
}
