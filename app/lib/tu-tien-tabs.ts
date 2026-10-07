export const tuTienTabs = [
  { id: "che-tao", label: "Chế tạo" },
  { id: "canh-gioi", label: "Cảnh giới" },
  { id: "nyx", label: "Nyx" },
  { id: "thanh-tuu", label: "Thành Tựu" },
  { id: "than-khi", label: "Thần Khí" },
  { id: "cong-trinh", label: "Công Trình" },
  { id: "ham-nguc", label: "Hầm Ngục" },
] as const;

export type TuTienTabId = typeof tuTienTabs[number]["id"];

export function resolveTuTienTab(hash: string): TuTienTabId {
  const id = hash.replace(/^#/, "");
  return tuTienTabs.find(tab => tab.id === id)?.id ?? "che-tao";
}
