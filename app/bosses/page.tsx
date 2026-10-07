import type { Metadata } from "next";
import Link from "next/link";
import { BossCards } from "./boss-cards";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";

export const metadata: Metadata = {
  title: "Lộ trình boss DST: hướng dẫn từng tuyến từ đầu | DST Wiki",
  description: "Đi hết các tuyến boss DST: boss mùa, Bee Queen, Dragonfly, Klaus, Terraria, Toadstool, Werepig, Sanctum, boss biển, Lunar và Ancient.",
};

const stages = [
  { title: "01. Sống ổn qua các mùa", description: "Học né đòn với Deerclops, Moose/Goose và Bearger; chuẩn bị chống nóng để giải quyết Antlion. Tận dụng mùa đông tìm Klaus, không cần chờ xong toàn bộ nhóm đầu mới đi nhánh tiếp.", links: [{ label: "Boss theo mùa", href: "/bosses/seasonal" }, { label: "Klaus", href: "/bosses/klaus" }] },
  { title: "02. Có nguồn đồ hồi phục và trang bị", description: "Chọn Eye of Terror để lấy mũ có thể cho ăn sửa; Bee Queen để có Royal Jelly và Bundling Wrap; Dragonfly cho Scaled Furnace. Đây là thứ tự gợi ý, không phải khóa tiến trình.", links: [{ label: "Eye & Twins", href: "/bosses/terraria" }, { label: "Bee Queen", href: "/bosses/bee-queen" }, { label: "Dragonfly", href: "/bosses/dragonfly" }] },
  { title: "03. Khám phá sâu và ra biển", description: "Đi Ruins chế đồ, đánh Guardian lấy Key. Đóng thuyền để đi Pearl, Crab King và các boss biển; nhánh biển có thể chuẩn bị song song với nhánh hang.", links: [{ label: "Ruins → Guardian", href: "/ancient" }, { label: "Malbatross & Frostjaw", href: "/bosses/ocean" }, { label: "Pearl → Crab King", href: "/lunar-rift#truoc-rift" }] },
  { title: "04. Hoàn thành hai tuyến tiến trình lớn", description: "Shadow Pieces + Guardian hội tụ ở Fuelweaver. Nhánh Pearl + Archive hội tụ ở Celestial Champion. Nightmare Werepig cung cấp Dreadstone cho bước mở Shadow Rift, nên có thể đánh trước hoặc sau Fuelweaver.", links: [{ label: "Fuelweaver → Shadow Rift", href: "/ancient#trieu-hoi" }, { label: "Champion → Lunar Rift", href: "/lunar-rift" }, { label: "Nightmare → Scrappy Werepig", href: "/bosses/werepig" }] },
  { title: "05. Dọn các thử thách còn lại", description: "Hoàn thành Twins, Toadstool rồi Misery; khám phá Ancient Sanctum và Guard Towers. Khi đã mở Lunar Rift, tiếp tục boss đột biến và chuỗi Wagstaff trong guide Lunar.", links: [{ label: "Twins of Terror", href: "/bosses/terraria" }, { label: "Toadstool & Misery", href: "/bosses/toadstool" }, { label: "Ancient Sanctum", href: "/bosses/ancient-sanctum" }, { label: "Boss sau Lunar Rift", href: "/lunar-rift#tien-trinh" }] },
];

function Source({ page, children }: { page: string; children: string }) {
  return <a href={`https://dontstarve.wiki.gg/wiki/${page}`} target="_blank" rel="noreferrer" className="text-nova-accent underline underline-offset-4">{children} ↗</a>;
}

export default function BossRoutesPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
    <SiteHeader active="bosses" />
    <DstPageShell>
      <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
        <div className="mb-7">
          <p className="text-xs font-semibold uppercase tracking-widest text-nova-faint">Cẩm nang Don&apos;t Starve Together</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Lộ trình boss</h1>
          <p className="mt-3 text-sm leading-6 text-nova-muted">Chọn boss để xem cách triệu hồi, chuẩn bị vật phẩm và hướng dẫn chiến đấu.</p>
        </div>
        <BossCards />
        <nav aria-label="Mục lục lộ trình boss" className="my-6 flex flex-wrap gap-3">{[["lo-trinh", "Lộ trình đi hết"], ["hanh-trang", "Hành trang từ số 0"], ["cac-guide", "Chọn guide chi tiết"]].map(([id, label]) => <a key={id} href={`#${id}`} className="inline-flex min-h-11 items-center rounded-full border border-nova-border bg-nova-surface px-5 text-sm font-semibold text-nova-accent underline underline-offset-4">{label}</a>)}</nav>

        <section id="lo-trinh" aria-labelledby="lo-trinh-title" className="scroll-mt-6 rounded-2xl border border-nova-border bg-nova-surface p-5 sm:p-8">
          <h2 id="lo-trinh-title" className="text-2xl font-semibold">Lộ trình đi hết: theo đồ đang có, không chạy đua ngày</h2>
          <p className="mt-3 max-w-4xl text-sm leading-7 text-nova-muted">“Đi hết” ở đây bao gồm các tuyến đã giới thiệu ở trang Ancient, thêm nhóm boss mùa và biển. Không cần cố hoàn tất trong năm đầu. Khi gặp đúng mùa hoặc tìm thấy địa điểm thuận tiện, có thể rẽ sang nhánh khác rồi quay lại.</p>
          <ol className="mt-6 grid gap-4">{stages.map(stage => <li key={stage.title} className="rounded-xl bg-nova-surface-soft p-5"><h3 className="text-lg font-semibold">{stage.title}</h3><p className="mt-2 text-sm leading-7 text-nova-muted">{stage.description}</p><div className="mt-3 flex flex-wrap gap-x-5 gap-y-2">{stage.links.map(link => <Link key={link.href} href={link.href} className="inline-flex min-h-10 items-center text-sm font-semibold text-nova-accent underline underline-offset-4">{link.label} →</Link>)}</div></li>)}</ol>
          <p className="mt-5 text-sm leading-7 text-nova-muted">Hãy ghi lại boss đã hạ và vật phẩm còn thiếu theo save của bạn. Một boss chết không đồng nghĩa đã xong nhánh: Klaus còn túi đồ cần mở, Frostjaw còn đổi cá, Fuelweaver còn bước trao Dreadstone.</p>
        </section>

        <section id="hanh-trang" aria-labelledby="hanh-trang-title" className="mt-6 scroll-mt-6 rounded-2xl border border-nova-border bg-nova-surface p-5 sm:p-8">
          <h2 id="hanh-trang-title" className="text-2xl font-semibold">Hành trang từ số 0</h2>
          <p className="mt-3 text-sm leading-7 text-nova-muted">Đây là nền chuẩn bị chung. Mỗi guide bổ sung công cụ riêng; số lượng hồi máu và giáp phải tăng theo độ khó, nhân vật và số người cùng đánh.</p>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl bg-nova-surface-soft p-5"><h3 className="font-semibold">Vũ khí đủ sức đánh lâu</h3><p className="mt-2 text-sm leading-7 text-nova-muted">Ham Bat cần 1 Pig Skin + 2 Meat + 2 Twigs, học tại Alchemy Engine. Chuẩn bị nguyên liệu rồi chế gần giờ đánh để giữ sát thương; giết Werepig thường là một cách kiếm da và thịt. Những trận cuối có thể cần đồ Ancient hoặc planar theo guide. <Source page="Ham_Bat">Ham Bat</Source></p></div>
            <div className="rounded-xl bg-nova-surface-soft p-5"><h3 className="font-semibold">Giáp và đồ thay sẵn</h3><p className="mt-2 text-sm leading-7 text-nova-muted">Mang mũ/giáp đang dùng và bộ dự phòng; đặt ở ô dễ đổi khi gần vỡ. Kiểm tra ô trang bị: đeo Nightmare Amulet thay giáp thân, đội kính thay mũ. Đừng vào trận rồi mới phát hiện món tiện ích đã chiếm ô phòng thủ. <Source page="Armor">Trang bị phòng thủ</Source></p></div>
            <div className="rounded-xl bg-nova-surface-soft p-5"><h3 className="font-semibold">Hồi máu và no bụng là hai việc</h3><p className="mt-2 text-sm leading-7 text-nova-muted">Một công thức Pierogi dễ nhớ: 1 Egg + 1 Meat + 1 Carrot + 1 Berry trong Crock Pot. Trứng có thể lấy bằng cách cho chim trong Birdcage ăn thịt. Mang thêm thức ăn no bụng; đừng dùng hết đồ hồi máu chỉ để chống đói. Nhân vật có chế độ ăn đặc biệt cần món phù hợp. <Source page="Pierogi">Pierogi</Source> · <Source page="Birdcage">Birdcage</Source></p></div>
            <div className="rounded-xl bg-nova-surface-soft p-5"><h3 className="font-semibold">Sân đánh, ánh sáng và đường rút</h3><p className="mt-2 text-sm leading-7 text-nova-muted">Gợi ý chuẩn bị: dọn vật cản, đặt ánh sáng ngoài vùng boss phá được, để đồ dự phòng ở điểm tập kết riêng. Chọn cách hồi sinh phù hợp chế độ chơi. Khi đi nhóm, phân công người giữ boss và người xử lý quái phụ; không cùng kéo boss về trại.</p></div>
          </div>
          <p className="mt-5 text-sm leading-7 text-nova-muted">Đọc các từ trong bài: <strong className="text-nova-text">kite</strong> = dụ boss đánh hụt rồi phản công; <strong className="text-nova-text">aggro</strong> = boss đang nhắm ai; <strong className="text-nova-text">phase</strong> = giai đoạn thay đổi bộ đòn; <strong className="text-nova-text">reset</strong> = trận kết thúc/mất tiến độ, phải chuẩn bị lại. Không cố thuộc một số hit cố định khi tốc độ và độ trễ server khác nhau.</p>
        </section>

        <p className="mt-8 text-xs leading-6 text-nova-faint">Ảnh boss: Klei Entertainment / <a href="https://dontstarve.wiki.gg/" target="_blank" rel="noreferrer" className="underline underline-offset-4">Don&apos;t Starve Wiki</a>. Hướng dẫn theo DST gốc; thiết lập và mod server có thể thay đổi cơ chế.</p>
      </div>
    </DstPageShell>
  </div>;
}
