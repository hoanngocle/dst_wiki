import Image from "next/image";

import { SiteHeader } from "@/app/components/site-header";
import { baseEntries } from "@/app/data/base-entries";

export default function BasePage() {
  return (
    <div className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <SiteHeader active="base" />
      <main>
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
          <div className="max-w-2xl">
            <h1 className="text-4xl font-semibold leading-[1.02] tracking-[-0.045em] text-[#14233b] sm:text-5xl lg:text-6xl">
              Thư viện Base
            </h1>
            <p className="mt-4 max-w-[52ch] text-base leading-7 text-[#53647a]">
              Tham khảo cách bố trí căn cứ theo từng địa hình và giai đoạn sinh tồn.
            </p>
          </div>

          <ul className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {baseEntries.map((entry) => (
              <li
                key={entry.id}
                className="overflow-hidden rounded-2xl border border-[#cbd5e1] bg-[#f8fafc]"
              >
                <div className="relative aspect-video overflow-hidden bg-[#dbe3ec]">
                  <Image
                    src={entry.image}
                    alt={entry.name}
                    fill
                    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                    className="object-cover"
                  />
                </div>
                <div className="px-5 py-4 text-base font-semibold tracking-[-0.015em] text-[#14233b]">
                  {entry.name}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </main>
    </div>
  );
}
