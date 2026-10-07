import fs from "node:fs";

const file = "public/data/items.json";
const payload = JSON.parse(fs.readFileSync(file, "utf8"));
const catalog = new Map(JSON.parse(fs.readFileSync("public/data/catalog.json", "utf8")).entities.map((entry) => [entry.key, entry]));
const names = "Wilson|Willow|Wolfgang|Wendy|WX-78|Wickerbottom|Woodie|Wes|Maxwell|Waxwell|Wigfrid|Wathgrithr|Webber|Winona|Warly|Wortox|Wormwood|Wurt|Walter|Wanda";
const normalize = (name) => ({ Waxwell: "Maxwell", Wathgrithr: "Wigfrid" })[name] ?? name;
const unknown = () => ({ status: "unknown", text: null, sources: [] });
const known = (text, sources) => ({ status: "known", text, sources });
const pages = new Map();
const tags = new Map();

// Learn tag-to-character mappings from explicit recipe restrictions in the saved Wiki.
for (const item of payload.items) {
  if (!item.wiki) continue;
  const path = `public${item.wiki.detailUrl}`;
  if (!fs.existsSync(path)) continue;
  const page = JSON.parse(fs.readFileSync(path, "utf8"));
  const start = page.wikitext?.indexOf("{{Object Infobox") ?? -1;
  const head = start < 0 ? "" : page.wikitext.slice(start).split(/\{\{Quotes|<tabber>|\n'''/i)[0];
  const lines = head.split("\n").filter((line) => /^\|multiplier\d*\s*=/.test(line) && /\bonly\b/i.test(line));
  const characters = [...new Set(lines.flatMap((line) => [...line.matchAll(new RegExp(`(${names}) Portrait`, "g"))].map((match) => normalize(match[1]))))];
  pages.set(item.id, { page, path, characters });
  if (characters.length !== 1) continue;
  for (const recipe of catalog.get(item.id)?.recipes ?? []) {
    const tag = recipe.restrictions?.config_expression?.match(/builder_tag\s*=\s*"([^"]+)"/)?.[1];
    if (tag) {
      const matches = tags.get(tag) ?? new Map();
      matches.set(characters[0], `${path}#recipe`);
      tags.set(tag, matches);
    }
  }
}

let craftingCount = 0;
let usageCount = 0;
for (const item of payload.items) {
  const evidence = pages.get(item.id);
  const recipes = catalog.get(item.id)?.recipes ?? [];
  const characters = new Set(evidence?.characters ?? []);
  const sources = characters.size ? [`${evidence.path}#recipe`] : [];
  for (const recipe of recipes) {
    const tag = recipe.restrictions?.config_expression?.match(/builder_tag\s*=\s*"([^"]+)"/)?.[1];
    const mapping = tags.get(tag);
    if (mapping?.size === 1) {
      const [character, source] = [...mapping][0];
      characters.add(character);
      sources.push(`public/data/catalog.json#${item.id}/recipes`, source);
    }
  }
  const requirement = { crafting: unknown(), usage: unknown() };
  if (characters.size) {
    const alternative = recipes.some((recipe) => recipe.restrictions?.config_expression && !/builder_tag/.test(recipe.restrictions.config_expression));
    requirement.crafting = known(`${[...characters].join(" / ")} — công thức riêng của nhân vật.${alternative ? " Có công thức khác không yêu cầu nhân vật này." : ""}`, [...new Set(sources)]);
  }
  // Do not infer who may use an item from who may craft it.
  const text = evidence?.page.plainText ?? "";
  const onlyUser = text.match(new RegExp(`(?:can only be|only be) (?:used|equipped|worn) by (${names})\\b`, "i"));
  if (onlyUser) requirement.usage = known(normalize(onlyUser[1]), [`${evidence.path}#plainText`]);
  if (item.id === "base_game:abigail_flower") requirement.usage = known("Wendy", [`${evidence.path}#perk`]);
  item.characterRequirements ??= requirement;
  if (item.characterRequirements.crafting.status === "known") craftingCount++;
  if (item.characterRequirements.usage.status === "known") usageCount++;
}
fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
console.log(JSON.stringify({ craftingCount, usageCount, mappedTags: tags.size }));
