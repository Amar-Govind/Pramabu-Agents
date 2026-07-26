"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Product } from "@/lib/products";

export type CartItem = {
  product: Product;
  quantity: number;
};

type CartState = {
  items: CartItem[];
  couponCode: string | null;
  isOpen: boolean;
  openCart: () => void;
  closeCart: () => void;
  toggleCart: () => void;
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (slug: string) => void;
  setQuantity: (slug: string, quantity: number) => void;
  increment: (slug: string) => void;
  decrement: (slug: string) => void;
  setCouponCode: (code: string | null) => void;
  clearCoupon: () => void;
  clear: () => void;
};

export const useCart = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      couponCode: null,
      isOpen: false,
      openCart: () => set({ isOpen: true }),
      closeCart: () => set({ isOpen: false }),
      toggleCart: () => set({ isOpen: !get().isOpen }),
      addItem: (product, quantity = 1) => {
        set((state) => {
          const existing = state.items.find((item) => item.product.slug === product.slug);
          if (existing) {
            return {
              isOpen: true,
              items: state.items.map((item) =>
                item.product.slug === product.slug
                  ? { ...item, quantity: item.quantity + quantity }
                  : item
              ),
            };
          }
          return {
            isOpen: true,
            items: [...state.items, { product, quantity }],
          };
        });
      },
      removeItem: (slug) =>
        set((state) => ({
          items: state.items.filter((item) => item.product.slug !== slug),
        })),
      setQuantity: (slug, quantity) =>
        set((state) => ({
          items:
            quantity <= 0
              ? state.items.filter((item) => item.product.slug !== slug)
              : state.items.map((item) =>
                  item.product.slug === slug ? { ...item, quantity } : item
                ),
        })),
      increment: (slug) => {
        const item = get().items.find((entry) => entry.product.slug === slug);
        if (item) get().setQuantity(slug, item.quantity + 1);
      },
      decrement: (slug) => {
        const item = get().items.find((entry) => entry.product.slug === slug);
        if (item) get().setQuantity(slug, item.quantity - 1);
      },
      setCouponCode: (code) => set({ couponCode: code }),
      clearCoupon: () => set({ couponCode: null }),
      clear: () => set({ items: [], couponCode: null }),
    }),
    {
      name: "parambu-cart",
      partialize: (state) => ({ items: state.items, couponCode: state.couponCode }),
    }
  )
);
