import { expect, it, vi } from "vitest";

const { notFound } = vi.hoisted(() => ({
  notFound: vi.fn(() => {
    throw new Error("not found");
  }),
}));

vi.mock("next/navigation", () => ({ notFound }));

import GuidePage, { generateMetadata, generateStaticParams } from "./page";

it("builds only the four reviewed JSON guide routes", () => {
  expect(generateStaticParams()).toEqual([
    { slug: "how-to-kill-the-giants-in-dst" },
    { slug: "maximum-efficiency-day-13-base-dst-guide" },
    { slug: "slurtle-slime-guide" },
    { slug: "taming-a-beefalo" },
  ]);
  expect(generateStaticParams().some(({ slug }) => slug === "canh-gioi-tu-tien")).toBe(false);
});

it("derives metadata from the validated article and rejects an unpublished slug", async () => {
  await expect(generateMetadata({ params: Promise.resolve({ slug: "taming-a-beefalo" }) })).resolves.toMatchObject({
    title: "Thuần hóa Beefalo | Guide DST",
    description: "Hướng dẫn tăng mức tuân lệnh, độ thuần hóa và chọn khuynh hướng cho Beefalo.",
  });
  await expect(GuidePage({ params: Promise.resolve({ slug: "unpublished-guide" }) })).rejects.toThrow("not found");
  expect(notFound).toHaveBeenCalledOnce();
});
