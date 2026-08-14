import { describe, expect, it } from "vitest";

import payload from "../../data/manual/achievement-level.json";
import {
  filterAchievements,
  filterPerks,
  filterTasks,
  getAchievementLevelCounts,
  parseAchievementLevelData,
} from "./achievement-level";

const data = parseAchievementLevelData(payload);

describe("parseAchievementLevelData", () => {
  it("validates the complete Workshop snapshot", () => {
    expect(getAchievementLevelCounts(data)).toEqual({
      tasks: 763,
      taskPools: 28,
      characterTaskGroups: 18,
      achievements: 169,
      perks: 128,
    });
  });

  it("rejects an incomplete artifact", () => {
    const incomplete = structuredClone(payload);
    incomplete.perks.pop();

    expect(() => parseAchievementLevelData(incomplete)).toThrow(/128 perks/);
  });

  it.each([
    ["task-2 rewards", (value: typeof payload) => value.rewards.task2.pop(), /19 task-2 rewards/],
    ["task-4 rewards", (value: typeof payload) => value.rewards.task4.pop(), /11 task-4 rewards/],
    ["level summary", (value: typeof payload) => value.level.summary.pop(), /3 level summary lines/],
    ["player attributes", (value: typeof payload) => value.level.playerAttributes.pop(), /6 player attributes/],
    ["pet attributes", (value: typeof payload) => value.level.petAttributes.pop(), /6 pet attributes/],
  ])("rejects truncated %s", (_label, truncate, message) => {
    const incomplete = structuredClone(payload);
    truncate(incomplete);

    expect(() => parseAchievementLevelData(incomplete)).toThrow(message);
  });

  it("rejects duplicate task occurrence keys", () => {
    const duplicate = structuredClone(payload);
    duplicate.taskGroups[0].tasks[1].key = duplicate.taskGroups[0].tasks[0].key;

    expect(() => parseAchievementLevelData(duplicate)).toThrow(/duplicate task key/);
  });

  it("reports the path of malformed fields", () => {
    const malformed = structuredClone(payload) as unknown as {
      achievements: Array<{ name: unknown }>;
    };
    malformed.achievements[0].name = null;

    expect(() => parseAchievementLevelData(malformed)).toThrow(/achievements\[0\]\.name/);
  });
});

describe("selectors", () => {
  it("filters task occurrences without deduplicating pool context", () => {
    const batilisks = filterTasks(data, {
      query: "batilisk",
      slot: "all",
      season: "all",
      character: "all",
    });

    expect(batilisks.length).toBeGreaterThan(1);
    expect(new Set(batilisks.map((task) => task.key)).size).toBe(batilisks.length);
  });

  it("filters tasks by repeat slot and winter", () => {
    expect(
      filterTasks(data, {
        query: "",
        slot: "repeat",
        season: "winter",
        character: "all",
      }),
    ).toHaveLength(18);
  });

  it("filters tasks by required character", () => {
    expect(
      filterTasks(data, {
        query: "",
        slot: "character",
        season: "all",
        character: "Wilson",
      }),
    ).toHaveLength(18);
  });

  it("normalizes Vietnamese search and filters achievements", () => {
    const results = filterAchievements(data, {
      query: "than chet",
      category: "all",
    });

    expect(results.some((achievement) => achievement.id === "death")).toBe(true);
  });

  it("filters achievements by category", () => {
    expect(
      filterAchievements(data, { query: "", category: "Ăn uống" }),
    ).toHaveLength(14);
  });

  it("filters character perks", () => {
    const results = filterPerks(data, {
      query: "",
      category: "Chuyên môn nhân vật",
      character: "Wanda",
    });

    expect(results.length).toBeGreaterThan(0);
    expect(results.every((perk) => perk.scope.includes("Wanda"))).toBe(true);
  });
});
