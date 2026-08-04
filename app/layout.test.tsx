import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";

import RootLayout, { metadata } from "./layout";

it("defines a root metadata base URL", () => {
  expect(metadata.metadataBase).toBeInstanceOf(URL);
});

it("wraps the standalone site in the dark DST shell", () => {
  const markup = renderToStaticMarkup(
    <RootLayout>
      <main>Catalog content</main>
    </RootLayout>,
  );

  expect(markup).toContain('class="nova-game-theme min-h-dvh text-nova-text"');
});
