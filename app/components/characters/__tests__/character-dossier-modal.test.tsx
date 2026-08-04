import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { useState } from "react";
import { describe, expect, it } from "vitest";

import type { CharacterCatalogEntry } from "@/app/lib/character-catalog";
import { CharacterDossierModal } from "../character-dossier-modal";

const character: CharacterCatalogEntry = {
  id: "tu_tien:xd_wukong",
  code: "xd_wukong",
  namespace: "tu_tien",
  name: "Tôn Ngộ Không",
  englishName: "Sun Wukong",
  title: "Tề Thiên Đại Thánh",
  description: "Chiến binh biến hóa.",
  portrait: "/assets/dst/characters/xd_wukong.png",
  stats: {},
  abilities: [],
  startingItems: [],
  artifacts: [],
  guide: {
    roles: ["Cận chiến"],
    attackPattern: "Áp sát mục tiêu.",
    range: "melee",
    complexity: "advanced",
    summary: "Hồ sơ chiến thuật.",
    strengths: [],
    tradeoffs: [],
    firstSteps: [],
    combat: [],
    realmMilestones: [],
    artifacts: [],
  },
};

function ModalHarness() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)}>
        Mở hồ sơ từ thẻ
      </button>
      <CharacterDossierModal
        character={character}
        open={open}
        onOpenChange={setOpen}
      />
    </>
  );
}

describe("CharacterDossierModal", () => {
  it("opens a named, viewport-bounded dialog and focuses the overview tab", async () => {
    render(<ModalHarness />);
    fireEvent.click(screen.getByRole("button", { name: "Mở hồ sơ từ thẻ" }));

    const dialog = screen.getByRole("dialog", { name: "Tôn Ngộ Không" });
    expect(dialog.getAttribute("aria-modal")).toBe("true");
    expect(dialog.className).toContain("h-svh");
    expect(dialog.className).toContain("sm:max-w-[64rem]");
    await waitFor(() => {
      expect(document.activeElement).toBe(
        within(dialog).getByRole("tab", { name: "Tổng quan" }),
      );
    });
  });

  it("does not apply desktop centering utilities at the mobile breakpoint", () => {
    render(
      <CharacterDossierModal
        character={character}
        open
        onOpenChange={() => undefined}
      />,
    );

    const dialog = screen.getByRole("dialog");
    expect(dialog.classList).toContain("left-0");
    expect(dialog.classList).toContain("top-0");
    expect(dialog.classList).toContain("sm:left-1/2");
    expect(dialog.classList).toContain("sm:-translate-x-1/2");
    expect(dialog.classList).not.toContain("left-1/2");
    expect(dialog.classList).not.toContain("top-1/2");
    expect(dialog.classList).not.toContain("-translate-x-1/2");
    expect(dialog.classList).not.toContain("-translate-y-1/2");
  });

  it("supports automatic arrow-key tab navigation", async () => {
    render(
      <CharacterDossierModal
        character={character}
        open
        onOpenChange={() => undefined}
      />,
    );
    const dialog = screen.getByRole("dialog");
    const overview = within(dialog).getByRole("tab", { name: "Tổng quan" });
    overview.focus();
    fireEvent.keyDown(overview, { key: "ArrowRight" });

    await waitFor(() => {
      expect(
        within(dialog).getByRole("tab", { name: "Chiến đấu" }).getAttribute(
          "aria-selected",
        ),
      ).toBe("true");
    });
  });

  it("traps focus and restores it after Escape", async () => {
    render(<ModalHarness />);
    const trigger = screen.getByRole("button", { name: "Mở hồ sơ từ thẻ" });
    trigger.focus();
    fireEvent.click(trigger);
    const dialog = screen.getByRole("dialog");
    const lastTab = within(dialog).getByRole("tab", { name: "Pháp bảo" });
    act(() => lastTab.focus());
    fireEvent.keyDown(lastTab, { key: "Tab" });
    expect(dialog.contains(document.activeElement)).toBe(true);

    fireEvent.keyDown(document, { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(document.activeElement).toBe(trigger);
  });

  it("closes from the overlay and restores focus", async () => {
    render(<ModalHarness />);
    const trigger = screen.getByRole("button", { name: "Mở hồ sơ từ thẻ" });
    trigger.focus();
    fireEvent.click(trigger);
    const overlay = document.querySelector<HTMLElement>(
      '[data-slot="dialog-overlay"]',
    );
    expect(overlay).not.toBeNull();
    fireEvent.pointerDown(overlay!, { button: 0, ctrlKey: false, pointerType: "mouse" });
    fireEvent.pointerUp(overlay!, { button: 0, ctrlKey: false, pointerType: "mouse" });
    fireEvent.click(overlay!);

    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(document.activeElement).toBe(trigger);
  });
});
