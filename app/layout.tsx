import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  ),
  title: "DST Wiki | Don't Starve Together",
  description: "Tra cứu vật phẩm, đồ chế Tu Tiên của Hàn Lập và cảnh giới Tu Tiên trong Don't Starve Together.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="h-full antialiased">
      <body className="min-h-full">
        <div className="nova-game-theme min-h-dvh text-nova-text">{children}</div>
      </body>
    </html>
  );
}
