export type TaskSlot = "character" | "seasonal" | "repeat";
export type Season = "spring" | "winter" | "summer" | "autumn" | "fallback";

export interface AchievementLevelTask {
  key: string;
  sourceId: string;
  name: string;
  instructions: string;
  event: string;
}

export interface AchievementLevelTaskGroup {
  id: string;
  label: string;
  slot: TaskSlot;
  season: Season | null;
  character: string | null;
  repeatCount: number;
  tasks: readonly AchievementLevelTask[];
}

export interface AchievementRecord {
  id: string;
  name: string;
  description: string;
  target: string;
  stars: number;
  characterRequirement: string;
  category: string;
}

export interface PerkRecord {
  id: string;
  name: string;
  description: string;
  cost: number;
  scope: string;
  notes: string | null;
  category: string;
}

export interface CharacterReward {
  character: string;
  effect: string;
}

export interface LevelAttribute {
  name: string;
  increase: string;
  multi: string;
}

export interface TaskMilestone {
  completed: number;
  reward: string;
}

export interface AchievementLevelData {
  meta: {
    workshopId: "2937640068";
    name: "Achievement & Level";
    version: "7.3.4";
    locale: "vi";
    taskPoolCount: 28;
    characterTaskGroupCount: 18;
  };
  taskGroups: readonly AchievementLevelTaskGroup[];
  achievements: readonly AchievementRecord[];
  perks: readonly PerkRecord[];
  rewards: {
    task2: readonly CharacterReward[];
    task4: readonly CharacterReward[];
  };
  level: {
    summary: readonly string[];
    starCurrency: string;
    taskMilestones: readonly TaskMilestone[];
    playerAttributes: readonly LevelAttribute[];
    petAttributes: readonly LevelAttribute[];
  };
}

export interface AchievementLevelCounts {
  tasks: number;
  taskPools: number;
  characterTaskGroups: number;
  achievements: number;
  perks: number;
}

export type TaskResult = AchievementLevelTask & {
  groupId: string;
  groupLabel: string;
  slot: TaskSlot;
  season: Season | null;
  character: string | null;
  repeatCount: number;
};

export interface TaskFilters {
  query: string;
  slot: TaskSlot | "all";
  season: Season | "all";
  character: string;
}

export interface AchievementFilters {
  query: string;
  category: string;
}

export interface PerkFilters {
  query: string;
  category: string;
  character: string;
}

const taskSlots: readonly TaskSlot[] = ["character", "seasonal", "repeat"];
const seasons: readonly Season[] = ["spring", "winter", "summer", "autumn", "fallback"];

function fail(path: string, expectation: string): never {
  throw new Error(`${path} ${expectation}`);
}

function record(value: unknown, path: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return fail(path, "must be an object");
  }
  return value as Record<string, unknown>;
}

function array(value: unknown, path: string): readonly unknown[] {
  if (!Array.isArray(value)) return fail(path, "must be an array");
  return value;
}

function requiredString(value: unknown, path: string): string {
  if (typeof value !== "string" || value.length === 0) {
    return fail(path, "must be a non-empty string");
  }
  return value;
}

function nullableString(value: unknown, path: string): string | null {
  if (value === null) return null;
  return requiredString(value, path);
}

function requiredNumber(value: unknown, path: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return fail(path, "must be a finite number");
  }
  return value;
}

function parseTask(value: unknown, path: string): AchievementLevelTask {
  const source = record(value, path);
  return {
    key: requiredString(source.key, `${path}.key`),
    sourceId: requiredString(source.sourceId, `${path}.sourceId`),
    name: requiredString(source.name, `${path}.name`),
    instructions: requiredString(source.instructions, `${path}.instructions`),
    event: requiredString(source.event, `${path}.event`),
  };
}

function parseTaskGroup(value: unknown, path: string): AchievementLevelTaskGroup {
  const source = record(value, path);
  const slot = requiredString(source.slot, `${path}.slot`);
  if (!taskSlots.includes(slot as TaskSlot)) {
    return fail(`${path}.slot`, "must be character, seasonal, or repeat");
  }
  const season = nullableString(source.season, `${path}.season`);
  if (season !== null && !seasons.includes(season as Season)) {
    return fail(`${path}.season`, "must be a supported season");
  }
  const tasks = array(source.tasks, `${path}.tasks`).map((task, index) =>
    parseTask(task, `${path}.tasks[${index}]`),
  );
  return {
    id: requiredString(source.id, `${path}.id`),
    label: requiredString(source.label, `${path}.label`),
    slot: slot as TaskSlot,
    season: season as Season | null,
    character: nullableString(source.character, `${path}.character`),
    repeatCount: requiredNumber(source.repeatCount, `${path}.repeatCount`),
    tasks,
  };
}

function parseAchievement(value: unknown, path: string): AchievementRecord {
  const source = record(value, path);
  return {
    id: requiredString(source.id, `${path}.id`),
    name: requiredString(source.name, `${path}.name`),
    description: requiredString(source.description, `${path}.description`),
    target: requiredString(source.target, `${path}.target`),
    stars: requiredNumber(source.stars, `${path}.stars`),
    characterRequirement: requiredString(
      source.characterRequirement,
      `${path}.characterRequirement`,
    ),
    category: requiredString(source.category, `${path}.category`),
  };
}

function parsePerk(value: unknown, path: string): PerkRecord {
  const source = record(value, path);
  return {
    id: requiredString(source.id, `${path}.id`),
    name: requiredString(source.name, `${path}.name`),
    description: requiredString(source.description, `${path}.description`),
    cost: requiredNumber(source.cost, `${path}.cost`),
    scope: requiredString(source.scope, `${path}.scope`),
    notes: nullableString(source.notes, `${path}.notes`),
    category: requiredString(source.category, `${path}.category`),
  };
}

function parseReward(value: unknown, path: string): CharacterReward {
  const source = record(value, path);
  return {
    character: requiredString(source.character, `${path}.character`),
    effect: requiredString(source.effect, `${path}.effect`),
  };
}

function parseLevelAttribute(value: unknown, path: string): LevelAttribute {
  const source = record(value, path);
  return {
    name: requiredString(source.name, `${path}.name`),
    increase: requiredString(source.increase, `${path}.increase`),
    multi: requiredString(source.multi, `${path}.multi`),
  };
}

function parseTaskMilestone(value: unknown, path: string): TaskMilestone {
  const source = record(value, path);
  return {
    completed: requiredNumber(source.completed, `${path}.completed`),
    reward: requiredString(source.reward, `${path}.reward`),
  };
}

function assertExact(value: unknown, expected: string | number, path: string): void {
  if (value !== expected) fail(path, `must equal ${String(expected)}`);
}

function assertUnique(values: readonly string[], label: string): void {
  const seen = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) throw new Error(`duplicate ${label}: ${value}`);
    seen.add(value);
  }
}

export function parseAchievementLevelData(value: unknown): AchievementLevelData {
  const source = record(value, "achievementLevel");
  const meta = record(source.meta, "meta");
  assertExact(meta.workshopId, "2937640068", "meta.workshopId");
  assertExact(meta.name, "Achievement & Level", "meta.name");
  assertExact(meta.version, "7.3.4", "meta.version");
  assertExact(meta.locale, "vi", "meta.locale");
  assertExact(meta.taskPoolCount, 28, "meta.taskPoolCount");
  assertExact(meta.characterTaskGroupCount, 18, "meta.characterTaskGroupCount");

  const taskGroups = array(source.taskGroups, "taskGroups").map((group, index) =>
    parseTaskGroup(group, `taskGroups[${index}]`),
  );
  const achievements = array(source.achievements, "achievements").map(
    (achievement, index) => parseAchievement(achievement, `achievements[${index}]`),
  );
  const perks = array(source.perks, "perks").map((perk, index) =>
    parsePerk(perk, `perks[${index}]`),
  );
  const rewardsSource = record(source.rewards, "rewards");
  const task2 = array(rewardsSource.task2, "rewards.task2").map((reward, index) =>
    parseReward(reward, `rewards.task2[${index}]`),
  );
  const task4 = array(rewardsSource.task4, "rewards.task4").map((reward, index) =>
    parseReward(reward, `rewards.task4[${index}]`),
  );
  const levelSource = record(source.level, "level");
  const summary = array(levelSource.summary, "level.summary").map((line, index) =>
    requiredString(line, `level.summary[${index}]`),
  );
  const starCurrency = requiredString(levelSource.starCurrency, "level.starCurrency");
  const taskMilestones = array(levelSource.taskMilestones, "level.taskMilestones").map(
    (milestone, index) => parseTaskMilestone(milestone, `level.taskMilestones[${index}]`),
  );
  const playerAttributes = array(
    levelSource.playerAttributes,
    "level.playerAttributes",
  ).map((attribute, index) =>
    parseLevelAttribute(attribute, `level.playerAttributes[${index}]`),
  );
  const petAttributes = array(levelSource.petAttributes, "level.petAttributes").map(
    (attribute, index) => parseLevelAttribute(attribute, `level.petAttributes[${index}]`),
  );

  const taskCount = taskGroups.reduce((total, group) => total + group.tasks.length, 0);
  if (taskCount !== 763) {
    throw new Error(`Achievement & Level data must contain 763 tasks; received ${taskCount}`);
  }
  if (taskGroups.length !== 28) {
    throw new Error(
      `Achievement & Level data must contain 28 task pools; received ${taskGroups.length}`,
    );
  }
  const characterTaskGroupCount = taskGroups.filter(
    (group) => group.slot === "character",
  ).length;
  if (characterTaskGroupCount !== 18) {
    throw new Error("Achievement & Level data must contain 18 character task groups");
  }
  if (achievements.length !== 169) {
    throw new Error(
      `Achievement & Level data must contain 169 achievements; received ${achievements.length}`,
    );
  }
  if (perks.length !== 128) {
    throw new Error(
      `Achievement & Level data must contain 128 perks; received ${perks.length}`,
    );
  }
  if (task2.length !== 19) {
    throw new Error(`Achievement & Level data must contain 19 task-2 rewards; received ${task2.length}`);
  }
  if (task4.length !== 11) {
    throw new Error(`Achievement & Level data must contain 11 task-4 rewards; received ${task4.length}`);
  }
  if (summary.length !== 3) {
    throw new Error(`Achievement & Level data must contain 3 level summary lines; received ${summary.length}`);
  }
  if (taskMilestones.length !== 4 || taskMilestones.some((item, index) => item.completed !== index + 1)) {
    throw new Error("Achievement & Level data must contain task milestones 1 through 4");
  }
  if (playerAttributes.length !== 6) {
    throw new Error(`Achievement & Level data must contain 6 player attributes; received ${playerAttributes.length}`);
  }
  if (petAttributes.length !== 6) {
    throw new Error(`Achievement & Level data must contain 6 pet attributes; received ${petAttributes.length}`);
  }

  assertUnique(taskGroups.map((group) => group.id), "task group id");
  assertUnique(taskGroups.flatMap((group) => group.tasks.map((task) => task.key)), "task key");
  assertUnique(achievements.map((achievement) => achievement.id), "achievement id");
  assertUnique(perks.map((perk) => perk.id), "perk id");

  return {
    meta: {
      workshopId: "2937640068",
      name: "Achievement & Level",
      version: "7.3.4",
      locale: "vi",
      taskPoolCount: 28,
      characterTaskGroupCount: 18,
    },
    taskGroups,
    achievements,
    perks,
    rewards: { task2, task4 },
    level: { summary, starCurrency, taskMilestones, playerAttributes, petAttributes },
  };
}

export function getAchievementLevelCounts(data: AchievementLevelData): AchievementLevelCounts {
  return {
    tasks: data.taskGroups.reduce((total, group) => total + group.tasks.length, 0),
    taskPools: data.taskGroups.length,
    characterTaskGroups: data.taskGroups.filter((group) => group.slot === "character").length,
    achievements: data.achievements.length,
    perks: data.perks.length,
  };
}

export function normalizeAchievementLevelSearch(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("vi")
    .trim();
}

function matchesQuery(query: string, values: readonly (string | null)[]): boolean {
  const normalizedQuery = normalizeAchievementLevelSearch(query);
  if (!normalizedQuery) return true;
  return values.some((value) =>
    normalizeAchievementLevelSearch(value ?? "").includes(normalizedQuery),
  );
}

export function filterTasks(
  data: AchievementLevelData,
  filters: TaskFilters,
): readonly TaskResult[] {
  return data.taskGroups.flatMap((group) =>
    group.tasks
      .map((task): TaskResult => ({
        ...task,
        groupId: group.id,
        groupLabel: group.label,
        slot: group.slot,
        season: group.season,
        character: group.character,
        repeatCount: group.repeatCount,
      }))
      .filter(
        (task) =>
          (filters.slot === "all" || task.slot === filters.slot) &&
          (filters.season === "all" || task.season === filters.season) &&
          (filters.character === "all" || task.character === filters.character) &&
          matchesQuery(filters.query, [
            task.name,
            task.instructions,
            task.event,
            task.sourceId,
            task.groupLabel,
            task.character,
          ]),
      ),
  );
}

export function filterAchievements(
  data: AchievementLevelData,
  filters: AchievementFilters,
): readonly AchievementRecord[] {
  return data.achievements.filter(
    (achievement) =>
      (filters.category === "all" || achievement.category === filters.category) &&
      matchesQuery(filters.query, [
        achievement.id,
        achievement.name,
        achievement.description,
        achievement.characterRequirement,
        achievement.category,
      ]),
  );
}

export function filterPerks(
  data: AchievementLevelData,
  filters: PerkFilters,
): readonly PerkRecord[] {
  const normalizedCharacter = normalizeAchievementLevelSearch(filters.character);
  return data.perks.filter(
    (perk) =>
      (filters.category === "all" || perk.category === filters.category) &&
      (filters.character === "all" ||
        normalizeAchievementLevelSearch(perk.scope).includes(normalizedCharacter)) &&
      matchesQuery(filters.query, [
        perk.id,
        perk.name,
        perk.description,
        perk.scope,
        perk.notes,
        perk.category,
      ]),
  );
}
