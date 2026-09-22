import type { Metadata } from "next";

import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { PhamNhanNav } from "@/app/components/pham-nhan-nav";
import { SiteHeader } from "@/app/components/site-header";

export const metadata: Metadata = {
  title: "Hướng dẫn hotkey | Phàm Nhân Tu Tiên",
  description: "Danh sách phím tắt, chức năng và điều kiện sử dụng trong Phàm Nhân Tu Tiên.",
};

interface HotkeyItem {
  keys: readonly string[];
  action: string;
  note: string;
}

interface HotkeyGroupProps {
  id: string;
  title: string;
  description: string;
  items: readonly HotkeyItem[];
}

const interfaceHotkeys: readonly HotkeyItem[] = [
  {
    keys: ["X"],
    action: "Mở Bảng Tổng Hợp",
    note: "X là phím mặc định và có thể đổi tại cấu hình mod. Nếu chọn B hoặc V, game tự dùng X. Không chọn G, J hoặc L vì các phím này đã có chức năng riêng.",
  },
  {
    keys: ["B"],
    action: "Mở bảng trạng thái nhân vật",
    note: "Mở thẳng tab nhân vật trong Bảng Tổng Hợp. Không hoạt động khi bảng hướng dẫn đang mở.",
  },
  {
    keys: ["G"],
    action: "Sắp xếp kho đồ",
    note: "Nếu đang mở rương, phím này sắp xếp rương. Nếu không, nó sắp túi đồ và ba lô. Không dùng được khi đang cầm vật phẩm hoặc đã chết.",
  },
  {
    keys: ["J"],
    action: "Mở cửa hàng hầm ngục",
    note: "Chỉ dùng khi nhân vật còn sống, đang ở mặt đất và không mở bảng hướng dẫn.",
  },
];

const evaHotkeys: readonly HotkeyItem[] = [
  {
    keys: ["1"],
    action: "Sinh Chi Hoa",
    note: "Chỉ dành cho EVA. Mở khóa từ cấp 10 và cần đủ Hồn Lực.",
  },
  {
    keys: ["2"],
    action: "Tử Phong Tụ Linh",
    note: "Chỉ dành cho EVA. Mở khóa từ cấp 20 và cần đủ Hồn Lực. Nhấn phím, sau đó chọn vị trí thi triển.",
  },
  {
    keys: ["3"],
    action: "Tinh Vũ Nguyệt Dực",
    note: "Chỉ dành cho EVA. Mở khóa từ cấp 30 và cần đủ Hồn Lực.",
  },
  {
    keys: ["4"],
    action: "Dạ Du",
    note: "Chỉ dành cho EVA. Mở khóa từ cấp 50 và cần đủ Hồn Lực. Nhấn phím, sau đó chọn vị trí thi triển.",
  },
  {
    keys: ["5"],
    action: "Trảm Linh",
    note: "Chỉ dành cho EVA. Mở khóa từ cấp 100 và cần đủ Hồn Lực. Nhấn phím, sau đó chọn vị trí thi triển.",
  },
  {
    keys: ["Chuột phải"],
    action: "Hồ Ảnh",
    note: "Chỉ dành cho EVA, có từ cấp 1. Nhấp chuột phải lên mặt đất để dịch chuyển và gây lôi kích. Không dùng được khi cưỡi thú.",
  },
];

const combatHotkeys: readonly HotkeyItem[] = [
  {
    keys: ["V"],
    action: "Mở vòng kỹ năng",
    note: "Nhấn một lần để mở hoặc đóng vòng kỹ năng Solo đã tích hợp. Một số kỹ năng cần cấp bang hội hoặc trạng thái phù hợp.",
  },
  {
    keys: ["L"],
    action: "Ra lệnh Fruit Fly Bóng Ma",
    note: "Đưa con trỏ tới vị trí trong thế giới hoặc trên bản đồ lớn rồi nhấn L. Không hoạt động khi con trỏ đang nằm trên giao diện.",
  },
  {
    keys: ["Shift", "Alt", "Chuột trái"],
    action: "Chia sẻ chỉ số trang bị",
    note: "Dùng trên trang bị Phàm Nhân hoặc Đá Hiệu Ứng. Tính năng phải được bật trong cấu hình mod.",
  },
  {
    keys: ["Alt", "Chuột phải"],
    action: "Khóa vật phẩm trong Kho Quân Vương",
    note: "Chỉ hoạt động trên ô của Kho Quân Vương. Lặp lại thao tác để thay đổi trạng thái khóa của vật phẩm.",
  },
];

function KeyCombination({ keys }: { keys: readonly string[] }) {
  return (
    <span role="group" className="flex flex-wrap items-center gap-1.5" aria-label={keys.join(" cộng ")}>
      <span aria-hidden="true" className="contents">
        {keys.map((key, index) => (
          <span key={key} className="contents">
            {index > 0 ? <span className="text-xs text-nova-faint">+</span> : null}
            <kbd className="inline-flex min-h-8 min-w-8 items-center justify-center rounded-lg border border-nova-border bg-nova-surface-raised px-2.5 font-mono text-xs font-semibold text-nova-text shadow-[0_2px_0_#cbd5e1]">
              {key}
            </kbd>
          </span>
        ))}
      </span>
    </span>
  );
}

function HotkeyGroup({ id, title, description, items }: HotkeyGroupProps) {
  return (
    <section aria-labelledby={id} className="rounded-2xl border border-nova-border bg-nova-surface p-4 sm:p-6">
      <div className="max-w-[65ch]">
        <h2 id={id} className="text-xl font-semibold tracking-[-0.02em] text-nova-text sm:text-2xl">
          {title}
        </h2>
        <p className="mt-2 text-sm leading-6 text-nova-muted">{description}</p>
      </div>

      <div aria-hidden="true" className="mt-6 hidden grid-cols-[minmax(9rem,0.8fr)_minmax(12rem,1.25fr)_auto] gap-4 px-4 text-xs font-semibold text-nova-faint sm:grid">
        <span>Phím bấm</span>
        <span>Chức năng</span>
        <span>Điều kiện / ghi chú</span>
      </div>

      <div className="mt-3 grid gap-3">
        {items.map((item) => (
          <details key={`${item.keys.join("+")}-${item.action}`} className="group rounded-xl border border-nova-border bg-nova-surface-raised open:border-nova-accent">
            <summary className="grid min-h-16 cursor-pointer list-none items-center gap-3 rounded-xl px-4 py-3 transition-colors hover:bg-nova-surface-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-nova-accent sm:grid-cols-[minmax(9rem,0.8fr)_minmax(12rem,1.25fr)_auto] sm:gap-4 [&::-webkit-details-marker]:hidden">
              <KeyCombination keys={item.keys} />
              <span className="font-semibold text-nova-text">{item.action}</span>
              <span className="flex items-center gap-2 text-sm font-semibold text-nova-accent">
                <span className="group-open:hidden">Xem ghi chú</span>
                <span className="hidden group-open:inline">Ẩn ghi chú</span>
                <span aria-hidden="true" className="text-lg leading-none transition-transform group-open:rotate-45">+</span>
              </span>
            </summary>
            <div className="border-t border-nova-border px-4 py-4 sm:pl-[calc(36.25%+1rem)]">
              <p className="max-w-[65ch] text-sm leading-6 text-nova-muted">{item.note}</p>
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}

export default function HotKeyPage() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="tu-tien-ky" />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <DstHero
            eyebrow="PHÀM NHÂN TU TIÊN"
            title="Hướng dẫn hotkey"
            description="Chọn một phím để xem chức năng, điều kiện mở khóa và cách sử dụng trong game."
          />
          <PhamNhanNav active="hotkey" />

          <div className="grid gap-5">
            <HotkeyGroup
              id="giao-dien-kho-do"
              title="Giao diện và kho đồ"
              description="Các phím mở bảng chức năng, cửa hàng và sắp xếp vật phẩm."
              items={interfaceHotkeys}
            />
            <HotkeyGroup
              id="ky-nang-eva"
              title="Kỹ năng EVA"
              description="Dùng dãy số phía trên bàn phím. Kỹ năng cần đúng cấp mở khóa và đủ Hồn Lực."
              items={evaHotkeys}
            />
            <HotkeyGroup
              id="chien-dau-tuong-tac"
              title="Chiến đấu và tương tác"
              description="Điều khiển vòng kỹ năng, thực thể triệu hồi và các thao tác đặc biệt với vật phẩm."
              items={combatHotkeys}
            />
          </div>
        </div>
      </DstPageShell>
    </div>
  );
}
