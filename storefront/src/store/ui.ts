"use client";

import { create } from "zustand";

type UIState = {
  searchOpen: boolean;
  mobileNavOpen: boolean;
  openSearch: () => void;
  closeSearch: () => void;
  openMobileNav: () => void;
  closeMobileNav: () => void;
};

export const useUI = create<UIState>((set) => ({
  searchOpen: false,
  mobileNavOpen: false,
  openSearch: () => set({ searchOpen: true, mobileNavOpen: false }),
  closeSearch: () => set({ searchOpen: false }),
  openMobileNav: () => set({ mobileNavOpen: true, searchOpen: false }),
  closeMobileNav: () => set({ mobileNavOpen: false }),
}));
