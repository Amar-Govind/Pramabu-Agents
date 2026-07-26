"use client";

import { CartDrawer } from "@/components/CartDrawer";
import { SearchModal } from "@/components/SearchModal";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <SiteHeader />
      <main>{children}</main>
      <SiteFooter />
      <CartDrawer />
      <SearchModal />
    </>
  );
}
