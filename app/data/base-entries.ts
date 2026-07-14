export type BaseEntry = {
  id: string;
  name: string;
  image: string;
};

export const baseEntries: readonly BaseEntry[] = [
  { id: "starter", name: "Base Khởi Đầu", image: "/base-placeholders/base-01.webp" },
  { id: "meadow", name: "Base Ven Đồng Cỏ", image: "/base-placeholders/base-02.webp" },
  { id: "forest", name: "Base Rìa Rừng", image: "/base-placeholders/base-03.webp" },
  { id: "winter", name: "Base Mùa Đông", image: "/base-placeholders/base-04.webp" },
  { id: "coast", name: "Base Ven Biển", image: "/base-placeholders/base-05.webp" },
  { id: "mega", name: "Mega Base", image: "/base-placeholders/base-06.webp" },
];
