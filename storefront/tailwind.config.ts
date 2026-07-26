import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        // Warm rose-copper from Parambu leaf logo — kept as `gold` token name
        gold: {
          DEFAULT: "#B18767",
          light: "#D6AA84",
          deep: "#8F6B4F",
        },
        forest: "#1b4332",
        leaf: "#2d6a4f",
        moss: "#40916c",
        mist: "#eef5ef",
        sand: "#f7f1e4",
        ink: "#14201a",
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      maxWidth: {
        site: "74rem",
      },
      boxShadow: {
        soft: "0 10px 30px rgba(20, 32, 26, 0.08)",
      },
    },
  },
  plugins: [],
} satisfies Config;
