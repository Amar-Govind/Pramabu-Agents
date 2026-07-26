# Parambu Organics Storefront

Production-oriented Next.js storefront for [Parambu Organics](https://parambu.in).

## Stack

- Next.js (App Router) + TypeScript
- Tailwind CSS with **golden brand system**
- Zustand cart + wishlist
- Catalog seeded from live WooCommerce SKUs

## Brand

- Logo: `/public/brand/logo-gold.png` (from Parambu Golden Logo)
- Accent: `#C9A227` gold with deep forest supporting tones

## Run locally

```bash
cd storefront
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Included (current)

- Custom generated hero + sub-banner + category images
- Hero banner carousel, testimonial carousel, product carousels
- Icons across header, trust bars, cart, wishlist, checkout
- Visible favorite (wishlist) buttons on product cards
- Slide-over cart with shipping progress + checkout steps
- Stepped checkout flow: Cart → Details → Payment
- Product image gallery, recommended / also-bought
- Shop filters/sort

## Still next

- Live Razorpay keys + order webhooks
- Inventory/order sync
- Customer accounts + real review ingestion
