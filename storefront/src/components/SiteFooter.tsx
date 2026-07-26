import Image from "next/image";
import Link from "next/link";
import { NewsletterForm } from "@/components/NewsletterForm";
import { collections } from "@/lib/collections";

export function SiteFooter() {
  return (
    <footer className="mt-20 border-t border-gold/25 bg-forest text-sand">
      <div className="mx-auto grid max-w-site gap-10 px-5 py-14 md:grid-cols-[1.2fr_1fr_1fr_1fr] md:px-8">
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
            Everyday pure & natural care — hair care, skin care, and gardening
            essentials for healthier homes.
          </p>
        </div>

        {collections.map((collection) => (
          <div key={collection.slug}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-light">
              {collection.title}
            </p>
            <div className="mt-4 flex flex-col gap-2 text-sm">
              <Link
                href={`/shop/${collection.slug}`}
                className="hover:text-gold-light"
              >
                All {collection.title}
              </Link>
              {collection.children.map((child) => (
                <Link
                  key={child.slug}
                  href={`/shop/${collection.slug}/${child.slug}`}
                  className="text-sand/75 hover:text-gold-light"
                >
                  {child.title}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mx-auto max-w-site px-5 pb-8 md:px-8">
        <div className="rounded-xl border border-sand/15 p-5 md:flex md:items-center md:justify-between">
          <p className="text-sm text-sand/80">Get natural living tips and new drops.</p>
          <div className="mt-3 md:mt-0 md:w-80">
            <NewsletterForm />
          </div>
        </div>
      </div>

      <div className="border-t border-sand/10 px-5 py-4 text-center text-xs text-sand/55 md:px-8">
        © {new Date().getFullYear()} Parambu Organics. All rights reserved.
      </div>
    </footer>
  );
}
