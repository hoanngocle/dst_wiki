import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import payload from "@/public/data/items.json";
import characterItems from "./__fixtures__/character-items.json";
import { parseItemPayload } from "@/app/lib/item-catalog";
import { ItemDetailModal } from "./item-detail-modal";

const items = parseItemPayload({ ...payload, items: [...payload.items, ...characterItems] });
const itemsById = new Map(items.map((item) => [item.id, item]));

describe("character requirements", () => {
  it("shows Wendy separately for crafting and using Abigail's Flower", () => {
    render(<ItemDetailModal item={itemsById.get("base_game:abigail_flower")!} itemsById={itemsById} onClose={vi.fn()} onSelectItem={vi.fn()} />);
    const crafting = screen.getByText("Nhân vật yêu cầu (chế tạo):");
    const usage = screen.getByText("Nhân vật yêu cầu (sử dụng):");
    expect(crafting.closest("section")?.textContent).toContain("Công thức");
    expect(crafting.parentElement?.textContent).toContain("Wendy");
    expect(usage.closest("section")?.textContent).toContain("Cách Sử dụng");
    expect(usage.parentElement?.textContent).toContain("Wendy");
  });

  it("does not infer a usage restriction from a character's crafting recipe", () => {
    const armor = itemsById.get("base_game:armor_bramble")!;
    expect(armor.characterRequirements?.crafting.text).toContain("Wormwood");
    expect(armor.characterRequirements?.usage.status).toBe("unknown");
    render(<ItemDetailModal item={armor} itemsById={itemsById} onClose={vi.fn()} onSelectItem={vi.fn()} />);
    expect(screen.getByText("Nhân vật yêu cầu (chế tạo):")).toBeDefined();
    expect(screen.queryByText("Nhân vật yêu cầu (sử dụng):")).toBeNull();
  });

  it("does not mark ordinary logs as character-exclusive", () => {
    expect(itemsById.get("base_game:log")?.characterRequirements?.crafting.status).toBe("unknown");
  });
});
