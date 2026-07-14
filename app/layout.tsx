import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Wiki vật phẩm Tu Tiên | Don't Starve Together",
  description:
    "Tra cứu tên, prefab, hình ảnh và công thức vật phẩm Tu Tiên trong Don't Starve Together.",
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
