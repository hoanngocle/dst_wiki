import type { WikiEntry } from "@/app/lib/wiki-search";

export const wikiEntries: readonly WikiEntry[] = [
  { id: "ancient-blade", name: "Ancient Blade", category: "item", description: "A relic weapon recovered from the northern ruins.", keywords: ["sword", "rare", "relic"], accent: "ice" },
  { id: "wayfinder-lantern", name: "Wayfinder Lantern", category: "item", description: "A travel tool that glows near hidden passages.", keywords: ["tool", "light", "exploration"], accent: "sand" },
  { id: "mire-stalker", name: "Mire Stalker", category: "creature", description: "A territorial creature found beside flooded paths.", keywords: ["swamp", "beast", "hostile"], accent: "moss" },
  { id: "glasswing-moth", name: "Glasswing Moth", category: "creature", description: "A passive night creature drawn to cold light.", keywords: ["flying", "passive", "night"], accent: "ice" },
  { id: "hollow-crossing", name: "The Hollow Crossing", category: "location", description: "A forgotten route beneath the old city.", keywords: ["underground", "ruins", "route"], accent: "slate" },
  { id: "windrest-observatory", name: "Windrest Observatory", category: "location", description: "A mountain station built to chart distant storms.", keywords: ["mountain", "tower", "weather"], accent: "ice" },
  { id: "borrowed-map", name: "The Borrowed Map", category: "quest", description: "Return a marked survey map before the next expedition.", keywords: ["exploration", "delivery", "survey"], accent: "sand" },
  { id: "quiet-bell", name: "The Quiet Bell", category: "quest", description: "Discover why the village signal no longer sounds.", keywords: ["mystery", "village", "investigation"], accent: "slate" },
];
