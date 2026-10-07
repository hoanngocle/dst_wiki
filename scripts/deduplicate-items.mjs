import fs from "node:fs";

const file = "public/data/items.json";
const payload = JSON.parse(fs.readFileSync(file, "utf8"));
const groups = new Map();
const normalize = (text) => text.replace(/\/DST$/i, "").replaceAll("_", " ").trim().toLowerCase();
for (const item of payload.items) {
  const key = `${item.namespace}:${normalize(item.wiki?.title ?? item.englishName ?? item.name)}`;
  const group = groups.get(key) ?? [];
  group.push(item);
  groups.set(key, group);
}

const replacements = new Map();
const removed = [];
for (const group of groups.values()) {
  const wiki = group.filter((item) => item.id.startsWith("wiki:"));
  if (!wiki.length) continue;
  wiki.sort((a, b) => Number(/\/DST$/i.test(b.wiki?.title ?? b.name)) - Number(/\/DST$/i.test(a.wiki?.title ?? a.name)));
  const preferred = wiki[0];
  const path = preferred.wiki && `public${preferred.wiki.detailUrl}`;
  const page = path && fs.existsSync(path) ? JSON.parse(fs.readFileSync(path, "utf8")) : null;
  // A shared display name alone cannot identify different game entities.
  const firstSpawn = page?.wikitext?.match(/^\s*\|spawnCode\s*=\s*"([a-z0-9_]+)"/im)?.[1];
  const native = group.filter((item) => !item.id.startsWith("wiki:") &&
    (item.prefabId === firstSpawn || item.wiki?.pageId === preferred.wiki?.pageId));
  const winner = native.length === 1 ? native[0] : preferred;
  if (winner !== preferred) {
    if (winner.summary?.usage.status !== "known" && preferred.description) winner.description = preferred.description;
    winner.recipe ??= preferred.recipe;
    winner.craftingNote ??= preferred.craftingNote;
    winner.sprite ??= preferred.sprite;
    winner.wiki ??= { ...preferred.wiki, mappingState: "mapped" };
    for (const key of ["usage", "fuel", "recycling", "acquisition"]) {
      if (winner.summary?.[key]?.status === "unknown" && preferred.summary?.[key]?.status === "known") winner.summary[key] = preferred.summary[key];
    }
  }
  for (const duplicate of wiki) {
    if (duplicate === winner) continue;
    replacements.set(duplicate.id, winner);
    removed.push({ id: duplicate.id, name: duplicate.name, keptId: winner.id, keptName: winner.name });
  }
}

payload.items = payload.items.filter((item) => !replacements.has(item.id));
// Keep recipe links and nested item references pointing to the retained record.
function remap(value) {
  if (!value || typeof value !== "object") return;
  if (Array.isArray(value)) { value.forEach(remap); return; }
  const winner = replacements.get(value.id);
  if (winner) {
    value.id = winner.id;
    if ("name" in value) value.name = winner.name;
    if ("sprite" in value) value.sprite = winner.sprite;
  }
  for (const [key, child] of Object.entries(value)) {
    if (key === "entityId" && replacements.has(child)) value[key] = replacements.get(child).id;
    else remap(child);
  }
}
remap(payload);
fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
if (removed.length) fs.writeFileSync("docs/deduplicated-items.json", `${JSON.stringify({ removed }, null, 2)}\n`);
console.log(JSON.stringify({ removed: removed.length, remaining: payload.items.length, berryBush: payload.items.filter((item) => normalize(item.name) === "berry bush").map((item) => ({ id: item.id, name: item.name })) }));
