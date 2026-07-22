import { expect, it } from "vitest";

import { metadata } from "./layout";

it("defines a root metadata base URL", () => {
  expect(metadata.metadataBase).toBeInstanceOf(URL);
});
