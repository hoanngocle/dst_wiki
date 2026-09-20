import type { Metadata } from "next";

import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { WikiSearch } from "@/app/components/wiki-search";
import { PhamNhanNav } from "@/app/components/pham-nhan-nav";
import { tuTienKyItems, tuTienKyReferences, tuTienKyVersion } from "@/app/data/tu-tien-ky";

export const metadata: Metadata = {
  title: "Phàm Nhân Tu Tiên | DST Wiki",
  description: "Tra cứu đầy đủ công thức, tác dụng, sản vật, thú nuôi và thực thể triệu hồi trong mod Phàm Nhân Tu Tiên.",
};

export default function TuTienKyPage() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="tu-tien-ky" />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <DstHero
            eyebrow={`DST · Phàm Nhân Tu Tiên ${tuTienKyVersion}`}
            title="Phàm Nhân Tu Tiên"
            description="Từ công thức chế tạo đến sản vật thu hoạch, thú nuôi và triệu hồi. Chọn một mục để xem cách dùng và những thứ sinh ra từ nó."
            stats={[
              { label: "Mục tra cứu", value: tuTienKyItems.length },
              { label: "Công thức", value: tuTienKyItems.filter((item) => item.recipe !== null).length },
              { label: "Công trình", value: tuTienKyItems.filter((item) => item.category === "structure").length },
            ]}
            statsAriaLabel="Tổng quan Phàm Nhân Tu Tiên"
          />
          <PhamNhanNav active="catalog" />
          <div className="mb-6 rounded-2xl border border-nova-border bg-nova-surface-soft p-4 text-sm leading-6 text-nova-muted">
            <p><strong className="text-nova-text">Phàm Nhân {tuTienKyVersion}:</strong> Solo đã tích hợp đầy đủ. Wiki gồm công trình, pháp bảo, bộ giáp, linh thảo, thú nuôi, Máy Quay Thưởng, Linh Tuyền và Vĩnh Hằng Thần Hỏa. Xem Hướng dẫn để tra cứu cách chơi và Config để xem tùy chọn mặc định. EVA đã tích hợp, dùng cấp từ Achievement & Level. Đã bổ sung chín boss, linh vật, chiến lợi phẩm và hạt cây.</p>
          </div>
          <WikiSearch items={tuTienKyItems} referenceItems={[...tuTienKyReferences, ...tuTienKyItems]} hideSourceFilters />
        </div>
      </DstPageShell>
    </div>
  );
}
