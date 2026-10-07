import { surfaceGuides } from "./surface-guides";
import { crossoverGuides } from "./crossover-guides";
import { shadowGuides } from "./shadow-guides";
import { explorationGuides } from "./exploration-guides";

export const bossGuides = [...surfaceGuides, ...crossoverGuides, ...shadowGuides, ...explorationGuides];

export function findBossGuide(slug: string) {
  return bossGuides.find(guide => guide.slug === slug);
}
