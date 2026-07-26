import type { Metadata } from "next";
import { Fraunces, Plus_Jakarta_Sans } from "next/font/google";
import { AppShell } from "@/components/AppShell";
import "./globals.css";

const display = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

const sans = Plus_Jakarta_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: {
    default: "Parambu Organics",
    template: "%s · Parambu Organics",
  },
  description:
    "Everyday pure & natural care from Parambu Organics — handcrafted soaps, virgin coconut oil, and coco gardening essentials.",
  metadataBase: new URL("https://parambu.in"),
  icons: {
    icon: [{ url: "/favicon.png", type: "image/png" }],
    apple: ["/brand/logo-gold.png"],
    shortcut: ["/favicon.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${sans.variable} font-sans antialiased`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
