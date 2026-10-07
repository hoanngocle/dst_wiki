import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      { source: "/hot-key", destination: "/nova/hot-key", permanent: true },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "dontstarve.wiki.gg",
        port: "",
        pathname: "/wiki/Special:Redirect/file/**",
        search: "",
      },
      {
        protocol: "https",
        hostname: "dontstarve.wiki.gg",
        port: "",
        pathname: "/images/thumb/**",
      },
    ],
  },
};

export default nextConfig;
