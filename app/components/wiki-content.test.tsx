import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { WikiContent } from "./wiki-content";

const detail = {
  schema_version: 1,
  pageId: 105588,
  title: "Cảnh giới",
  canonicalUrl: "https://dontstarve.wiki.gg/wiki/Cultivation",
  html: "<h2>Nguồn nhận</h2><p>Nội dung Wiki tĩnh.</p>",
  summaryViHtml: null,
  categories: [],
  images: [],
  revision: { id: 9, sha1: "abc123", timestamp: "2026-07-27T00:00:00Z" },
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("WikiContent", () => {
  it("shows a loading state while the local article request is pending", () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise(() => undefined)));

    render(<WikiContent pageId={105588} canonicalUrl={detail.canonicalUrl} />);

    expect(screen.getByRole("status").textContent).toContain(
      "Đang tải bài viết Wiki",
    );
  });

  it("fetches the static page, validates it, and applies Wiki content tokens", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => detail,
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <WikiContent pageId={105588} canonicalUrl={detail.canonicalUrl} />,
    );

    expect(await screen.findByText("Nội dung Wiki tĩnh.")).toBeDefined();
    expect(fetchMock).toHaveBeenCalledWith("/data/wiki/pages/105588.json", {
      signal: expect.any(AbortSignal),
    });
    expect(screen.getByTestId("wiki-content").className).toContain(
      "[&_h2]:text-nova-text",
    );
  });

  it("shows an error and retries the same static page", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 503 })
      .mockResolvedValueOnce({ ok: true, json: async () => detail });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <WikiContent pageId={105588} canonicalUrl={detail.canonicalUrl} />,
    );

    expect(await screen.findByText("Không tải được bài viết Wiki")).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "Thử lại" }));
    expect(await screen.findByText("Nội dung Wiki tĩnh.")).toBeDefined();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("rejects article payloads outside the parsed Wiki contract", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ ...detail, html: "<script>alert(1)</script>" }),
      }),
    );

    render(<WikiContent pageId={105588} canonicalUrl={detail.canonicalUrl} />);

    expect(await screen.findByText("Không tải được bài viết Wiki")).toBeDefined();
    expect(document.querySelector("script")).toBeNull();
  });

  it("aborts the stale page request when the identity changes", () => {
    const signals: AbortSignal[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn((_input: RequestInfo | URL, init?: RequestInit) => {
        signals.push(init?.signal as AbortSignal);
        return new Promise<Response>(() => undefined);
      }),
    );

    const { rerender, unmount } = render(
      <WikiContent pageId={105588} canonicalUrl={detail.canonicalUrl} />,
    );
    rerender(<WikiContent pageId={100736} canonicalUrl={detail.canonicalUrl} />);

    expect(signals[0].aborted).toBe(true);
    expect(signals[1].aborted).toBe(false);
    unmount();
    expect(signals[1].aborted).toBe(true);
  });
});
