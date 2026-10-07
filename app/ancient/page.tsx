import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";

export const metadata: Metadata = {
  title: "Ancient: Ruins, Fuelweaver và các tuyến boss | DST Wiki",
  description: "Guide Ancient tiếng Việt từ đầu: tìm Ruins, đánh Ancient Guardian, lấy Shadow Atrium, triệu hồi Fuelweaver, mở Shadow Rift và chọn tuyến boss tiếp theo.",
};

const chapters = [
  ["bat-dau", "Hiểu tuyến Ancient"], ["xuong-ruins", "Chuyến đầu xuống Ruins"],
  ["guardian", "Ancient Guardian & Key"], ["trieu-hoi", "Chuẩn bị triệu hồi"],
  ["fuelweaver", "Đánh Ancient Fuelweaver"], ["vat-pham", "Đồ nên lấy & chế"],
  ["shadow-rift", "Mở Shadow Rift"], ["boss-khac", "Các tuyến boss khác"],
  ["hoi-dap", "Kẹt ở đâu?"],
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

const equipment = [
  { name: "Thulecite Club / Crown / Suit", page: "Thulecite", use: "Bộ chiến đấu từ Thulecite. Chế tại Ancient Pseudoscience Station; chọn món theo nguyên liệu và trang bị hiện có.", priority: "Chuyến Ruins đầu" },
  { name: "Magiluminescence", page: "Magiluminescence", use: "Dây chuyền phát sáng và tăng tốc, tiện khám phá. Cần tiếp nhiên liệu; vẫn mang nguồn sáng dự phòng.", priority: "Di chuyển & khám phá" },
  { name: "The Lazy Explorer", page: "The_Lazy_Explorer", use: "Gậy dịch chuyển, hữu ích để thoát lồng xương Fuelweaver. Dành sẵn độ bền cho trận đánh.", priority: "Trước Fuelweaver" },
  { name: "Nightmare Amulet", page: "Nightmare_Amulet", use: "Giả lập trạng thái mất trí để đánh Unseen Hands. Chiếm ô thân: khi đeo, giáp thân bị thay ra, nên giữ mũ bảo vệ.", priority: "Cơ chế phá khiên" },
  { name: "Weather Pain", page: "Weather_Pain", use: "Lốc đánh diện rộng để dọn Woven Shadows đang bò về hồi máu boss. Cần Down Feather, Volt Goat Horn và Gears.", priority: "Cơ chế chống hồi máu" },
  { name: "Bone Armor", page: "Bone_Armor", use: "Đồ rơi Fuelweaver: chặn một lần sát thương mỗi 5 giây. Giữa hai lần chặn không có giảm sát thương sẵn, nên kết hợp mũ giáp; không thay nguồn sáng.", priority: "Phần thưởng boss" },
  { name: "Bone Helm / Shadow Thurible", page: "Ancient_Fuelweaver", use: "Hai phần thưởng khác của Fuelweaver. Đọc hiệu ứng từng món trước khi dùng; Bone Helm liên quan trạng thái mất trí, Thurible dùng với Reanimated Skeleton.", priority: "Tiện ích sau boss" },
];

const routes = [
  { name: "Lunar / Mặt Trăng", path: "Pearl + Ancient Archive + Crab King → ba bàn thờ → Moonstorm → Celestial Champion → Lunar Rift", reward: "Brightshade, boss đột biến và chuỗi Wagstaff về sau.", page: "Celestial_Champion" },
  { name: "Shadow / Ancient", path: "Ruins → Ancient Guardian; Shadow Pieces → Shadow Atrium; hai nhánh hội tụ ở Atrium → Fuelweaver → Shadow Rift", reward: "Đồ Ancient, Bone Armor, nguyên liệu và trang bị Shadow.", page: "Ancient_Fuelweaver" },
  { name: "Nightmare Werepig", path: "Tìm Werepig bị xích trong hang → giải phóng → hạ boss; tiếp nối với Scrappy Werepig trên mặt đất", reward: "Pure Horror, blueprint Dreadstone; Dreadstone lấy từ cột bị boss phá.", page: "Nightmare_Werepig" },
  { name: "Bee Queen", path: "Tìm Gigantic Beehive → dùng búa để gọi boss → xử lý đàn Grumble Bees và hạ nữ hoàng", reward: "Royal Jelly để làm Jellybeans, Bee Queen Crown và blueprint Bundling Wrap.", page: "Bee_Queen" },
  { name: "Dragonfly", path: "Tìm vùng hồ dung nham ở sa mạc → chuẩn bị sân đánh và đối phó Lavae → hạ Dragonfly", reward: "Scales và blueprint Scaled Furnace. Là nhánh săn đồ độc lập.", page: "Dragonfly" },
  { name: "Klaus", path: "Mùa đông: lấy Deer Antler → dùng trên Loot Stash → đánh hai dạng Klaus → dùng Stag Antler mở túi", reward: "Loot Stash có nhiều đồ quý. Tránh giết hai Gem Deer vì khiến Klaus nổi giận.", page: "Klaus" },
  { name: "Terraria", path: "Lấy Terrarium trong Conspicuous Chest → kích hoạt ban đêm; cho Nightmare Fuel trước khi kích hoạt để gọi Twins", reward: "Eye of Terror hoặc Twins of Terror. Không bắt buộc giết Eye trước mới gọi được Twins.", page: "Terrarium" },
  { name: "Toadstool", path: "Tìm mũ nấm trong hang → chặt để gọi Toadstool; biến thể Misery cần Volatile Canary nổ cạnh mũ trước", reward: "Nhánh boss khó tùy chọn, có Mushroom Skin và blueprint liên quan.", page: "Toadstool" },
  { name: "Ancient Sanctum", path: "Khám phá Sanctum → phòng khóa với Pulse Cradles → Ancient Guard Tower → Keystone", reward: "Nhánh Ancient riêng. Ancient Guard Tower không phải Ancient Guardian trong Labyrinth.", page: "Ancient_Guard_Tower" },
];

export default function AncientPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
    <SiteHeader active="bosses" />
    <DstPageShell>
      <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
        <Link href="/bosses" className="mb-5 inline-flex min-h-11 items-center text-sm font-semibold text-nova-accent underline underline-offset-4">← Lộ trình boss</Link>
        <DstHero eyebrow="Cẩm nang sinh tồn • Don't Starve Together" title="Ancient & Shadow" description="Từ chuyến xuống Ruins đầu tiên đến Ancient Fuelweaver: tìm đường, gom đúng vật phẩm, hiểu cơ chế boss và mở Shadow Rift." stats={[{ label: "Bắt đầu", value: "Khám phá Ruins" }, { label: "Đích đến", value: "Fuelweaver & Rift" }]} statsAriaLabel="Phạm vi hướng dẫn">
          <p className="text-sm leading-6 text-nova-muted">Cơ chế DST gốc • Đối chiếu nguồn ngày <time dateTime="2026-10-07">07/10/2026</time>. Server Tu Tiên có thể đổi chỉ số, công thức và thiết lập thế giới.</p>
        </DstHero>
        <div className="mt-8 grid items-start gap-6 lg:grid-cols-[14rem_minmax(0,1fr)]">
          <aside className="rounded-2xl border border-nova-border bg-nova-surface p-4 lg:sticky lg:top-6">
            <p className="px-3 text-xs font-semibold uppercase tracking-wider text-nova-faint">Trong trang này</p>
            <nav aria-label="Mục lục Ancient" className="mt-3 grid gap-1 sm:grid-cols-2 lg:grid-cols-1">
              {chapters.map(([id, label], index) => <a key={id} href={`#${id}`} className="flex min-h-11 items-center gap-3 rounded-lg px-3 py-2 text-sm text-nova-muted hover:bg-nova-surface-soft hover:text-nova-text focus-visible:outline-2 focus-visible:outline-nova-accent"><span className="text-xs text-nova-faint">{String(index + 1).padStart(2, "0")}</span>{label}</a>)}
            </nav>
            <Link href="/lunar-rift" className="mt-3 block rounded-lg bg-nova-accent/10 px-3 py-3 text-sm font-semibold text-nova-accent underline underline-offset-4">Đọc tuyến Lunar Rift →</Link>
          </aside>
          <article aria-label="Hướng dẫn Ancient" className="min-w-0 space-y-6">
            <Section id="bat-dau" title="01. Hiểu tuyến Ancient trước khi đi">
              <p><strong>Bạn có thể xuống Ruins lấy đồ rồi về, chưa cần đánh Fuelweaver.</strong> Chuyến đầu nên tập trung tìm đường, đánh dấu trạm chế tạo và mang Thulecite về an toàn.</p>
              <ol className="grid list-inside list-decimal gap-3 sm:grid-cols-2">
                {["Xuống Caves → tìm Ruins → khai thác và chế trang bị Ancient.", "Tìm Labyrinth → hạ Ancient Guardian → lấy Ancient Key.", "Trên mặt đất: đánh Shadow Pieces lấy Shadow Atrium. Trong hang: gom 8 Fossil Fragments.", "Tìm Atrium → lắp Key vào Gateway → dựng bộ xương → gắn Shadow Atrium để gọi Fuelweaver.", "Hạ Fuelweaver → nhận đồ và tái tạo Ruins.", "Khi sẵn sàng: đưa 5 Dreadstone cho Beckoning Hand để mở chu kỳ Shadow Rift."].map(text => <li key={text} className="rounded-xl bg-nova-surface-soft p-4">{text}</li>)}
              </ol>
              <p><strong>Ba nơi khác nhau:</strong> Ruins là khu tàn tích trong hang; Atrium là nơi gọi Fuelweaver; Ancient Archive thuộc chuỗi Mặt Trăng. Tên đều “Ancient” không có nghĩa phải đi hết chúng theo một đường thẳng. <Source page="Ruins/DST" /> · <Source page="Atrium" /></p>
            </Section>

            <Section id="xuong-ruins" title="02. Chuyến đầu xuống Ruins">
              <h3 className="text-lg font-semibold text-nova-text">Mang gì trước khi rời nhà?</h3>
              <ul className="list-disc space-y-2 pl-5">
                <li><strong>Ánh sáng:</strong> Lantern hoặc Miner Hat, nhiên liệu và nguồn sáng dự phòng. Đừng đi sâu chỉ với một cây Torch.</li>
                <li><strong>Chiến đấu:</strong> vũ khí, vài mũ/giáp dự phòng, đồ hồi máu và thức ăn. Chừa đồ hồi Sanity để xử lý lúc cần tỉnh táo.</li>
                <li><strong>Khai thác:</strong> Pickaxe, Hammer, đồ thay thế và chỗ trống trong túi. Thulecite, Gems và Gears thường đáng ưu tiên hơn đá thường.</li>
                <li><strong>Đường về:</strong> đánh dấu cửa hang, chỗ rẽ, trạm Ancient và lối vào Labyrinth trên bản đồ; đặt điểm tập kết ở nơi đã dọn quái.</li>
              </ul>
              <h3 className="text-lg font-semibold text-nova-text">Tìm và nhận biết Ruins</h3>
              <p>Phá đá bịt Sinkhole rồi xuống hang. Trong DST, Ruins nằm <strong>cùng tầng Caves</strong>; không cần tìm cầu thang xuống tầng hai như bản Don’t Starve đơn. Khám phá các nhánh sâu để tìm nền tàn tích, tượng Ancient, clockwork hỏng và khu Splumonkey; không có hướng trái/phải cố định cho mọi bản đồ.</p>
              <p><strong>Đừng đứng farm xuyên Nightmare Phase.</strong> Khi chu kỳ ác mộng mạnh lên, quái bóng có thể tấn công dù Sanity còn cao. Ánh sáng đỏ từ nền không thay được đèn. Lùi về khu đã an toàn và chờ là lựa chọn hợp lý cho lần đầu. <Source page="Ruins/DST" /></p>
              <p>Tìm <strong>Ancient Pseudoscience Station</strong> để chế đồ; trạm hỏng chỉ có một phần công thức, dùng Thulecite sửa để mở thêm. Đa số đồ Ancient phải chế cạnh trạm, không học một lần rồi mang về nhà chế thoải mái. <Source page="Ancient_Pseudoscience_Station" /></p>
            </Section>

            <Section id="guardian" title="03. Ancient Guardian: lấy chiếc chìa khóa đầu tiên">
              <p><strong>Ancient Guardian</strong> là con quái một sừng ở cuối Labyrinth. Đây là boss lấy chìa khóa; Ancient Fuelweaver là một trận khác, ở Atrium.</p>
              <ol className="list-decimal space-y-2 pl-5">
                <li>Dọn đường và kiểm tra ánh sáng, giáp, đồ hồi máu trước khi vào đấu trường.</li>
                <li>Dụ cú lao của Guardian vào <strong>Ruins Pillar hoặc Blocky Ruin</strong>. Khi nó choáng, tiến vào đánh rồi rút; đừng đứng chắn đường lao để đổi máu.</li>
                <li>Ở giai đoạn sau, né cú nhảy đập và tận dụng thời gian nó choáng. Tránh Shadow Tentacles; chúng không phải mục tiêu cần giết.</li>
                <li>Sau chiến thắng, mở <strong>Large Ornate Chest</strong> lấy <strong>Ancient Key</strong>. Cất kỹ để mang đến Ancient Gateway.</li>
              </ol>
              <p>Không cần ép bản thân nhớ một số lần đánh cố định: tốc độ nhân vật, vũ khí và độ trễ server làm nhịp né khác nhau. Ưu tiên nhận ra đòn lao và cửa sổ choáng. <Source page="Ancient_Guardian/DST" /> · <Source page="Ancient_Key" /></p>
            </Section>

            <Section id="trieu-hoi" title="04. Từ Ancient Key đến triệu hồi Fuelweaver">
              <p className="rounded-xl bg-nova-accent/5 p-4"><strong>Danh sách bắt buộc:</strong> Ancient Key + Shadow Atrium + 8 Fossil Fragments + tìm đúng Ancient Gateway trong Atrium. Chỉ có chiếc chìa khóa là chưa đủ.</p>
              <h3 className="text-lg font-semibold text-nova-text">A. Shadow Atrium: “trái tim” từ Shadow Pieces</h3>
              <p>Trên mặt đất, tìm bộ tượng cẩm thạch Knight, Bishop và Rook. Mang các <strong>Suspicious Marble</strong> tương ứng về sửa tượng. Vào <strong>đêm trăng non — New Moon</strong>, khai thác tượng đã sửa để gọi Shadow Pieces. Cũng có thể dùng bộ Chess Pieces đã chế rồi đập bằng búa vào trăng non; không dùng tượng Moon Shard thay thế. <Source page="Set_Piece/DST" /></p>
              <p>Cần đủ <strong>ba loại Knight, Bishop, Rook</strong> trong cùng cuộc giao chiến: khi một loại chết, các loại còn lại ở gần tăng cấp. Hạ con đạt cấp 3 để nhận Shadow Atrium. Hãy chuẩn bị tốc độ di chuyển và khoảng trống từ trước, vì con cuối mạnh hơn nhiều. <strong>Trăng tròn không phải điều kiện gọi Shadow Pieces.</strong> <Source page="Shadow_Pieces" /></p>
              <h3 className="text-lg font-semibold text-nova-text">B. Fossil Fragments: đủ 8 mảnh hóa thạch</h3>
              <p>Khai thác <strong>Spilagmites</strong> để lấy Fossil Fragment; Stalagmites thường chỉ có cơ hội rơi. Bone Shards không dùng thay được. Đặt mảnh đầu xuống đất rồi thêm đủ 7 mảnh còn lại để dựng Odd Skeleton. Mang Shadow Atrium ở gần lúc dựng giúp ra đúng bộ xương; nếu dựng sai hình, đập bằng búa để thu hồi các mảnh rồi làm lại. <Source page="Fossils" /></p>
              <h3 className="text-lg font-semibold text-nova-text">C. Tìm Atrium và Ancient Gateway</h3>
              <p>Tìm <strong>Big Tentacle / Tentapillar</strong> trong hang, đánh cho nó rút xuống rồi chui vào Big Slimy Pit. Các hố nối sang vị trí khác; lối Atrium gắn với một khu có hai Damaged Bishops và dấu tích Ancient. Ghi lại các cặp lối đi đã thử. <Source page="Big_Tentacle/DST" /> · <Source page="Set_Piece/DST" /></p>
              <p>Đường chính trong Atrium có <strong>Insanity Obelisks</strong>: cần Sanity ở mức 15% trở xuống để đi qua; Nightmare Amulet cũng hữu ích. Đừng nhầm với loại obelisk cần tỉnh táo. Sau khi qua, phục hồi Sanity nếu cần và đi đến Gateway. <Source page="Obelisk/DST" /></p>
              <h3 className="text-lg font-semibold text-nova-text">D. Làm đúng thứ tự tại đấu trường</h3>
              <ol className="list-decimal space-y-2 pl-5">
                <li>Cắm Ancient Key vào <strong>Ancient Gateway</strong>.</li>
                <li>Dựng bộ xương đúng hình bằng 8 Fossil Fragments <strong>trong Atrium, gần Gateway đã kích hoạt</strong>.</li>
                <li>Đặt đèn và chuẩn bị thanh vật phẩm nhanh: hồi máu, Nightmare Amulet, đồ dịch chuyển, đồ đánh diện rộng.</li>
                <li>Gắn <strong>Shadow Atrium</strong> vào bộ xương để bắt đầu trận. Đừng gắn khi đồng đội còn chưa đến nơi.</li>
              </ol>
              <p><Source page="Ancient_Fuelweaver" /> · <Source page="Shadow_Atrium" /></p>
            </Section>

            <Section id="fuelweaver" title="05. Fuelweaver: phải xử lý cơ chế, không chỉ đánh mạnh">
              <p>Đây là trận khó, đặc biệt khi chơi một mình. Trước khi gọi boss, tập đổi nhanh giữa vũ khí, Nightmare Amulet và công cụ dịch chuyển.</p>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-xl bg-nova-surface-soft p-4"><h3 className="font-semibold text-nova-text">Bị nhốt trong lồng xương</h3><p>Dùng The Lazy Explorer hoặc kỹ năng thoát phù hợp nhân vật. Giữ sẵn lượt sử dụng; đứng kẹt trong lồng khiến bạn khó né đòn tiếp theo.</p></div>
                <div className="rounded-xl bg-nova-surface-soft p-4"><h3 className="font-semibold text-nova-text">Bóng nhỏ bò về boss</h3><p>Đó là Woven Shadows, mỗi con lọt vào sẽ hồi máu boss. Dùng Weather Pain hoặc sát thương diện rộng để dọn trước khi tiếp tục đánh.</p></div>
                <div className="rounded-xl bg-nova-surface-soft p-4"><h3 className="font-semibold text-nova-text">Boss có khiên, đánh không mất máu</h3><p>Đeo Nightmare Amulet để thấy và đánh Unseen Hands. Dọn các bàn tay để phá khiên rồi tháo amulet, trở lại chiến đấu.</p></div>
                <div className="rounded-xl bg-nova-surface-soft p-4"><h3 className="font-semibold text-nova-text">Mất kiểm soát khi đang điên</h3><p>Fuelweaver có Mind Control ở giai đoạn sau. Tránh giữ trạng thái mất trí liên tục: tháo amulet, hồi Sanity và giữ ánh sáng.</p></div>
              </div>
              <p><strong>Nhịp ưu tiên:</strong> thoát nguy hiểm → chặn hồi máu → phá khiên → gây sát thương. Nếu đi nhóm, phân công người dọn bóng và người xử lý bàn tay. <Source page="Ancient_Fuelweaver" /></p>
            </Section>

            <Section id="vat-pham" title="06. Đồ nên lấy, chế và giữ lại">
              <div className="grid gap-3 sm:grid-cols-2">
                {equipment.map(item => <div key={item.name} className="rounded-xl border border-nova-border p-4"><p className="text-xs font-semibold uppercase tracking-wide text-nova-faint">{item.priority}</p><h3 className="mt-1 font-semibold text-nova-text">{item.name}</h3><p className="mt-2">{item.use}</p><Source page={item.page}>Xem vật phẩm</Source></div>)}
              </div>
              <p><strong>Sau Fuelweaver:</strong> Ruins được tái tạo, gồm nhiều tài nguyên và Ancient Guardian. Theo thiết lập mặc định, Gateway có thời gian chờ 20 ngày trước lần kích hoạt tiếp theo. Chuẩn bị lại Shadow Atrium cho lần đánh mới vì trái tim bị tiêu thụ khi thắng trận. <Source page="Ancient_Gateway" /> · <Source page="Shadow_Atrium" /></p>
            </Section>

            <Section id="shadow-rift" title="07. Mở Shadow Rift: Dreadstone lấy ở đâu?">
              <p>Sau khi hạ Fuelweaver, <strong>Beckoning Hand</strong> xuất hiện ở Ancient Gateway. Trao <strong>5 Dreadstone</strong> cho bàn tay để mở tiến trình Shadow Rift trong hang. Đây là thay đổi tiến trình lâu dài của thế giới; bạn có thể để bàn tay chờ đến khi cả nhóm sẵn sàng. <Source page="Shadow_Rift" /></p>
              <h3 className="text-lg font-semibold text-nova-text">Chưa mở Rift vẫn lấy được Dreadstone</h3>
              <ol className="list-decimal space-y-2 pl-5">
                <li>Tìm <strong>Nightmare Werepig bị xích</strong> trong khu hang có nền bùn và Light Flowers.</li>
                <li>Dùng cuốc bóc lớp ngoài của ba Cracked Pillars. Sau đó dùng công cụ mạnh như <strong>Pick/Axe</strong> tác động để cả ba cột cùng rung, giải phóng boss. Không bắt buộc phải có đồ Lunar trước.</li>
                <li>Khi vừa thoát xích, Werepig chưa nhận sát thương. Hạ Sanity hoặc đeo <strong>Nightmare Amulet</strong> để đánh các <strong>Parasitic Shadelings</strong> nó hất ra; dọn chúng để chuyển sang giai đoạn chiến đấu.</li>
                <li>Trong trận, <strong>dụ cú đập đất của Werepig phá cột</strong> để lấy Dreadstone. Đá này đến từ cột; phần thưởng boss có Pure Horror và blueprint Dreadstone.</li>
                <li>Gom đủ 5 Dreadstone, trở lại Beckoning Hand tại Gateway.</li>
              </ol>
              <p><Source page="Nightmare_Werepig" /> · <Source page="Cracked_Pillar" /></p>
              <h3 className="text-lg font-semibold text-nova-text">Sau khi Rift hoạt động, farm gì?</h3>
              <ul className="list-disc space-y-2 pl-5">
                <li><strong>Pure Horror và Dark Tatters:</strong> nhận từ Ink Blights. Pure Horror cũng có nguồn trước Rift là Nightmare Werepig. Đừng nhầm với Nightmare Fuel thường. <Source page="Ink_Blight" /></li>
                <li><strong>Dreadstone:</strong> khai thác Dreadstone Outcrops gần Nightmare Fissures khi Rift hoạt động. Chuẩn bị công cụ mạnh và chú ý outcrop có thể biến mất khi nhóm canh giữ bị dọn hết. <Source page="Dreadstone_Outcrop" /></li>
                <li><strong>Shadowcraft Plinth:</strong> chế kit tại trạm Ancient bằng 5 Nightmare Fuel + 2 Dreadstone + 1 Pure Horror, đặt xuống rồi đứng cạnh để chế đồ Shadow. <Source page="Shadowcraft_Plinth" /></li>
                <li><strong>Trang bị:</strong> xem Void Robe, Void Cowl và Shadow Reaper. Chú ý phòng thủ planar khi bước sang các trận cuối game; giáp vật lý cao không thay thế hoàn toàn phòng thủ planar. <Source page="Void_Robe" /></li>
              </ul>
            </Section>

            <Section id="boss-khac" title="08. Ngoài Ancient còn những tuyến boss nào?">
              <Link href="/bosses" className="block rounded-xl bg-nova-accent/10 p-4 font-semibold text-nova-accent underline underline-offset-4">Muốn đi hết? Mở lộ trình tổng và guide chi tiết từng tuyến →</Link>
              <p><strong>Có hai tuyến tiến trình lớn là Lunar và Shadow; nhiều boss khác là nhánh săn đồ độc lập.</strong> Bảng này là bản đồ chọn mục tiêu, không phải thứ tự bắt buộc phải giết mọi boss.</p>
              <div className="grid gap-4">
                {routes.map(route => <div key={route.name} className="rounded-xl border border-nova-border p-4 sm:p-5"><h3 className="text-lg font-semibold text-nova-text">{route.name}</h3><p className="mt-2">{route.path}</p><p className="mt-2"><strong>Đáng đi vì:</strong> {route.reward}</p><Source page={route.page}>Cơ chế & điều kiện</Source>{route.name === "Lunar / Mặt Trăng" && <Link href="/lunar-rift" className="ml-4 font-semibold text-nova-accent underline underline-offset-4">Guide Lunar đầy đủ →</Link>}</div>)}
              </div>
              <p className="rounded-xl bg-nova-accent/5 p-4"><strong>Gợi ý cho người mới:</strong> ổn định thức ăn và đồ hồi phục → chọn một boss săn đồ phù hợp → đi Ruins kiếm trang bị → học Guardian → chuẩn bị Fuelweaver hoặc đi tuyến Lunar. Không cần chờ đánh xong tất cả boss độc lập mới bắt đầu Ancient.</p>
              <p>Riêng <strong>Ancient Sanctum</strong> là một nhánh khác của nội dung Ancient: phòng Key Room có bốn tháp và bốn Pulse Cradles. Keystone lấy ở đây còn liên quan việc tái tạo Sanctum qua Beckoning Hand. Nó không thay Ancient Key để gọi Fuelweaver. <Source page="Ancient_Guard_Tower" /> · <Source page="Keystone" /></p>
            </Section>

            <Section id="hoi-dap" title="09. Kẹt ở đâu?">
              <dl className="space-y-4">
                <div><dt className="font-semibold text-nova-text">Chỉ muốn có đồ Ancient, có bắt buộc đánh Fuelweaver không?</dt><dd>Không. Bạn có thể khai thác Ruins, dùng trạm chế đồ và trở về. Fuelweaver là bước tiếp theo khi đã đủ vật phẩm và trang bị.</dd></div>
                <div><dt className="font-semibold text-nova-text">Đã giết Guardian nhưng không gọi được Fuelweaver?</dt><dd>Kiểm tra đủ Key, Shadow Atrium, 8 hóa thạch đúng hình; bộ xương phải ở Atrium gần Gateway đã cắm Key. Labyrinth không phải chỗ gọi boss.</dd></div>
                <div><dt className="font-semibold text-nova-text">Shadow Pieces không cho trái tim?</dt><dd>Cần hạ Shadow Piece cấp 3, đạt được bằng chuỗi tăng cấp giữa ba loại khác nhau ở gần nhau. Một tượng đơn lẻ không đủ.</dd></div>
                <div><dt className="font-semibold text-nova-text">Lunar Rift mở rồi thì Shadow Rift tự mở theo không?</dt><dd>Không. Đây là hai nhánh riêng. Theo tiến trình mặc định, Shadow Rift cần Fuelweaver và 5 Dreadstone; thiết lập server có thể thay đổi điều kiện.</dd></div>
                <div><dt className="font-semibold text-nova-text">Bàn tay trong trận và bàn tay nhận đá có phải một không?</dt><dd>Không. Unseen Hands tạo khiên cho Fuelweaver; Beckoning Hand ở Gateway nhận Dreadstone sau chiến thắng.</dd></div>
              </dl>
            </Section>
          </article>
        </div>
      </div>
    </DstPageShell>
  </div>;
}
