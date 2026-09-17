import { fireEvent, render, screen, within } from "@testing-library/react";
import { beforeEach, expect, it } from "vitest";

import payload from "@/data/generated/solo-leveling.json";
import { SoloLevelingBrowser } from "./solo-leveling-browser";

beforeEach(() => window.history.replaceState(null, "", "/solo-leveling"));

function selectTab(name: string) {
  fireEvent.mouseDown(screen.getByRole("tab", { name: new RegExp(name) }), { button: 0 });
}

it("lists daily quests in full-width rows with distinct difficulty colors and complete details", () => {
  window.history.replaceState(null, "", "#solo-daily");
  render(<SoloLevelingBrowser data={payload} />);
  const easy = screen.getByRole("article", { name: "Lâm tặc tập sự" });
  const quests = payload.groups.find((group) => group.id === "daily")!.entries;
  for (const difficulty of ["Dễ", "Vừa", "Khó"]) {
    const quest = quests.find((entry) => entry.category === difficulty)!;
    const row = screen.getByRole("article", { name: quest.title });
    expect(row.getAttribute("data-difficulty")).toBe(difficulty);
    expect(within(row).getByText(`Độ khó: ${difficulty}`)).toBeDefined();
  }
  expect(easy.parentElement!.className).not.toContain("sm:grid-cols-2");
  expect(within(easy).getByText("50 EXP")).toBeDefined();
  fireEvent.click(within(easy).getByText("Cách tính tiến độ & điều kiện"));
  expect(within(easy).getByText(/Phải chặt hạ cây/)).toBeDefined();
  expect(screen.getByRole("heading", { name: "Cách làm nhiệm vụ ngày" })).toBeDefined();
  expect(screen.getByRole("tab", { name: /Daily Quest/, selected: true })).toBeDefined();
  expect(screen.getByRole("heading", { name: "Daily Quest", level: 2 })).toBeDefined();
  expect(screen.queryByLabelText("Rank", { exact: true })).toBeNull();
  fireEvent.change(screen.getByLabelText("Độ khó", { exact: true }), { target: { value: "Khó" } });
  expect(screen.getAllByRole("article").every((row) => within(row).queryByText("Độ khó: Khó"))).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: "Xóa bộ lọc" }));
  expect((screen.getByLabelText("Độ khó", { exact: true }) as HTMLSelectElement).value).toBe("all");
});

it("shows guild quests as rows and combines Rank and browsing difficulty filters", () => {
  window.history.replaceState(null, "", "#solo-guild");
  render(<SoloLevelingBrowser data={payload} />);
  const row = screen.getByRole("article", { name: "Nhiệm vụ: Lập kho tiền tuyến" });
  expect(row.parentElement!.className).not.toContain("sm:grid-cols-2");
  expect(within(row).getByText("30 Xu Hiệp Hội")).toBeDefined();
  fireEvent.click(within(row).getByText("Điều kiện & phần thưởng"));
  expect(within(row).getByText(/Vật phẩm giao nộp: 20 × cutgrass/)).toBeDefined();
  fireEvent.change(screen.getByLabelText("Rank", { exact: true }), { target: { value: "A" } });
  fireEvent.change(screen.getByLabelText("Độ khó (theo Rank)"), { target: { value: "Khó" } });
  expect(screen.getAllByRole("article").every((card) => within(card).queryByText("Rank: A") && card.getAttribute("data-difficulty") === "Khó")).toBe(true);
  fireEvent.change(screen.getByLabelText("Độ khó (theo Rank)"), { target: { value: "Dễ" } });
  expect(screen.getByText("Không tìm thấy nội dung phù hợp.")).toBeDefined();
  fireEvent.click(screen.getByRole("button", { name: "Xóa bộ lọc" }));
  expect(screen.getByRole("article", { name: "Nhiệm vụ: Lập kho tiền tuyến" })).toBeDefined();
});

it("names Rank exams Rank Up and lists each exam as a full-width row", () => {
  window.history.replaceState(null, "", "#solo-exams");
  render(<SoloLevelingBrowser data={payload} />);
  expect(screen.getByRole("tab", { name: /Rank Up/, selected: true })).toBeDefined();
  expect(screen.getByRole("heading", { name: "Rank Up", level: 2 })).toBeDefined();
  expect(screen.queryByRole("tab", { name: /Thăng Rank/ })).toBeNull();
  const exam = screen.getByRole("article", { name: "Bài Kiểm Tra: Cánh cửa đầu tiên" });
  expect(exam.parentElement!.className).not.toContain("sm:grid-cols-2");
  expect(within(exam).getByText("Rank: D")).toBeDefined();
  expect(within(exam).getByText("Mục tiêu: 5")).toBeDefined();
  expect(within(exam).getByText("100 Xu Hiệp Hội")).toBeDefined();
  const exams = screen.getAllByRole("article").filter((article) => article.id.startsWith("exams-"));
  expect(new Set(exams.map((article) => article.className)).size).toBe(5);
  fireEvent.click(within(exam).getByText("Điều kiện & phần thưởng"));
  expect(within(exam).getByText(/Vật phẩm thưởng: 10 × bluegem/)).toBeDefined();
});

it("shows recipe ingredient icons, actual output quantity, and dungeon currency", () => {
  render(<SoloLevelingBrowser data={payload} />);
  selectTab("Chế tạo & dung hợp");
  const gem = screen.getByRole("article", { name: "Đá Cường Hoá" });
  expect(within(gem).getByRole("img", { name: "Icon Đá Cường Hoá" }).getAttribute("data-missing")).toBeNull();
  expect(within(gem).getByRole("img", { name: "Nguyên liệu Linh Thạch" })).toBeDefined();
  expect(within(gem).getByText("8 × Đá Cường Hoá")).toBeDefined();
  selectTab("Cửa hàng Hầm Ngục");
  const potion = screen.getByRole("article", { name: "Thuốc Sức Mạnh" });
  expect(within(potion).getByText("120 Xu Hầm Ngục")).toBeDefined();
  expect(within(potion).getByRole("img", { name: "Icon Thuốc Sức Mạnh" }).getAttribute("data-missing")).toBeNull();
  selectTab("Đệ tử & quân đoàn");
  const igris = screen.getByRole("article", { name: "Igris" });
  expect(within(igris).getByText("Thép Đen")).toBeDefined();
  expect(within(igris).getByText("Cấp 5")).toBeDefined();
});

it("filters by recipe station, dungeon product type, and quest difficulty and resets on tab changes", () => {
  render(<SoloLevelingBrowser data={payload} />);
  selectTab("Chế tạo & dung hợp");
  fireEvent.change(screen.getByLabelText("Loại nội dung"), { target: { value: "Dung hợp" } });
  expect(screen.getAllByRole("article")).toHaveLength(2);
  expect(screen.getByRole("heading", { name: "Dung hợp Phúc Lạc Dược III" })).toBeDefined();
  selectTab("Cửa hàng Hầm Ngục");
  expect((screen.getByLabelText("Loại nội dung") as HTMLSelectElement).value).toBe("all");
  fireEvent.change(screen.getByLabelText("Loại nội dung"), { target: { value: "Vũ khí" } });
  expect(screen.getAllByRole("article")).toHaveLength(7);
  expect(screen.queryByRole("heading", { name: "Thuốc Sức Mạnh" })).toBeNull();
  selectTab("Daily Quest");
  fireEvent.change(screen.getByLabelText("Độ khó"), { target: { value: "Khó" } });
  expect(screen.getAllByRole("article").every((card) => within(card).queryByText("Độ khó: Khó"))).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: "Xóa bộ lọc" }));
  expect(screen.getByRole("heading", { name: "Cách làm nhiệm vụ ngày" })).toBeDefined();
});

it("shows one topic at a time and searches only the selected tab without accents", () => {
  render(<SoloLevelingBrowser data={payload} />);
  expect(screen.getByRole("tab", { name: /Hướng dẫn/, selected: true })).toBeDefined();
  expect(screen.queryByRole("heading", { name: "Cỏ cắt" })).toBeNull();
  expect(screen.queryByRole("heading", { name: "Lâm tặc tập sự" })).toBeNull();
  selectTab("Daily Quest");
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm trong Solo Leveling" }), { target: { value: "lam tac tap su" } });
  expect(screen.getByRole("heading", { name: "Lâm tặc tập sự" })).toBeDefined();
  expect(screen.getByText("50 EXP")).toBeDefined();
  expect(screen.queryByRole("heading", { name: "Chạy marathon" })).toBeNull();
  selectTab("Chế tạo & dung hợp");
  expect(screen.getByRole("searchbox").getAttribute("value")).toBe("");
  expect(screen.queryByRole("heading", { name: "Lâm tặc tập sự" })).toBeNull();
  expect(screen.getByRole("heading", { name: "Đá Cường Hoá" })).toBeDefined();
});

it("renders guild shop icons and clear purchase quantities, filters by Rank, and paginates", () => {
  render(<SoloLevelingBrowser data={payload} />);
  selectTab("Cửa hàng Hiệp Hội");
  const grass = screen.getByRole("article", { name: "Cỏ cắt" });
  expect(within(grass).getByRole("img", { name: "Icon Cỏ cắt" }).getAttribute("data-missing")).toBeNull();
  expect(within(grass).getByText("2 Xu Hiệp Hội")).toBeDefined();
  expect(within(grass).getByText("6 vật phẩm")).toBeDefined();
  expect(within(grass).getByText("10 lượt / chu kỳ")).toBeDefined();
  expect(screen.getAllByRole("article")).toHaveLength(12);
  fireEvent.click(screen.getAllByRole("button", { name: "Trang sau" })[0]);
  expect(screen.queryByRole("heading", { name: "Cỏ cắt" })).toBeNull();
  expect(screen.getByRole("heading", { name: "Bánh răng" })).toBeDefined();
  fireEvent.change(screen.getByLabelText("Rank yêu cầu"), { target: { value: "S" } });
  expect(screen.queryByRole("heading", { name: "Bánh răng" })).toBeNull();
  expect(screen.getByRole("heading", { name: "Nhãn cầu Deerclops" })).toBeDefined();
  expect(screen.getByRole("status").textContent).toContain("15");
  fireEvent.change(screen.getByRole("searchbox"), { target: { value: "co cat" } });
  expect(screen.getByText("Không tìm thấy nội dung phù hợp.")).toBeDefined();
  fireEvent.click(screen.getByRole("button", { name: "Xóa bộ lọc" }));
  expect(screen.getByRole("article", { name: "Cỏ cắt" })).toBeDefined();
  expect(screen.getByRole("tab", { name: /Cửa hàng Hiệp Hội/, selected: true })).toBeDefined();
});

it("keeps Wiki tables while removing configuration and source tabs, including their old hash links", () => {
  render(<SoloLevelingBrowser data={payload} />);
  selectTab("Wiki");
  fireEvent.change(screen.getByRole("searchbox"), { target: { value: "CƯỜNG HOÁ" } });
  expect(screen.getByRole("table", { name: "CƯỜNG HOÁ — bảng 1" })).toBeDefined();
  expect(screen.getByText("93.50")).toBeDefined();
  expect(screen.queryByRole("heading", { name: "File nguồn & tài liệu gốc" })).toBeNull();
  expect(screen.queryByRole("tab", { name: /File nguồn/ })).toBeNull();
  expect(screen.queryByRole("tab", { name: /Thông số & cấu hình/ })).toBeNull();
  expect(screen.queryByRole("tab", { name: /Thuộc tính & hiệu ứng/ })).toBeNull();
  expect(screen.getAllByRole("tab")).toHaveLength(10);
  for (const hash of ["#solo-sources", "#solo-config", "#solo-effects"]) {
    window.history.replaceState(null, "", hash);
    fireEvent(window, new Event("hashchange"));
    expect(screen.getByRole("tab", { name: /Hướng dẫn/, selected: true })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Hướng dẫn", level: 2 })).toBeDefined();
  }
});

it("opens a topic from existing hash links", () => {
  window.history.replaceState(null, "", "/solo-leveling#solo-guild-shop");
  render(<SoloLevelingBrowser data={payload} />);
  expect(screen.getByRole("tab", { name: /Cửa hàng Hiệp Hội/, selected: true })).toBeDefined();
  expect(screen.getByRole("article", { name: "Cỏ cắt" })).toBeDefined();
});

it("resets incompatible filters when navigating to another topic through a hash link", () => {
  render(<SoloLevelingBrowser data={payload} />);
  selectTab("Cửa hàng Hiệp Hội");
  fireEvent.change(screen.getByLabelText("Rank yêu cầu"), { target: { value: "S" } });
  window.history.replaceState(null, "", "#solo-daily");
  fireEvent(window, new Event("hashchange"));
  expect(screen.getByRole("heading", { name: "Lâm tặc tập sự" })).toBeDefined();
  expect(screen.queryByText("Không tìm thấy nội dung phù hợp.")).toBeNull();
});

it("opens the containing topic and page for existing entry deep links", () => {
  window.history.replaceState(null, "", "#guild-shop-73");
  render(<SoloLevelingBrowser data={payload} />);
  expect(screen.getByRole("tab", { name: /Cửa hàng Hiệp Hội/, selected: true })).toBeDefined();
  expect(screen.getByRole("article", { name: "Giáp xương" })).toBeDefined();
  expect(screen.getByRole("status").textContent).toContain("73–84");
  window.history.replaceState(null, "", "#guild-shop-89");
  fireEvent(window, new Event("hashchange"));
  expect(screen.getByRole("article", { name: "Giáp Brightshade" })).toBeDefined();
  expect(screen.queryByRole("article", { name: "Giáp xương" })).toBeNull();
});
