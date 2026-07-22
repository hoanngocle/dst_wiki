import type { Metadata } from "next";

import { GuideBrowser } from "@/app/components/guide-browser";
import { SiteHeader } from "@/app/components/site-header";
import { parseGuideIndex } from "@/app/lib/guide-catalog";
import guidePayload from "@/public/data/guides/index.json";

export const metadata: Metadata = {
  title: "Guide DST | Don't Starve Together",
  description: "Thư viện hướng dẫn Don't Starve Together đã chọn lọc và lưu cục bộ.",
};

const index = parseGuideIndex(guidePayload);

export default function GuidesPage() {
  return (
    <div className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <SiteHeader active="guides" />
      <main className="mx-auto max-w-7xl px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
        <div className="grid gap-8 border-b border-[#c7d2df] pb-9 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-end">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#2e5fb3]">Sổ tay DST</p>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-[1.04] tracking-[-0.04em] text-[#14233b] sm:text-5xl">Guide thực chiến, đọc riêng từng bài</h1>
            <p className="mt-4 max-w-[65ch] text-base leading-7 text-[#53647a]">Nội dung áp dụng cho Don&apos;t Starve Together, có ảnh nguồn và thông tin phiên bản đã kiểm tra.</p>
          </div>
          <dl className="grid grid-cols-2 overflow-hidden rounded-2xl border border-[#c7d2df] bg-[#f8fafc]">
            <div className="border-r border-[#d7dfe8] p-4"><dt className="text-xs text-[#607188]">Bài đã duyệt</dt><dd className="mt-1 text-2xl font-semibold">{index.count}</dd></div>
            <div className="p-4"><dt className="text-xs text-[#607188]">Phạm vi</dt><dd className="mt-1 text-2xl font-semibold">DST</dd></div>
          </dl>
        </div>
        <GuideBrowser guides={index.guides} />
      </main>
    </div>
  );
}
