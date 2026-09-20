export interface LingGioiSection { id: string; name: string }
export interface LingGioiItem {
  id: string; section: string; name: string; originalName: string;
  summary: string; recipe: string; details: string; tags: string[];
  image: string; order: number; hidden?: boolean;
}

export function searchVietnamese(text: string) {
  return text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[đĐ]/g, "d").toLowerCase();
}

export function lingGioiImage(path: string) {
  return /^images\/[\w./-]+\.(png|jpe?g|webp|gif|svg)$/i.test(path) && !path.includes("..")
    ? `/ling-gioi/${path}` : "";
}
