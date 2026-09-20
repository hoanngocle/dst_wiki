import type { Metadata } from "next";
import { SiteHeader } from "@/app/components/site-header";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { DstHero } from "@/app/components/dst-hero";
import { LingGioiBrowser } from "@/app/components/ling-gioi-browser";
import { lingGioiItems, lingGioiSections } from "@/app/data/ling-gioi";

export const metadata: Metadata = { title: "Linh Giới | DST Wiki", description: "Wiki Linh Giới tiếng Việt: cảnh giới, luyện đan, pháp bảo, trận pháp, linh thực và Boss trong Don't Starve Together." };

export default function LingGioiPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text"><SiteHeader active="linh-gioi" /><DstPageShell><div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
    <DstHero eyebrow="DST · Linh Giới v0.1" title="Linh Giới" description="Từ những bước tu luyện đầu tiên đến luyện đan, trận pháp và đối đầu yêu thú. Tra cứu toàn bộ hướng dẫn bằng tiếng Việt." stats={[{ label: "Mục tra cứu", value: lingGioiItems.length }, { label: "Chuyên mục", value: lingGioiSections.length }, { label: "Cảnh giới", value: 9 }]} statsAriaLabel="Tổng quan Linh Giới" />
    <p className="mt-5 text-sm leading-6 text-nova-muted">Việt hóa từ <a href="https://eyanhuahu.github.io/lingjie/" target="_blank" rel="noreferrer" className="text-nova-accent underline">wiki Linh Giới</a> của JinYan và BigXian. Thông số và công thức theo bản nguồn; các mục chưa có nội dung được ghi rõ.</p>
    <LingGioiBrowser sections={lingGioiSections} items={lingGioiItems} />
  </div></DstPageShell></div>;
}
