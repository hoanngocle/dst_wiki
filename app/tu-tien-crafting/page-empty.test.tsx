import { expect, it, vi } from "vitest";

vi.mock("@/app/lib/tu-tien-crafting", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/app/lib/tu-tien-crafting")>();

  return {
    ...actual,
    selectHanLapCraftables: () => ({
      items: [],
      excluded: [
        { id: "tu_tien:no_recipe", reason: "no_recipe" },
        { id: "tu_tien:locked", reason: "other_character" },
        { id: "tu_tien:no_use", reason: "no_verified_use" },
        { id: "tu_tien:missing", reason: "unresolved_ingredient" },
      ],
    }),
  };
});

it("fails server rendering with exclusion counts when selection is empty", async () => {
  await expect(import("./page")).rejects.toThrow(
    /selected=0.*excluded=4.*no_recipe=1.*other_character=1.*no_verified_use=1.*unresolved_ingredient=1/i,
  );
});
