import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { spriteCropStyle } from "@/app/lib/sprite";
import itemPayload from "@/public/data/items.json";

export const metadata: Metadata = {
  title: "Lunar Rift: mở Rift, vật phẩm và cách chơi | DST Wiki",
  description: "Hướng dẫn Lunar Rift bằng tiếng Việt: mở Rift, farm Pure Brilliance và Brightshade Husk, chế trang bị, sát thương planar và boss đột biến.",
};

const chapters = [
  ["bat-dau", "Bắt đầu từ đâu?"],
  ["mo-rift", "Mở Rift & chu kỳ"],
  ["chuan-bi", "Chuẩn bị & planar"],
  ["nguyen-lieu", "Kiếm nguyên liệu"],
  ["vat-pham", "Vật phẩm & chế tạo"],
  ["brightshade", "Đánh Brightshade"],
  ["boss", "Boss đột biến"],
  ["tien-trinh", "Tiến trình tiếp theo"],
  ["hoi-dap", "Câu hỏi thường gặp"],
] as const;

function Source({ page, children }: { page: string; children?: ReactNode }) {
  return <a href={`https://dontstarve.wiki.gg/wiki/${page}`} target="_blank" rel="noreferrer" className="font-medium text-nova-accent underline decoration-nova-accent/40 underline-offset-4 hover:decoration-nova-accent focus-visible:outline-2 focus-visible:outline-nova-accent">{children ?? page.replaceAll("_", " ")} ↗</a>;
}

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return <section id={id} aria-labelledby={`${id}-title`} className="scroll-mt-6 rounded-2xl border border-nova-border bg-nova-surface p-5 sm:p-8">
    <h2 id={`${id}-title`} className="text-2xl font-semibold tracking-[-0.025em] text-nova-text">{title}</h2>
    <div className="mt-5 space-y-4 text-sm leading-7 text-nova-muted [&_strong]:font-semibold [&_strong]:text-nova-text [&_li]:pl-1">{children}</div>
  </section>;
}

function ItemIcon({ prefab }: { prefab: string }) {
  const sprite = itemPayload.items.find(item => item.id === `base_game:${prefab}`)?.sprite;
  return sprite ? <span aria-hidden="true" className="inline-block shrink-0 rounded-xl bg-nova-surface-soft" style={spriteCropStyle(sprite, 48)} /> : null;
}

const equipment = [
  { name: "Brightshade Helm", prefab: "lunarplanthat", cost: "4 Pure Brilliance + 2 Husk", use: "80% giáp vật lý, 10 phòng thủ planar. Chống Charlie trong bóng tối và tăng hiệu quả vũ khí Brightshade.", priority: "Ưu tiên đầu" },
  { name: "Brightshade Sword", prefab: "sword_lunarplant", cost: "4 Pure Brilliance + 3 Husk", use: "38 sát thương vật lý + 30 planar. Đội Helm tăng thành 41,8 + 35; đánh mục tiêu Shadow Aligned được thêm 10% tổng sát thương.", priority: "Vũ khí chủ lực" },
  { name: "Brightshade Armor", prefab: "armor_lunarplant", cost: "4 Pure Brilliance + 4 Husk", use: "80% giáp vật lý, 10 phòng thủ planar; phản sát thương planar. Mặc cùng Helm tăng khả năng chống địch Lunar Aligned.", priority: "An toàn khi đánh boss" },
  { name: "Brightshade Staff", prefab: "staff_lunarplant", cost: "3 Pure Brilliance + 6 Husk", use: "Đạn nảy giữa các mục tiêu, gây 10 planar mỗi lần trúng (20 với Shadow Aligned). Tối đa 5 lần trúng; đội Helm tăng lên 7.", priority: "Đánh nhóm / tầm xa" },
  { name: "Brightshade Smasher", prefab: "pickaxe_lunarplant", cost: "1 Pure Brilliance + 2 Husk", use: "Kết hợp cuốc và búa; tiện cho chuyến khai thác tiếp theo. Không cần sở hữu nó mới bắt đầu kiếm Pure Brilliance.", priority: "Công cụ khai thác" },
  { name: "Brightshade Shoevel", prefab: "shovel_lunarplant", cost: "1 Pure Brilliance + 2 Husk", use: "Công cụ đào thuộc bộ Brightshade. Có thể để sau trang bị chiến đấu nếu nguyên liệu còn ít.", priority: "Tiện ích về sau" },
  { name: "Brightshade Bomb", prefab: "bomb_lunarplant", cost: "4 Pure Brilliance + 4 Husk + 1 Infused Moon Shard → 6 bom", use: "Vật phẩm chiến đấu tiêu hao. Nên hoàn thiện trang bị dùng lâu dài trước khi dành nguyên liệu làm bom.", priority: "Tùy nhu cầu" },
] as const;

const bosses = [
  { name: "Crystal Deerclops", from: "Deerclops", tip: "Dụ hai đòn bắn tinh thể, rồi dùng lửa đúng lúc nó đã hết hai tinh thể trên lưng, trước khi mọc lại, để gây choáng. Đừng đứng lâu trong vùng băng; sau choáng, đề phòng chuỗi đánh liên tiếp." },
  { name: "Armored Bearger", from: "Bearger", tip: "Đừng áp dụng máy móc nhịp né của Bearger thường: nó có thể tát liên tiếp. Sau cú ngồi đè, đánh trúng hai lần bằng vũ khí có planar để gây choáng; Staff giúp tận dụng cửa sổ này từ xa." },
  { name: "Possessed Varg", from: "Varg", tip: "Dọn hoặc kiểm soát đàn chó, vì chó được gọi có thể biến thành Horror Hound sau khi chết. Khi Varg phun lửa lạnh, dùng vũ khí planar đánh trúng để gây choáng rồi tranh thủ tấn công hoặc xử lý chó." },
] as const;

export default function LunarRiftPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
    <SiteHeader active="bosses" />
    <DstPageShell>
      <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
        <Link href="/bosses" className="mb-5 inline-flex min-h-11 items-center text-sm font-semibold text-nova-accent underline underline-offset-4">← Lộ trình boss</Link>
        <DstHero eyebrow="Cẩm nang sinh tồn • Don't Starve Together" title="Lunar Rift" description="Từ lần mở khe nứt đầu tiên đến bộ trang bị Brightshade: biết cần chuẩn bị gì, kiếm vật liệu ở đâu và đánh thế nào để sống sót." stats={[{ label: "Trọng tâm", value: "Farm & chiến đấu" }, { label: "Dành cho", value: "Giai đoạn cuối" }]} statsAriaLabel="Phạm vi hướng dẫn">
          <p className="text-sm leading-6 text-nova-muted">Cơ chế DST gốc • Đối chiếu nguồn ngày <time dateTime="2026-10-07">07/10/2026</time>. Server Tu Tiên có thể thay đổi chỉ số, công thức hoặc thiết lập thế giới.</p>
        </DstHero>

        <div className="mt-8 grid items-start gap-6 lg:grid-cols-[14rem_minmax(0,1fr)]">
          <aside className="rounded-2xl border border-nova-border bg-nova-surface p-4 lg:sticky lg:top-6">
            <p className="px-3 text-xs font-semibold uppercase tracking-wider text-nova-faint">Trong trang này</p>
            <nav aria-label="Mục lục Lunar Rift" className="mt-3 grid gap-1 sm:grid-cols-2 lg:grid-cols-1">
              {chapters.map(([id, label], index) => <a key={id} href={`#${id}`} className="flex min-h-11 items-center gap-3 rounded-lg px-3 py-2 text-sm text-nova-muted transition-colors hover:bg-nova-surface-soft hover:text-nova-text focus-visible:outline-2 focus-visible:outline-nova-accent"><span className="text-xs text-nova-faint">{String(index + 1).padStart(2, "0")}</span>{label}</a>)}
            </nav>
            <a href="#truoc-rift" className="mt-3 block rounded-lg bg-nova-accent/10 px-3 py-3 text-sm font-semibold text-nova-accent underline underline-offset-4">Chưa biết Celestial Champion? Bắt đầu từ đây ↓</a>
          </aside>

          <article aria-label="Hướng dẫn Lunar Rift" className="min-w-0 space-y-6">
            <Section id="bat-dau" title="01. Bắt đầu từ đâu?">
              <Link href="/bosses" className="inline-block font-semibold text-nova-accent underline underline-offset-4">Xem lộ trình đi hết các tuyến boss khác →</Link>
              <p><strong>Mục tiêu chuyến đầu:</strong> mang về nguyên liệu, dựng Brightsmithy và bắt đầu bộ trang bị. Chưa cần lao ngay vào boss đột biến.</p>
              <ol className="grid list-inside list-decimal gap-3 sm:grid-cols-2">
                {["Chưa mở Rift → bắt đầu chuỗi chuẩn bị và triệu hồi boss trong hướng dẫn ngay bên dưới.", "Đã thấy Rift → mang cuốc, giáp và đồ hồi máu để kiếm Pure Brilliance.", "Đã có nguyên liệu → đánh Brightshade lấy Husk, chế Helm rồi chọn Sword hoặc Staff.", "Đã có bộ đồ → dự trữ Repair Kit, săn boss đột biến và tiếp tục nhiệm vụ Wagstaff."].map(step => <li key={step} className="rounded-xl bg-nova-surface-soft p-4">{step}</li>)}
              </ol>
              <a href="#truoc-rift" className="inline-block font-semibold text-nova-accent underline underline-offset-4">Tôi chưa biết Celestial Champion, Enlightened Shard hay Wagstaff → đọc từ đầu</a>
              <p className="text-xs">Đây là thứ tự chơi gợi ý; điều chỉnh theo trang bị và đồng đội hiện có.</p>
            </Section>

            <Section id="truoc-rift" title="Chưa mở Rift: từ số 0 đến Celestial Champion">
              <p><strong>Celestial Champion là boss Mặt Trăng gồm ba dạng.</strong> Bạn phải làm chuỗi nhiệm vụ để triệu hồi, rồi hạ cả ba dạng. <strong>Enlightened Shard</strong> là mảnh nhận sau trận. <strong>Wagstaff</strong> là nhà khoa học xuất hiện dưới dạng hình chiếu, tên trong game là Grainy Transmission. Trao mảnh cho ông ấy mới kích hoạt chu kỳ Lunar Rift. <Source page="Celestial_Champion" /> · <Source page="Enlightened_Shard" /></p>
              <p className="rounded-xl bg-nova-accent/5 p-4"><strong>Lộ trình:</strong> chuẩn bị thuyền và đồ xuống hang → tìm đảo Mặt Trăng → lấy ngọc của Pearl → mở Ancient Archive → gom đủ ba bàn thờ → làm nhiệm vụ trong Moonstorm → dựng máy triệu hồi → hạ boss → trao mảnh. Hai nhánh Pearl và Archive có thể làm song song khi chơi cùng bạn.</p>
              <p><strong>Nếu thế giới đã có Rift:</strong> bỏ qua chuỗi này và đọc mục kiếm nguyên liệu. Không cần mỗi người trong server làm lại từ đầu.</p>

              <div className="space-y-5 [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:text-nova-text [&_ol]:mt-3 [&_ol]:list-decimal [&_ol]:space-y-2 [&_ol]:pl-5">
                <div className="rounded-xl border border-nova-border p-5">
                  <h3>Bước 1 — Tìm Lunar Island và bàn thờ thứ nhất</h3>
                  <ol>
                    <li>Chuẩn bị thuyền, mái chèo, đồ sửa thuyền, thức ăn và nguồn sáng; đi biển tìm <strong>Lunar Island (đảo Mặt Trăng)</strong>. Đảo này khác đảo của Pearl.</li>
                    <li>Trên đảo, tìm các khối đá có vật thể mắc bên trong, tên <strong>Inviting Formation</strong>; dùng cuốc giải phóng ba mảnh <strong>Celestial Altar Base, Orb và Idol</strong>.</li>
                    <li>Mang ba mảnh đến một <strong>Celestial Fissure</strong> — khe nứt trên đảo — rồi lắp thành <strong>Celestial Altar</strong>. Chọn khu có nhiều khe nứt gần nhau để sau này đặt đủ ba bàn thờ.</li>
                  </ol>
                  <p className="mt-3"><strong>Xong bước này khi:</strong> có một Celestial Altar hoàn chỉnh. Mảnh <strong>Celestial Altar Orb</strong> không phải vật phẩm <strong>Celestial Orb</strong> dùng ở bước triệu hồi. <Source page="Lunar_Altars" /></p>
                </div>

                <div className="rounded-xl border border-nova-border p-5">
                  <h3>Bước 2 — Giúp Pearl để lấy Pearl&apos;s Pearl</h3>
                  <p className="mt-3">Đi biển nhặt <strong>Message in a Bottle</strong> và đọc để tìm đảo của <strong>Crabby Hermit</strong> (về sau tên là Pearl). Giúp bà làm việc để tăng tình bạn. Sau nhiệm vụ đầu tiên, dùng Empty Bottle đổi bản vẽ <strong>Pinchin&apos; Winch</strong>, máy trục vớt lắp trên thuyền. <Source page="Guides/Summoning_Celestial_Champion">Tìm Pearl và máy trục vớt</Source></p>
                  <p className="mt-3">Cần <strong>10 điểm tình bạn và hoàn thành cả ba lần nâng cấp nhà đầu tiên</strong> để nhận ngọc. Mỗi việc chỉ tăng điểm lần đầu; lặp một việc không đủ. Ví dụ: nâng nhà, trồng đủ 10 hoa bằng bướm bắt được, hoặc xây ghế và đợi bà ngồi. Kiểm tra vật liệu tại nhà trước mỗi chuyến. <Source page="Crabby_Hermit">Danh sách việc và vật liệu nâng nhà</Source></p>
                  <p className="mt-3"><strong>Xong khi:</strong> cầm đúng <strong>Pearl&apos;s Pearl</strong>. Giữ ngọc để gắn vào Crab King, không mang đi làm nguyên liệu khác.</p>
                </div>

                <div className="rounded-xl border border-nova-border p-5">
                  <h3>Bước 3 — Mở Ancient Archive, lấy máy dò</h3>
                  <ol>
                    <li>Xuống hang tìm <strong>Ruins</strong> (khu tàn tích cổ). Chế <strong>Star Caller&apos;s Staff</strong> và <strong>Deconstruction Staff</strong> tại trạm Ancient Pseudoscience Station phù hợp. Chuẩn bị ánh sáng, hồi máu và giáp trước khi khám phá.</li>
                    <li>Trên mặt đất, tìm và sửa <strong>Moon Stone</strong>. Vào đêm trăng tròn, cắm Star Caller&apos;s Staff vào đó, bảo vệ khỏi quái cho tới khi biến thành <strong>Moon Caller&apos;s Staff</strong>.</li>
                    <li>Dùng Deconstruction Staff tháo Moon Caller&apos;s Staff để lấy <strong>Iridescent Gem</strong>, viên ngọc cầu vồng. <Source page="Moon_Caller%27s_Staff">Cách chuyển gậy và lấy ngọc</Source></li>
                    <li>Trong hang, tìm <strong>Ancient Archive</strong> qua vùng <strong>Lunar Grotto</strong>. Gắn ngọc vào ổ còn trống của Archive Switch để cấp điện. <Source page="Guides/Summoning_Celestial_Champion">Mở Archive</Source></li>
                    <li>Lấy <strong>Distilled Knowledge từ đài phun màu xanh dương</strong>. Thả nó giữa vòng <strong>Ancient Orchestrina</strong>, thử các vòng ngoài để biết số, rồi bước theo thứ tự 1 đến 8. Giải xong sẽ nhận bản vẽ máy dò. <Source page="Archive_Orchestrina">Cách giải vòng số</Source> · <Source page="Fountain_of_Knowledge">Chọn đúng màu đài phun</Source></li>
                    <li>Học bản vẽ rồi chế <strong>Astral Detector</strong> bằng <strong>1 Moon Rock + 1 Thulecite</strong>. <Source page="Astral_Detector" /></li>
                  </ol>
                  <p className="mt-3"><strong>Xong khi:</strong> chế được Astral Detector. Đừng nhầm Moon Stone (công trình cắm gậy) với Moon Rock (nguyên liệu).</p>
                </div>

                <div className="rounded-xl border border-nova-border p-5">
                  <h3>Bước 4 — Gom hai bàn thờ còn lại</h3>
                  <p className="mt-3"><strong>Celestial Sanctum:</strong> đặt Astral Detector trên mặt đất, theo hướng nó chỉ và đặt tiếp ở vị trí mới. Đến gần nơi chôn, máy sẽ khoan lộ mảnh. Tìm đủ <strong>hai mảnh</strong>, vận chuyển về Lunar Island để lắp trên khe nứt. <Source page="Astral_Detector" /></p>
                  <p className="mt-3"><strong>Celestial Tribute:</strong> tìm <strong>Crab King</strong> ngoài biển, gắn Pearl&apos;s Pearl vào một ổ ngọc và lấp các ổ còn lại để bắt đầu trận. Phải thắng trận có gắn ngọc của Pearl mới lấy được vật phẩm nhiệm vụ. Dùng Pinchin&apos; Winch trục vớt <strong>Inactive Celestial Tribute</strong>, mang về đảo Mặt Trăng để hoàn thiện bàn thờ. <Source page="Pearl%27s_Pearl" /> · <Source page="Lunar_Altars">Lắp Tribute</Source></p>
                  <p className="mt-3"><strong>Chuẩn bị riêng cho Crab King:</strong> đồ sửa thuyền, giáp và hồi máu; nên đi cùng đồng đội lần đầu. Đây là một trận boss biển, không phải chỉ gắn ngọc rồi nhặt đồ. <Source page="Crab_King">Xem cách đánh Crab King</Source></p>
                  <p className="mt-3"><strong>Xong khi:</strong> Altar, Sanctum và Tribute hoàn chỉnh, đặt gần nhau thành tam giác. Giữa chúng xuất hiện <strong>Mysterious Energy</strong>, đồng thời mở sự kiện <strong>Moonstorm</strong>. <Source page="Mysterious_Energy" /></p>
                </div>

                <div className="rounded-xl border border-nova-border p-5">
                  <h3>Bước 5 — Gặp Wagstaff trong Moonstorm</h3>
                  <p className="mt-3">Tìm vùng bão Mặt Trăng trên bản đồ. Gặp Wagstaff để lấy bản vẽ <strong>Astroggles</strong> (kính dùng trong bão) và <strong>Incomplete Experiment</strong> (máy chưa hoàn chỉnh). Học bản vẽ, làm kính rồi quay lại theo ông ấy đến chỗ thí nghiệm.</p>
                  <p className="mt-3">Khi ông ấy làm việc, <strong>nhặt dụng cụ rơi quanh khu vực và đưa đúng món được yêu cầu</strong>, đồng thời bảo vệ máy khỏi chim. Nhân vật thường thấy tên dụng cụ khác tên Wagstaff gọi; đối chiếu bảng dưới. Thành công sẽ nhận <strong>Restrained Static</strong>. Nếu thất bại, tìm lại ông ấy để thử tiếp. <Source page="Grainy_Transmission">Nhiệm vụ trong Moonstorm</Source></p>
                  <dl className="mt-3 grid gap-2 rounded-lg bg-nova-surface-soft p-4 sm:grid-cols-2">
                    {[["Reticulating Buffer", "Odd Tool"], ["Widget Deflubber", "Weird Tool"], ["Grommet Scriber", "Strange Tool"], ["Conceptual Scrubber", "Funky Tool"], ["Calibrated Perceiver", "Bizarre Tool"]].map(([request, shown]) => <div key={request}><dt className="font-semibold text-nova-text">{request}</dt><dd>Nhặt: {shown}</dd></div>)}
                  </dl>
                  <p className="mt-3"><strong>Xong khi:</strong> có bản vẽ máy và 1 Restrained Static. Đây chưa phải Enlightened Shard để mở Rift.</p>
                </div>

                <div className="rounded-xl border border-nova-border p-5">
                  <h3>Bước 6 — Dựng Lunar Siphonator để gọi boss</h3>
                  <p className="mt-3">Trong Moonstorm, dùng <strong>Bug Net</strong> bắt Moongleam và dùng cuốc lấy <strong>Infused Moon Shard</strong>. Kiếm <strong>Scrap</strong> từ Junk Pile/Junky Fence; lấy <strong>Celestial Orb</strong> bằng cách đào Suspicious Boulder ở vùng thiên thạch. Tổng cần: <strong>8 Scrap, 15 Moongleam, 30 Infused Moon Shard, 2 Electrical Doodad, 1 Restrained Static và 1 Celestial Orb</strong>.</p>
                  <ol>
                    <li>Chế Incomplete Experiment với <strong>4 Scrap + 5 Moongleam + 2 Electrical Doodad</strong>, đặt trên Mysterious Energy giữa ba bàn thờ.</li>
                    <li>Nâng lần tiếp bằng <strong>4 Scrap + 10 Moongleam + 10 Infused Moon Shard</strong>.</li>
                    <li>Hoàn tất bằng <strong>1 Restrained Static + 1 Celestial Orb + 20 Infused Moon Shard</strong>. Boss xuất hiện ngay sau đó; chỉ nộp đủ đợt cuối khi cả đội đã sẵn sàng.</li>
                  </ol>
                  <p className="mt-3"><Source page="Lunar_Siphonator">Công thức và các giai đoạn máy</Source></p>
                </div>

                <div className="rounded-xl border border-nova-border p-5">
                  <h3>Bước 7 — Hạ đủ ba dạng Celestial Champion</h3>
                  <p className="mt-3"><strong>Gợi ý chuẩn bị:</strong> bãi đánh rộng, giáp và vũ khí dự phòng, nhiều đồ hồi máu, Walking Cane nếu có. Không đặt kho quan trọng sát nơi gọi boss.</p>
                  <ul className="mt-3 list-disc space-y-2 pl-5">
                    <li><strong>Dạng 1:</strong> né đường lăn và đập đất; tranh thủ đánh khi boss dừng. Khi nó gọi Gestalt và dựng thế phòng thủ, ưu tiên né để tránh bị ngủ.</li>
                    <li><strong>Dạng 2:</strong> chú ý đòn xoay truy đuổi và gai. Chủ động chạy khỏi đòn rồi mới quay lại đánh, không đứng giữ nút tấn công.</li>
                    <li><strong>Dạng 3:</strong> quan sát hướng laser, vòng bẫy và Gestalt; tìm khoảng trống trước khi áp sát. Đừng nhầm boss gục ở hai dạng đầu là trận đã kết thúc.</li>
                  </ul>
                  <p className="mt-3"><strong>Xong khi:</strong> dạng thứ ba bị hạ và Wagstaff xuất hiện gần tàn tích boss. <Source page="Celestial_Champion">Xem chi tiết đòn đánh từng dạng</Source></p>
                </div>

                <div className="rounded-xl border border-nova-accent/30 bg-nova-accent/5 p-5">
                  <h3>Bước 8 — Nhặt đúng mảnh và trao cho Wagstaff</h3>
                  <ol>
                    <li>Nhặt <strong>Enlightened Shard</strong> sau trận. Một mảnh rơi khi boss bị hạ; <strong>không bắt buộc phá Enlightened Crown</strong>. Nếu đã mất mảnh, Deconstruction Staff có thể tháo Crown thành 5 mảnh. <Source page="Enlightened_Shard" /></li>
                    <li>Đến <strong>Grainy Transmission</strong> cạnh máy hút năng lượng. Cầm mảnh và tương tác với ông ấy để cho xem, rồi trao mảnh khi được yêu cầu.</li>
                    <li>Đọc và xác nhận hộp thoại mở Rift. Nếu ông ấy biến mất trước khi bạn kịp trao, giữ mảnh và chờ lần xuất hiện khác trên mặt đất; không cần đánh lại boss chỉ vì lỡ cuộc gặp. <Source page="Grainy_Transmission">Trao mảnh sau trận</Source></li>
                  </ol>
                  <p className="mt-3"><strong>Phân biệt:</strong> Moon Shard, Infused Moon Shard và Enlightened Shard là ba vật phẩm khác nhau. Món Wagstaff cần ở bước này là <strong>Enlightened Shard</strong>.</p>
                </div>
              </div>
            </Section>

            <Section id="mo-rift" title="02. Mở Rift & nhận biết chu kỳ">
              <p>Sau khi hạ <strong>Celestial Champion</strong>, đưa <strong>Enlightened Shard</strong> cho <strong>Grainy Transmission (Wagstaff)</strong> và xác nhận mở Rift. Nếu ông ấy biến mất, giữ mảnh và tìm lần xuất hiện tiếp theo. Đây là bước thay đổi tiến trình thế giới, không chỉ mở một sự kiện tạm thời. <Source page="Grainy_Transmission" /></p>
              <p>Ở thiết lập mặc định, Rift đầu xuất hiện sau khoảng <strong>5 ngày</strong>. Xem biểu tượng trên bản đồ; Rift xuất hiện trên đất liền, không phải cổng dịch chuyển sang Lunar Island. <Source page="Lunar_Rift" /></p>
              <div className="grid gap-3 sm:grid-cols-3">
                {[["Giai đoạn 1", "Rift vừa xuất hiện. Chuẩn bị đường đi và vật tư."], ["Giai đoạn 2", "Bắt đầu khai thác Ryftstal quanh khe nứt."], ["Giai đoạn 3", "Brightshade bắt đầu xâm chiếm cây; đi kiểm tra khu trồng trọt."]].map(([title, text]) => <div key={title} className="rounded-xl border border-nova-border bg-nova-surface-soft p-4"><h3 className="font-semibold text-nova-text">{title}</h3><p className="mt-2">{text}</p></div>)}
              </div>
              <p>Mỗi lần chuyển giai đoạn mất khoảng <strong>4–5 ngày</strong>. Giai đoạn cuối có <strong>4–6 đợt Brightshade</strong>. Rift đóng rồi sẽ mở lại; tinh thể chưa đào biến mất không rơi đồ. <Source page="Lunar_Rift">Chu kỳ Rift</Source></p>
              <p><strong>Thiết lập server:</strong> Wild Rifts = Auto theo tiến trình; Always mở từ đầu; Never tắt. Wild Rift Frequency điều chỉnh thời gian chờ. <Source page="Lunar_Rift">Thiết lập Rift</Source></p>
            </Section>

            <Section id="chuan-bi" title="03. Chuẩn bị & hiểu sát thương planar">
              <ul className="list-disc space-y-2 pl-5">
                <li><strong>Đi đào:</strong> cuốc còn bền, đồ hồi máu, giáp, thức ăn, nguồn sáng và ô túi trống.</li>
                <li><strong>Đi đánh:</strong> thêm vũ khí dự phòng, đồ tăng tốc nếu có, kế hoạch rút lui và hồi sinh.</li>
                <li><strong>Đánh theo đội:</strong> một người dụ đòn, người còn lại quan sát và hỗ trợ; tránh cùng lao vào cây đang phản đòn.</li>
              </ul>
              <div className="rounded-xl border border-nova-accent/25 bg-nova-accent/5 p-4">
                <h3 className="font-semibold text-nova-text">Giáp vật lý cao chưa đủ</h3>
                <p className="mt-2">Đòn đánh có thể gồm <strong>vật lý + planar</strong>. Giáp thường giảm phần vật lý; muốn giảm planar cần chỉ số <strong>Planar Defense</strong>. Phòng thủ planar của đồ đội đầu và áo có thể cộng lại. Quái có <strong>Planar Entity Protection</strong> lại giảm sát thương vật lý bạn gây ra, nên vũ khí planar hữu ích khi săn chúng. <Source page="Guides/Planar_Damage">Giải thích planar</Source></p>
              </div>
              <p>Khu vực mặt đất quanh Rift dùng <strong>Enlightenment</strong> thay Sanity. Gestalt có thể làm chậm và gây ngủ khi Enlightenment cao; đừng xem thanh đầy là luôn an toàn. <Source page="Gestalt" /></p>
            </Section>

            <Section id="nguyen-lieu" title="04. Hai nguyên liệu phải phân biệt">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-xl bg-nova-surface-soft p-5"><div className="flex items-center gap-3"><ItemIcon prefab="purebrilliance" /><h3 className="text-lg font-semibold text-nova-text">Pure Brilliance</h3></div><p className="mt-3">Đào <strong>Ryftstal</strong> quanh Rift bằng cuốc. Cuốc thường dùng được nhưng bị bật lại trong quá trình đào; nâng cấp Smasher khi đã có nguyên liệu. <Source page="Lunar_Rift">Khai thác tinh thể</Source></p></div>
                <div className="rounded-xl bg-nova-surface-soft p-5"><div className="flex items-center gap-3"><ItemIcon prefab="lunarplant_husk" /><h3 className="text-lg font-semibold text-nova-text">Brightshade Husk</h3></div><p className="mt-3">Hạ <strong>Deadly Brightshade</strong>: mỗi cây rơi <strong>2 Husk + 2 Leafy Meat</strong>. Tìm ở khu cây trồng bị chiếm, không chỉ quanh Rift. <Source page="Deadly_Brightshade">Nguồn Husk</Source></p></div>
              </div>
              <p><strong>Gợi ý quản lý:</strong> chia kho thành nguyên liệu chế mới và nguyên liệu sửa đồ. Sau mỗi chuyến, bù lại số Repair Kit đã dùng trước khi đầu tư món tiếp theo.</p>
            </Section>

            <Section id="vat-pham" title="05. Brightsmithy, vật phẩm & thứ tự chế">
              <p>Đứng cạnh một <strong>Lunar Altar đã lắp hoàn chỉnh</strong> để chế <strong>Brightsmithy Kit</strong>: <strong>5 Moon Rock + 5 Moon Shard + 1 Pure Brilliance</strong>. Đặt kit xuống để dựng trạm. Các món dưới đây cần chế tại Brightsmithy; chế một lần không đồng nghĩa mở công thức ở mọi nơi. <Source page="Brightsmithy" /></p>
              <div className="overflow-x-auto rounded-xl border border-nova-border focus-visible:outline-2 focus-visible:outline-nova-accent" tabIndex={0} role="region" aria-label="Bảng vật phẩm Brightshade, cuộn ngang trên màn hình nhỏ">
                <table className="w-full min-w-[42rem] border-collapse text-left text-sm">
                  <caption className="bg-nova-surface-soft px-4 py-3 text-left text-xs">Husk trong bảng = Brightshade Husk. Công thức thường, chưa áp dụng giảm chi phí chế tạo.</caption>
                  <thead className="bg-nova-surface-soft text-nova-text"><tr>{["Vật phẩm", "Nguyên liệu", "Công dụng / khi nên chế"].map(title => <th key={title} scope="col" className="px-4 py-3 font-semibold">{title}</th>)}</tr></thead>
                  <tbody>{equipment.map(item => <tr key={item.prefab} className="border-t border-nova-border align-top"><th scope="row" className="w-48 px-4 py-4"><div className="flex items-center gap-3"><ItemIcon prefab={item.prefab} /><Source page={item.name.replaceAll(" ", "_")}>{item.name}</Source></div></th><td className="w-44 px-4 py-4">{item.cost}</td><td className="px-4 py-4"><span className="mb-2 inline-block rounded-full bg-nova-accent/10 px-2.5 py-0.5 text-xs font-semibold text-nova-accent">{item.priority}</span><p>{item.use}</p></td></tr>)}</tbody>
                </table>
              </div>
              <p><strong>Brightshade Repair Kit:</strong> 1 Pure Brilliance + 1 Brightshade Husk tại Brightsmithy. Dùng để sửa đầy độ bền trang bị Brightshade phù hợp. Helm, Armor, Sword và Staff hết bền sẽ không biến mất, nhưng phải sửa mới dùng lại được. <a href="https://www.dstcraft.com/item/brightshade-repair-kit" target="_blank" rel="noreferrer" className="text-nova-accent underline underline-offset-4">Công thức Repair Kit ↗</a> · <Source page="Brightshade_Sword">Cơ chế sửa đồ</Source></p>
              <p><strong>Lộ trình gợi ý:</strong> Helm → Sword cho cận chiến hoặc Staff cho đánh nhóm → Armor → công cụ. Người chưa quen né đòn có thể lấy Armor sớm hơn. Luôn giữ nguyên liệu sửa đồ.</p>
              <p><strong>Dự toán bộ cận chiến:</strong> trạm + Helm + Sword + Armor + 2 Repair Kit cần <strong>15 Pure Brilliance, 11 Husk, 5 Moon Rock và 5 Moon Shard</strong>, chưa tính giảm chi phí. Đây là tổng cộng từ các công thức trên.</p>
            </Section>

            <Section id="brightshade" title="06. Cách đánh Brightshade & giữ vườn an toàn">
              <ol className="list-decimal space-y-2 pl-5">
                <li><strong>Dụ dây leo ra trước.</strong> Khi Tunneling Vine còn sống, cây chính phản đòn nếu bị đánh ở gần.</li>
                <li><strong>Hạ dây leo.</strong> Cây mở nụ và ngừng phản đòn khoảng 9 giây.</li>
                <li><strong>Đánh trong cửa sổ an toàn.</strong> Cây bắt đầu rung sau khoảng 5 giây; chủ động lùi, đừng tham thêm đòn cuối.</li>
                <li><strong>Lặp lại.</strong> Dọn từng cây, hồi máu giữa các lượt. Có Staff thì tận dụng tầm xa và các mục tiêu gần nhau.</li>
              </ol>
              <p>Brightshade ưu tiên cây đã di dời và cây nông nghiệp. <strong>Gợi ý bố trí:</strong> dành khu trồng trọt có lối chạy rộng, tách khỏi nơi mở rương và chế đồ để dễ xử lý khi bị chiếm. <Source page="Deadly_Brightshade">Cơ chế và chiến thuật Brightshade</Source></p>
            </Section>

            <Section id="boss" title="07. Ba boss đột biến nên biết">
              <p>Khi Rift đang hoạt động, xác Deerclops, Bearger hoặc Varg trên mặt đất có thể bị Gestalt nhập và hồi sinh thành boss đột biến. Nếu chưa muốn đánh tiếp, đốt xác trước khi bị nhập có thể ngăn biến đổi. <Source page="Armored_Bearger">Điều kiện biến đổi</Source></p>
              <div className="space-y-4">{bosses.map(boss => <div key={boss.name} className="rounded-xl border border-nova-border p-5"><p className="text-xs font-semibold uppercase tracking-wide text-nova-faint">{boss.from} →</p><h3 className="mt-1 text-lg font-semibold text-nova-text">{boss.name}</h3><p className="mt-2">{boss.tip}</p><p className="mt-2 text-xs"><Source page={boss.name.replaceAll(" ", "_")}>Xem đòn đánh và phần thưởng</Source></p></div>)}</div>
              <p><strong>Trước khi vào trận:</strong> sửa giáp, mang nguồn gây planar, chọn bãi trống xa căn cứ và thống nhất đường rút. Không cố đánh cả hai dạng boss liên tục khi đã cạn hồi máu.</p>
            </Section>

            <Section id="tien-trinh" title="08. Sau bộ Brightshade: đi tiếp thế nào?">
              <p>Săn đủ ba loại boss đột biến là một phần nhiệm vụ của Wagstaff để nhận <strong>Spark Ark</strong>. Theo tiếp lời hướng dẫn của ông ấy; Spark Ark mở nhánh công nghệ với các món như <strong>Howlitzer, Polar Bearger Bin và Ice Crystaleyezer</strong>. <Source page="Grainy_Transmission">Nhiệm vụ Wagstaff</Source> · <Source page="Spark_Ark" /></p>
              <p>Nhánh Lunar còn đi tiếp tới <strong>W.A.R.B.O.T. và Celestial Scion</strong>. Hãy xem đây là mục tiêu sau khi đã chủ động nguồn sửa đồ và đánh boss, không phải điều kiện để bắt đầu farm Rift. <Source page="Celestial_Scion">Nhánh boss tiếp theo</Source></p>
              <p>Sau Celestial Scion, phần thưởng của boss đột biến có thay đổi, gồm <strong>Nucleation Fluid</strong>; đừng áp dụng nguyên xi hướng dẫn Spark Ark cũ cho thế giới đã qua mốc này. <Source page="Armored_Bearger">Phần thưởng sau Scion</Source></p>
            </Section>

            <Section id="hoi-dap" title="09. Các tình huống thường gặp">
              {[
                ["Có nhiều Pure Brilliance nhưng không có Husk?", <>Bạn đang đào tinh thể, chưa săn cây. Quay lại khu cây trồng khi Rift ở giai đoạn cuối để tìm Deadly Brightshade. <Source page="Deadly_Brightshade" /></>],
                ["Giáp vẫn còn mà mất máu rất nhanh?", <>Kiểm tra Planar Defense, không chỉ phần trăm giáp. Tách dây leo trước khi đánh cây và dừng đánh khi cây hết choáng. <Source page="Guides/Planar_Damage">Phòng thủ planar</Source></>],
                ["Cầm kiếm sáng có đi đêm được không?", <>Brightshade Sword không phải nguồn sáng. Brightshade Helm đang hoạt động mới có khả năng ngăn Charlie; vẫn nên mang nguồn sáng để quan sát đường và phòng lúc mũ hết bền. <Source page="Brightshade_Sword" /> · <Source page="Brightshade_Helm" /></>],
                ["Vì sao đứng ở base không chế được đồ Brightshade?", <>Cần đứng sát Brightsmithy, mang đúng nguyên liệu và kiểm tra bộ lọc chế tạo. Trạm Alchemy Engine không thay thế Brightsmithy. <Source page="Brightsmithy" /></>],
                ["Server Tu Tiên khác số liệu trong bài?", <>Bài mô tả DST gốc. Hãy đối chiếu mô tả vật phẩm và cấu hình server đang chơi; không dùng chỉ số mod để suy ra cơ chế chuẩn của Rift.</>],
              ].map(([question, answer], index) => <details key={index} className="rounded-xl border border-nova-border p-4"><summary className="cursor-pointer rounded-md font-semibold text-nova-text focus-visible:outline-2 focus-visible:outline-nova-accent">{question}</summary><p className="mt-3">{answer}</p></details>)}
              <p className="border-t border-nova-border pt-4 text-xs">Nguồn được gắn trực tiếp tại từng mục và tên vật phẩm. Công thức công cụ và bom được đối chiếu thêm với danh mục vật phẩm DST của website. Thứ tự chế đồ, cách chia vật tư và bố trí bãi đánh là gợi ý thực hành.</p>
            </Section>
            <a href="#bat-dau" className="inline-flex min-h-11 items-center text-sm font-semibold text-nova-accent underline underline-offset-4">↑ Về đầu hướng dẫn</a>
          </article>
        </div>
      </div>
    </DstPageShell>
  </div>;
}
