import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "dontstarve.wiki.gg",
        port: "",
        pathname: "/wiki/Special:Redirect/file/**",
        search: "",
      },
    ],
  },
};

export default nextConfig;
