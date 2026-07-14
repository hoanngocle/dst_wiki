import type { WikiEntry } from "@/app/lib/wiki-search";

export const wikiEntries: readonly WikiEntry[] = [
  { id: "ancient-blade", name: "Lưỡi Kiếm Cổ", category: "item", description: "Một vũ khí cổ được tìm thấy trong tàn tích phương bắc.", keywords: ["kiếm", "hiếm", "di vật", "vật phẩm"], accent: "ice" },
  { id: "wayfinder-lantern", name: "Đèn Dẫn Lối", category: "item", description: "Một công cụ phát sáng khi ở gần lối đi bí mật.", keywords: ["công cụ", "ánh sáng", "khám phá", "vật phẩm"], accent: "sand" },
  { id: "mire-stalker", name: "Kẻ Rình Đầm Lầy", category: "creature", description: "Một sinh vật bảo vệ lãnh thổ bên những lối đi ngập nước.", keywords: ["đầm lầy", "quái thú", "thù địch", "sinh vật"], accent: "moss" },
  { id: "glasswing-moth", name: "Bướm Cánh Kính", category: "creature", description: "Một sinh vật đêm hiền lành bị thu hút bởi ánh sáng lạnh.", keywords: ["bay", "hiền lành", "ban đêm", "sinh vật"], accent: "ice" },
  { id: "hollow-crossing", name: "Lối Qua Vùng Trũng", category: "location", description: "Một tuyến đường bị lãng quên bên dưới thành phố cổ.", keywords: ["dưới lòng đất", "tàn tích", "tuyến đường", "địa điểm"], accent: "slate" },
  { id: "windrest-observatory", name: "Đài Quan Sát Windrest", category: "location", description: "Một trạm trên núi được dựng để theo dõi những cơn bão xa.", keywords: ["núi", "tháp", "thời tiết", "địa điểm"], accent: "ice" },
  { id: "borrowed-map", name: "Tấm Bản Đồ Mượn", category: "quest", description: "Trả lại bản đồ khảo sát đã đánh dấu trước chuyến thám hiểm tiếp theo.", keywords: ["khám phá", "giao trả", "khảo sát", "nhiệm vụ"], accent: "sand" },
  { id: "quiet-bell", name: "Chiếc Chuông Im Lặng", category: "quest", description: "Tìm hiểu vì sao chuông báo hiệu của ngôi làng không còn vang lên.", keywords: ["bí ẩn", "ngôi làng", "điều tra", "nhiệm vụ"], accent: "slate" },
];
