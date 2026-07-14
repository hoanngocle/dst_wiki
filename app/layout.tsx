import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Wiki Prefab DST & Tu Tiên | Don't Starve Together",
  description:
    "Tra cứu toàn bộ prefab DST và Tu Tiên theo category, hình ảnh và công thức.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
