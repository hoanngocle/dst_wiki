import type {
  ItemListEntry,
  ItemNamespace,
  SpriteDescriptor,
} from "./item-catalog";

export type CharacterLocale = "vi" | "en";

type LocalizedText = {
  vi: string;
  en: string;
};

type CharacterStatSource = {
  value: string | number | null;
  display: string | null;
  note: string | null;
};

type CharacterAbilitySource = {
  name: LocalizedText;
  effect: LocalizedText;
};

type CharacterEquipmentSource = {
  code: string;
  name: LocalizedText;
  quantity: number | null;
  effect: LocalizedText;
};

export type CharacterProfileSource = {
  id: string;
  code: string;
  namespace: ItemNamespace;
  name: LocalizedText;
  title: LocalizedText;
  description: LocalizedText;
  portraitPath: string;
  stats: Readonly<Record<string, CharacterStatSource>>;
  abilities: readonly CharacterAbilitySource[];
  startingItems: readonly CharacterEquipmentSource[];
  artifacts: readonly CharacterEquipmentSource[];
};

export type CharacterGuideFact = {
  label: string;
  description: string;
  confidence: string;
};

export type CharacterGuide = {
  roles: readonly string[];
  attackPattern: string;
  range: string;
  complexity: string;
  summary: string;
  strengths: readonly string[];
  tradeoffs: readonly string[];
  firstSteps: readonly string[];
  combat: readonly CharacterGuideFact[];
  realmMilestones: readonly {
    realm: string;
    unlocks: readonly CharacterGuideFact[];
  }[];
  artifacts: readonly CharacterGuideFact[];
};

export type CharacterEquipment = {
  code: string;
  name: string;
  quantity: number | null;
  effect: string;
  icon: SpriteDescriptor | null;
};

export type CharacterCatalogEntry = {
  id: string;
  code: string;
  namespace: ItemNamespace;
  name: string;
  englishName: string;
  title: string;
  description: string;
  portrait: string;
  stats: Readonly<Record<string, CharacterStatSource>>;
  abilities: readonly {
    name: string;
    effect: string;
  }[];
  startingItems: readonly CharacterEquipment[];
  artifacts: readonly CharacterEquipment[];
  guide: CharacterGuide | null;
};

export type CharacterFilters = {
  query?: string;
  namespace?: ItemNamespace | "all";
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function requiredString(value: unknown, field: string): string {
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return value.trim();
}

function optionalString(value: unknown, field: string): string | null {
  if (value === undefined) return null;
  return requiredString(value, field);
}

function localizedText(value: unknown, field: string): LocalizedText {
  if (!isRecord(value) || typeof value.vi !== "string" || typeof value.en !== "string") {
    throw new Error(`${field} must contain Vietnamese and English strings`);
  }
  if (!value.vi.trim() && !value.en.trim()) {
    throw new Error(`${field} must contain public text`);
  }
  return { vi: value.vi.trim(), en: value.en.trim() };
}

function stringArray(value: unknown, field: string): readonly string[] {
  if (!Array.isArray(value)) {
    throw new Error(`${field} must be an array`);
  }
  return value.map((entry, index) => requiredString(entry, `${field} ${index}`));
}

function positiveInteger(value: unknown, field: string): number {
  if (typeof value !== "number" || !Number.isInteger(value) || value < 1) {
    throw new Error(`${field} must be a positive integer`);
  }
  return value;
}

function parseEquipment(
  value: unknown,
  field: string,
): CharacterEquipmentSource {
  if (!isRecord(value)) {
    throw new Error(`${field} must be an object`);
  }
  return {
    code: requiredString(value.code, `${field} code`).toLowerCase(),
    name: localizedText(value.name, `${field} name`),
    quantity:
      value.quantity === undefined
        ? null
        : positiveInteger(value.quantity, `${field} quantity`),
    effect: localizedText(value.effect, `${field} effect`),
  };
}

function parseProfile(
  code: string,
  value: unknown,
): CharacterProfileSource {
  if (!isRecord(value)) {
    throw new Error(`character profile ${code} must be an object`);
  }
  if (value.namespace !== "base_game" && value.namespace !== "tu_tien") {
    throw new Error(`character profile ${code} namespace is invalid`);
  }
  const normalizedCode = requiredString(code, "character profile code").toLowerCase();
  if (!isRecord(value.portrait)) {
    throw new Error(`character profile ${code} portrait must be an object`);
  }
  const portraitPath = requiredString(
    value.portrait.path,
    `character profile ${code} portrait path`,
  );
  const expectedPortraitPath =
    value.namespace === "base_game"
      ? `/assets/dst/characters/base/${normalizedCode}.png`
      : `/assets/dst/characters/${normalizedCode}.png`;
  if (portraitPath !== expectedPortraitPath) {
    throw new Error(`character profile ${code} portrait path is invalid`);
  }
  if (!isRecord(value.stats)) {
    throw new Error(`character profile ${code} stats must be an object`);
  }
  const stats = Object.fromEntries(
    Object.entries(value.stats).map(([stat, raw]) => {
      if (
        !isRecord(raw) ||
        (typeof raw.value !== "number" &&
          typeof raw.value !== "string" &&
          !(
            raw.value === null &&
            typeof raw.display === "string" &&
            raw.display.trim()
          ))
      ) {
        throw new Error(`character profile ${code} stat ${stat} is invalid`);
      }
      return [
        stat,
        {
          value: raw.value,
          display: optionalString(
            raw.display,
            `character profile ${code} stat ${stat} display`,
          ),
          note: optionalString(
            raw.note,
            `character profile ${code} stat ${stat} note`,
          ),
        },
      ];
    }),
  );
  if (!Array.isArray(value.abilities)) {
    throw new Error(`character profile ${code} abilities must be an array`);
  }
  const abilities = value.abilities.map((raw, index) => {
    if (!isRecord(raw)) {
      throw new Error(`character profile ${code} ability ${index} must be an object`);
    }
    return {
      name: localizedText(raw.name, `character profile ${code} ability ${index} name`),
      effect: localizedText(
        raw.effect,
        `character profile ${code} ability ${index} effect`,
      ),
    };
  });
  if (!Array.isArray(value.startingItems) || !Array.isArray(value.artifacts)) {
    throw new Error(`character profile ${code} equipment must contain arrays`);
  }
  return {
    id: `${value.namespace}:${normalizedCode}`,
    code: normalizedCode,
    namespace: value.namespace,
    name: localizedText(value.name, `character profile ${code} name`),
    title: localizedText(value.title, `character profile ${code} title`),
    description: localizedText(
      value.description,
      `character profile ${code} description`,
    ),
    portraitPath,
    stats,
    abilities,
    startingItems: value.startingItems.map((raw, index) =>
      parseEquipment(raw, `character profile ${code} starting item ${index}`),
    ),
    artifacts: value.artifacts.map((raw, index) =>
      parseEquipment(raw, `character profile ${code} artifact ${index}`),
    ),
  };
}

export function parseCharacterProfiles(
  value: unknown,
): ReadonlyMap<string, CharacterProfileSource> {
  if (!isRecord(value) || value.schemaVersion !== 1 || !isRecord(value.profiles)) {
    throw new Error("character profiles must use schema version 1");
  }
  const profiles = new Map<string, CharacterProfileSource>();
  for (const [code, raw] of Object.entries(value.profiles)) {
    const profile = parseProfile(code, raw);
    if (profiles.has(profile.id)) {
      throw new Error(`duplicate character identity ${profile.id}`);
    }
    profiles.set(profile.id, profile);
  }
  return profiles;
}

function parseGuideFact(value: unknown, field: string): CharacterGuideFact {
  if (!isRecord(value)) {
    throw new Error(`${field} must be an object`);
  }
  return {
    label: requiredString(value.label, `${field} label`),
    description: requiredString(value.description, `${field} description`),
    confidence: requiredString(value.confidence, `${field} confidence`),
  };
}

function parseGuide(code: string, value: unknown): CharacterGuide {
  if (!isRecord(value)) {
    throw new Error(`character guide ${code} must be an object`);
  }
  if (
    !Array.isArray(value.combat) ||
    !Array.isArray(value.realmMilestones) ||
    !Array.isArray(value.artifacts)
  ) {
    throw new Error(`character guide ${code} must contain guide arrays`);
  }
  return {
    roles: stringArray(value.roles, `character guide ${code} roles`),
    attackPattern: requiredString(
      value.attackPattern,
      `character guide ${code} attack pattern`,
    ),
    range: requiredString(value.range, `character guide ${code} range`),
    complexity: requiredString(
      value.complexity,
      `character guide ${code} complexity`,
    ),
    summary: requiredString(value.summary, `character guide ${code} summary`),
    strengths: stringArray(value.strengths, `character guide ${code} strengths`),
    tradeoffs: stringArray(value.tradeoffs, `character guide ${code} tradeoffs`),
    firstSteps: stringArray(value.firstSteps, `character guide ${code} first steps`),
    combat: value.combat.map((raw, index) =>
      parseGuideFact(raw, `character guide ${code} combat ${index}`),
    ),
    realmMilestones: value.realmMilestones.map((raw, index) => {
      if (!isRecord(raw) || !Array.isArray(raw.unlocks)) {
        throw new Error(`character guide ${code} milestone ${index} is invalid`);
      }
      return {
        realm: requiredString(
          raw.realm,
          `character guide ${code} milestone ${index} realm`,
        ),
        unlocks: raw.unlocks.map((unlock, unlockIndex) =>
          parseGuideFact(
            unlock,
            `character guide ${code} milestone ${index} unlock ${unlockIndex}`,
          ),
        ),
      };
    }),
    artifacts: value.artifacts.map((raw, index) =>
      parseGuideFact(raw, `character guide ${code} artifact ${index}`),
    ),
  };
}

export function parseCharacterGuides(
  value: unknown,
): ReadonlyMap<string, CharacterGuide> {
  if (!isRecord(value) || value.schemaVersion !== 1 || !isRecord(value.guides)) {
    throw new Error("character guides must use schema version 1");
  }
  const guides = new Map<string, CharacterGuide>();
  for (const [code, raw] of Object.entries(value.guides)) {
    const identity = `tu_tien:${requiredString(code, "character guide code").toLowerCase()}`;
    if (guides.has(identity)) {
      throw new Error(`duplicate guide identity ${identity}`);
    }
    guides.set(identity, parseGuide(code, raw));
  }
  return guides;
}

function localized(value: LocalizedText, locale: CharacterLocale): string {
  const fallback = locale === "vi" ? "en" : "vi";
  return value[locale] || value[fallback];
}

function resolveEquipment(
  equipment: CharacterEquipmentSource,
  profile: CharacterProfileSource,
  items: ReadonlyMap<string, ItemListEntry>,
  locale: CharacterLocale,
): CharacterEquipment {
  const item = items.get(`${profile.namespace}:${equipment.code}`);
  const resolvedName = item
    ? locale === "en"
      ? item.englishName || item.name
      : item.name
    : localized(equipment.name, locale);
  return {
    code: equipment.code,
    name: resolvedName,
    quantity: equipment.quantity,
    effect: localized(equipment.effect, locale),
    icon: item?.sprite ?? null,
  };
}

export function buildCharacterCatalog(
  items: readonly ItemListEntry[],
  profiles: ReadonlyMap<string, CharacterProfileSource>,
  guides: ReadonlyMap<string, CharacterGuide>,
  locale: CharacterLocale,
): CharacterCatalogEntry[] {
  const itemsById = new Map(items.map((item) => [item.id, item]));
  return [...profiles.values()]
    .map((profile) => ({
      id: profile.id,
      code: profile.code,
      namespace: profile.namespace,
      name: localized(profile.name, locale),
      englishName: localized(profile.name, "en"),
      title: localized(profile.title, locale),
      description: localized(profile.description, locale),
      portrait: profile.portraitPath,
      stats: profile.stats,
      abilities: profile.abilities.map((ability) => ({
        name: localized(ability.name, locale),
        effect: localized(ability.effect, locale),
      })),
      startingItems: profile.startingItems.map((equipment) =>
        resolveEquipment(equipment, profile, itemsById, locale),
      ),
      artifacts: profile.artifacts.map((equipment) =>
        resolveEquipment(equipment, profile, itemsById, locale),
      ),
      guide: guides.get(profile.id) ?? null,
    }))
    .sort(
      (left, right) =>
        (left.namespace === "tu_tien" ? 0 : 1) -
          (right.namespace === "tu_tien" ? 0 : 1) ||
        left.name.localeCompare(right.name, locale) ||
        left.id.localeCompare(right.id),
    );
}

function normalizeSearchText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase()
    .replace(/đ/g, "d");
}

export function filterCharacters(
  characters: readonly CharacterCatalogEntry[],
  filters: CharacterFilters,
): CharacterCatalogEntry[] {
  const query = normalizeSearchText(filters.query?.trim() ?? "");
  return characters.filter((character) => {
    if (
      filters.namespace &&
      filters.namespace !== "all" &&
      character.namespace !== filters.namespace
    ) {
      return false;
    }
    if (!query) return true;
    return normalizeSearchText(
      [
        character.name,
        character.englishName,
        character.title,
        character.description,
        character.code,
        ...(character.guide?.roles ?? []),
      ].join(" "),
    ).includes(query);
  });
}

export function selectCharacters(
  items: readonly ItemListEntry[],
): ItemListEntry[] {
  return items.filter((item) => item.category === "character");
}
