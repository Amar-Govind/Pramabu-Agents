import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "parambu.in",
        pathname: "/wp-content/uploads/**",
      },
    ],
  },
  async redirects() {
    return [
      { source: "/shop/oils", destination: "/shop/hair-care/oils", permanent: false },
      { source: "/shop/oil", destination: "/shop/hair-care/oils", permanent: false },
      { source: "/shop/soap", destination: "/shop/skin-care/soap", permanent: false },
      { source: "/shop/soaps", destination: "/shop/skin-care/soap", permanent: false },
      { source: "/shop/cocopeat", destination: "/shop/gardening/cocopeat", permanent: false },
      { source: "/shop/coco", destination: "/shop/gardening/cocopeat", permanent: false },
    ];
  },
};

export default nextConfig;
