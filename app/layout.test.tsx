import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";

import RootLayout, { metadata } from "./layout";

it("defines a root metadata base URL", () => {
  expect(metadata.metadataBase).toBeInstanceOf(URL);
});

it("wraps the standalone site in the light DST shell", () => {
  const markup = renderToStaticMarkup(
    <RootLayout>
      <main>Catalog content</main>
    </RootLayout>,
  );

  expect(markup).toContain('class="nova-game-theme min-h-dvh text-nova-text"');
});

it("describes items, Hàn Lập crafting, and cultivation realms without generic guides", () => {
  expect(metadata.description).toContain("vật phẩm");
  expect(metadata.description).toContain("đồ chế Tu Tiên");
  expect(metadata.description).toContain("cảnh giới Tu Tiên");
  expect(metadata.description).not.toContain("nhân vật");
  expect(metadata.description).not.toContain("hướng dẫn");
});

it("uses the approved light palette instead of the former dark root colors", () => {
  const globals = readFileSync(join(process.cwd(), "app/globals.css"), "utf8");

  for (const color of ["#edf1f5", "#14233b", "#f8fafc", "#53647a", "#cbd5e1", "#2e5fb3"]) {
    expect(globals).toContain(color);
  }

  for (const color of ["#050914", "#091323", "#111f35", "#10203a", "#67e8f9"]) {
    expect(globals).not.toContain(color);
  }
});
