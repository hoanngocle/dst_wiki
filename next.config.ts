import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [{ source: "/tu-tien-ky", destination: "/pham-nhan-tu-tien", permanent: true }];
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
