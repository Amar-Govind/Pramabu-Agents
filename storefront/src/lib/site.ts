import siteData from "@/data/site.json";

export type SiteConfig = typeof siteData;

export const site = siteData as SiteConfig;
