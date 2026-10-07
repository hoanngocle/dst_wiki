import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { TuTienHub } from "./tu-tien-hub";
import snapshot from "@/data/generated/tu-tien-mods.json";

it("includes ingredients and actual output counts for all 18 copied Nyx recipes", () => {
  const rows=snapshot.mods.find(mod=>mod.id==="nyx")!.entries.filter(row=>row.id.startsWith("copied:"));
  expect(rows).toHaveLength(18);
  for (const row of rows) {
    expect(row.ingredients.length,row.id).toBeGreaterThan(0);
    expect(row.facts.some(f=>f.label==="Thành phẩm"),row.id).toBe(true);
    expect(row.text.join(" ")).not.toContain("dùng công thức và thành phẩm gốc");
  }
  expect(rows.find(row=>row.id==="copied:xd_htz_sjcx")!.facts).toContainEqual({label:"Máu tiêu hao",value:"90"});
  expect(rows.find(row=>row.id==="copied:xd_htz_xyzzl")!.facts).toContainEqual({label:"Máu tiêu hao",value:"120"});
});

it("prints the recipe directly and shows four turf pieces rather than one", () => {
  window.history.replaceState(null,"","/tu-tien#nyx");
  render(<TuTienHub crafting={null} cultivation={null} mods={snapshot.mods} referenceItems={[]} sprites={{}} />);
  fireEvent.change(screen.getByRole("combobox",{name:"Nhóm nội dung Nyx"}),{target:{value:"Công thức Nyx"}});
  fireEvent.change(screen.getByRole("searchbox",{name:"Tìm trong Nyx"}),{target:{value:"turf_jingweitile"}});
  expect(screen.getByText("Thảm Đất Điền Hải ×4")).toBeDefined();
  expect(screen.getByText(/Huyền Vũ.*×1.*Twigs.*×4/)).toBeDefined();
});
