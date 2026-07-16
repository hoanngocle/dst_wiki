import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Danh mục vật phẩm DST & Tu Tiên | Don't Starve Together",
  description:
    "Tra cứu vật phẩm DST và Tu Tiên theo Wiki, hình ảnh, danh mục và công thức.",
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
