import source from "./source.json";
import a from "./part-a.json";
import b from "./part-b.json";
import c from "./part-c.json";
import type { LingGioiItem, LingGioiSection } from "@/app/lib/ling-gioi";

const names: Record<string, string> = {
  jingjie: "Cảnh giới", rumo: "Sinh vật nhập ma", danyao: "Đan dược và luyện đan",
  cailiao: "Vật liệu tinh luyện", jianzhu: "Công trình", wuqi: "Vũ khí và giáp",
  fabao: "Pháp bảo và công cụ", zhenfa: "Trận pháp và linh kỹ", lingzhi: "Linh thực",
  yihuo: "Khư hỏa và dị hỏa", ditu: "Địa hình và Boss", renwu: "Nhân vật", log: "Nhật ký cập nhật",
};
export const lingGioiSections: LingGioiSection[] = source.sections.map(section => ({ id: section["分类id"], name: names[section["分类id"]] }));
const translations = new Map([...a, ...b, ...c].map(item => [item.id, item]));
export const lingGioiItems: LingGioiItem[] = source.items.map(item => {
  const translated = translations.get(item.id);
  if (!translated) throw new Error(`Missing Vietnamese translation: ${item.id}`);
  return { ...translated, section: item["分类id"], originalName: item["名称"], image: item["图片"], order: Number(item["排序值"]) || 0, hidden: item["是否展示"] === "false" };
}).sort((a, b) => a.order - b.order);
