import fs from "node:fs";
import { JSDOM } from "jsdom";

const file = "public/data/items.json";
const payload = JSON.parse(fs.readFileSync(file, "utf8"));
const catalog = new Map(JSON.parse(fs.readFileSync("public/data/catalog.json", "utf8")).entities.map((item) => [item.key, item]));
const itemsById = new Map(payload.items.map((item) => [item.id, item]));
const document = new JSDOM("").window.document;
const sentences = new Intl.Segmenter("vi", { granularity: "sentence" });
const concise = (text) => [...sentences.segment(text)].slice(0, 2).map(({ segment }) => segment).join("").trim();
const unknown = () => ({ status: "unknown", text: null, sources: [] });
const known = (text, sources) => ({ status: "known", text, sources });
const plain = (html) => {
  const root = document.createElement("div");
  root.innerHTML = html;
  return root.textContent.replace(/\s+/g, " ").trim();
};
const name = (id) => itemsById.get(id)?.name ?? id.split(":").at(-1);
const counts = Object.fromEntries(["usage", "fuel", "recycling", "acquisition"].map((key) => [key, { known: 0, unknown: 0, not_applicable: 0 }]));

for (const item of payload.items) {
  const source = `public/data/items.json#${item.id}`;
  const entry = catalog.get(item.id);
  const pagePath = item.wiki ? `public${item.wiki.detailUrl}` : null;
  const page = pagePath && fs.existsSync(pagePath) ? JSON.parse(fs.readFileSync(pagePath, "utf8")) : null;
  const summary = { usage: unknown(), fuel: unknown(), recycling: unknown(), acquisition: unknown() };

  const effects = item.details?.usage?.effects?.map((effect) => effect.text) ?? [];
  if (effects.length) summary.usage = known(effects.join(" "), [`${source}/details/usage/effects`]);
  else if (page?.summaryViHtml) {
    const root = document.createElement("div");
    root.innerHTML = page.summaryViHtml;
    const paragraph = root.querySelector("p, li")?.textContent.trim();
    if (paragraph) summary.usage = known(concise(paragraph), [`${pagePath}#summaryViHtml`]);
  } else if (item.namespace === "tu_tien" && item.description) {
    summary.usage = known(item.description, [`${source}/description`]);
  }

  // Only extract explicit fuel fields; flammability categories are not fuel values.
  const burnTime = page?.wikitext?.match(/^\s*\|burnTime\s*=([^\n]*)/im)?.[1]?.trim();
  if (burnTime) {
    const fuelType = burnTime.match(/link=Fuel#([^\]]+)/)?.[1];
    const cleaned = plain(burnTime.replace(/\[\[File:[\s\S]*?\]\]/gi, ""));
    if (/^\d+(?:\.\d+)?\s*(?:sec|min)\.?$/i.test(cleaned)) {
      const text = cleaned.replace(/\bsec\.?/g, "giây").replace(/\bmin\.?/g, "phút");
      const typeLabel = fuelType === "Fire Fuel" ? "Nhiên liệu đốt lửa" : fuelType === "Nightmare Fuel" ? "Nhiên liệu ác mộng" : fuelType;
      summary.fuel = known(typeLabel ? `${typeLabel}: ${text}` : text, [`${pagePath}#burnTime`]);
    }
  }

  const acquisition = [];
  const acquisitionSources = [];
  if (item.recipe) {
    const ingredients = item.recipe.ingredients.map((ingredient) => `${ingredient.amount} ${name(ingredient.id)}`).join(" + ");
    acquisition.push(`Chế tạo từ ${ingredients}${item.craftingNote ? ` (${item.craftingNote})` : ""}.`);
    acquisitionSources.push(`${source}/recipe`);
  } else if (item.craftingNote) {
    acquisition.push(item.craftingNote);
    acquisitionSources.push(`${source}/craftingNote`);
  }
  for (const drop of item.details?.dropBy?.sources ?? []) {
    const prefix = { drop: "Rơi từ", harvest: "Thu hoạch từ", start: "Vật phẩm khởi đầu của", trade: "Trao đổi từ", other: "Nhận từ" }[drop.type];
    const text = [drop.source ? `${prefix} ${drop.source.name}` : null, drop.quantity, drop.chance, drop.conditions].filter(Boolean).join("; ");
    if (text) { acquisition.push(text); acquisitionSources.push(`${source}/details/dropBy`); }
  }
  if (!item.details?.dropBy?.sources?.length) {
    for (const drop of entry?.acquisition ?? []) {
      if (!drop.source || drop.type !== "drop") continue;
      // Conditional/random source expressions are not a guaranteed drop.
      const conditional = drop.chance == null || drop.conditions?.source_expression;
      acquisition.push(`${conditional ? "Có thể rơi" : "Rơi"} từ ${name(drop.source)}${typeof drop.chance === "number" ? ` (${Math.round(drop.chance * 100)}%)` : ""}.`);
      acquisitionSources.push(`public/data/catalog.json#${item.id}/acquisition`);
    }
  }
  if (acquisition.length) summary.acquisition = known([...new Set(acquisition)].join(" "), [...new Set(acquisitionSources)]);

  if (item.id === "base_game:tacklesketch") {
    const userSource = "user-provided:2026-10-07/advert";
    summary.usage = known("Nhấp chuột phải để học công thức Phao câu hoặc Mồi giả cho Cần câu biển; không học lại công thức đã biết.", [userSource]);
    summary.fuel = known("Đốt lửa trong 15 giây.", [userSource]);
    summary.recycling = known("Xóa tại Bàn vẽ bản đồ để thu hồi nguyên liệu.", [userSource]);
    summary.acquisition = known("Mua từ Bà Cua ở thân thiết cấp 6 với giá 1 Vỏ chai rỗng/tờ, hoặc nhận ngẫu nhiên từ Túi quà cảm ơn.", [userSource]);
    item.craftingNote = null;
    item.description = "Phiếu mẫu dùng để học công thức Phao câu và Mồi giả cho Cần câu biển.";
  }
  if (item.id === "base_game:abigail_flower") {
    item.description = "Kỷ vật của Wendy, dùng để gọi hồn người chị song sinh Abigail đồng hành và hỗ trợ chiến đấu.";
    summary.usage = known("Wendy dùng để triệu hồi hoặc thu hồi Abigail và điều chỉnh trạng thái chiến đấu của cô ấy.", [`${pagePath}#perk`]);
    summary.acquisition.text = `Wendy chế tạo từ ${item.recipe.ingredients.map((ingredient) => `${ingredient.amount} ${name(ingredient.id)}`).join(" + ")}.`;
    summary.acquisition.sources.push(`public/data/catalog.json#${item.id}/recipes`);
  }
  // Preserve later editorial corrections when this migration is rerun.
  item.summary ??= summary;
  if (item.description) item.description = concise(item.description);
  for (const key of Object.keys(counts)) counts[key][item.summary[key].status]++;
}

fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
console.log(JSON.stringify({ items: payload.items.length, fields: counts }, null, 2));
