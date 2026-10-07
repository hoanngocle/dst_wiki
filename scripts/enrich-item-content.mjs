import fs from "node:fs";
import { JSDOM } from "jsdom";

const file = "public/data/items.json";
const payload = JSON.parse(fs.readFileSync(file, "utf8"));
const overrides = JSON.parse(fs.readFileSync("data/manual/item-content.json", "utf8"));
const document = new JSDOM("").window.document;
const segmenter = new Intl.Segmenter("vi", { granularity: "sentence" });
const protectedIds = new Set(["base_game:atrium_key", "base_game:tacklesketch"]);
const known = (text, sources) => ({ status: "known", text, sources: [...new Set(sources)] });
const sentences = (text) => [...segmenter.segment(text)].map(({ segment }) => segment.trim());
const clean = (text) => text.replace(/[\u200b-\u200d\ufeff]/g, "").replace(/\s+/g, " ").trim();
const dlc = /Shipwrecked|Hamlet|Reign of Giants|DLC|The Gorge|The Forge/i;
const acquisition = /(?:chế tạo|được tạo ra từ|thu được|nhận được|rơi ra từ|rơi từ|tìm thấy|có được bằng|được mua|mua từ|thu hoạch từ)/i;
const names = new Map();
const uses = new Map();
for (const item of payload.items) {
  for (const name of [item.name, item.englishName, item.wiki?.title]) {
    if (name) names.set(name.replace(/\/DST$/, "").toLowerCase(), item);
  }
  for (const ingredient of item.recipe?.ingredients ?? []) {
    if (item.namespace !== "base_game") continue;
    const rows = uses.get(ingredient.id) ?? [];
    rows.push(item);
    uses.set(ingredient.id, rows);
  }
}
const changes = [];
for (const item of payload.items) {
  if (item.namespace !== "base_game" || item.category !== "item" || protectedIds.has(item.id)) continue;
  const before = JSON.stringify(item.summary);
  item.summary ??= Object.fromEntries(["usage", "acquisition", "fuel", "recycling"].map((field) => [field, { status: "unknown", text: null, sources: [] }]));
  // Remove only generated suffixes before rebuilding; repeated runs must be stable.
  if (item.summary.usage.text) item.summary.usage.text = item.summary.usage.text
    .replace(/\s*Dùng làm nguyên liệu chế tạo [^.]+\./g, "")
    .replace(/\s*Khi ăn \(chỉ số cơ bản\):[^.]+\./g, "").trim();
  const pageRef = item.wiki?.relatedPages?.find((page) => page.title.endsWith("/DST")) ?? item.wiki;
  const path = pageRef ? `public${pageRef.detailUrl}` : null;
  const page = path && fs.existsSync(path) ? JSON.parse(fs.readFileSync(path, "utf8")) : null;
  if (page?.summaryViHtml) {
    const root = document.createElement("div");
    root.innerHTML = page.summaryViHtml;
    // Preserve full paragraphs instead of truncating every item after two sentences.
    // Exclude DLC descriptions and incomplete icon-only numerical translations.
    const parts = [...root.querySelectorAll("p, li")].flatMap((p) => sentences(clean(p.textContent)))
      .filter((text) => text.length > 25 && !dlc.test(text) && !/chỉ khả dụng sau|nội dung này|\d\s*[,;.]\s*$|^“|^–/i.test(text));
    const usageParts = parts.filter((text) => !acquisition.test(text));
    if (usageParts.length) item.summary.usage = known(usageParts.join(" "), [`${path}#summaryViHtml`]);
    const acquireParts = parts.filter((text) => acquisition.test(text));
    if (acquireParts.length) {
      const existing = item.summary.acquisition;
      // Replace ambiguous extracted loot probabilities, keep explicit recipe text.
      const recipeText = item.recipe ? `Chế tạo từ ${item.recipe.ingredients.map((part) => `${part.amount} ${part.name}`).join(" + ")}.${item.craftingNote ? ` ${item.craftingNote}` : ""}` : null;
      item.summary.acquisition = known([...new Set([recipeText, ...acquireParts].filter(Boolean))].join(" "),
        [...(recipeText ? existing.sources : []), `${path}#summaryViHtml`]);
    }
  }
  // Link only recipes still present in this DST catalogue, never removed DLC recipes.
  const results = uses.get(item.id) ?? [];
  if (results.length && !overrides[item.id]?.usage) {
    const text = `Dùng làm nguyên liệu chế tạo ${results.slice(0, 6).map((entry) => entry.name).join(", ")}${results.length > 6 ? " và các công thức khác" : ""}.`;
    const current = item.summary.usage;
    const previous = (current.text ?? "").replace(/\s*Dùng làm nguyên liệu chế tạo [^.]+\.$/, "");
    item.summary.usage = known([previous, text].filter(Boolean).join(" "),
      [...current.sources, ...results.slice(0, 6).map((entry) => `public/data/items.json#${entry.id}/recipe`)]);
  }
  // A drop-table row can group different methods/chances. Do not copy its chance
  // or quantity onto every source. Only use explicit DST rows or retained entities.
  if (item.summary.acquisition.status !== "known" && page?.normalized?.dropTable?.rows) {
    const rows = page.normalized.dropTable.rows.filter((row) => !/SW|Ham|Shipwrecked|Hamlet/i.test(row.context ?? ""));
    const sources = rows.flatMap((row) => row.sources.filter((source) =>
      /\/DST$/.test(page.title) || names.has(source.title.toLowerCase())));
    if (sources.length) item.summary.acquisition = known(`Nguồn nhận: ${[...new Set(sources.map((source) => source.title))].join(", ")}.`, [`${path}#normalized/dropTable`]);
  }
  const override = overrides[item.id];
  if (override) {
    for (const field of ["usage", "acquisition"]) {
      if (override[field]) item.summary[field] = known(override[field], override.sources);
    }
  }
  if (JSON.stringify(item.summary) !== before) changes.push(item.id);
}
fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
const items = payload.items.filter((item) => item.namespace === "base_game" && item.category === "item");
const unresolved = items.filter((item) => item.summary.usage.status !== "known" || item.summary.acquisition.status !== "known")
  .map((item) => ({ id: item.id, name: item.name, missing: ["usage", "acquisition"].filter((field) => item.summary[field].status !== "known") }));
fs.writeFileSync("docs/item-content-audit.json", `${JSON.stringify({ scope: "base_game/item", total: items.length, unresolved }, null, 2)}\n`);
console.log(JSON.stringify({ changed: changes.length, total: items.length, unresolved: unresolved.length }));
