"use client";

import { ArrowSquareOut, WarningCircle } from "@phosphor-icons/react";
import { type ReactNode, useEffect, useState } from "react";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { cn } from "@/app/lib/cn";
import {
  buildWikiDetailUrl,
  parseWikiPageDetail,
  type WikiPageDetail,
} from "@/app/lib/wiki-detail";
import { WikiArticle } from "./wiki-article";

const EMPTY_ITEMS = new Map<string, ItemListEntry>();
const IGNORE_ITEM_SELECTION = () => undefined;

type ContentState =
  | { status: "loading"; pageId: number }
  | { status: "ready"; pageId: number; detail: WikiPageDetail }
  | { status: "error"; pageId: number };

export const wikiContentClassName = [
  "min-w-0 text-sm leading-7 text-nova-muted [overflow-wrap:anywhere]",
  "[&_h1]:text-nova-text [&_h2]:text-nova-text [&_h3]:text-nova-text",
  "[&_a]:font-semibold [&_a]:text-nova-accent [&_a]:underline [&_a]:underline-offset-4",
  "[&_img]:h-auto [&_img]:max-w-full",
  "[&_table]:max-w-full [&_table]:border-collapse",
  "[&_th]:border-nova-border [&_td]:border-nova-border",
].join(" ");

export function WikiContent({
  pageId,
  canonicalUrl,
  itemsById = EMPTY_ITEMS,
  onSelectItem = IGNORE_ITEM_SELECTION,
  fallbackSummary = null,
  contentAfterSummary = null,
  className,
}: {
  pageId: number;
  canonicalUrl: string;
  itemsById?: ReadonlyMap<string, ItemListEntry>;
  onSelectItem?: (item: ItemListEntry) => void;
  fallbackSummary?: ReactNode;
  contentAfterSummary?: ReactNode;
  className?: string;
}) {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<ContentState>({ status: "loading", pageId });
  const detailUrl = buildWikiDetailUrl({ pageId });

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    async function loadContent() {
      try {
        const response = await fetch(detailUrl, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`wiki detail request failed: ${response.status}`);
        }
        const detail = parseWikiPageDetail(await response.json());
        if (active) setState({ status: "ready", pageId, detail });
      } catch (error) {
        if (active && !(error instanceof DOMException && error.name === "AbortError")) {
          setState({ status: "error", pageId });
        }
      }
    }

    void loadContent();
    return () => {
      active = false;
      controller.abort();
    };
  }, [attempt, detailUrl, pageId]);

  let content: ReactNode;

  if (state.pageId !== pageId || state.status === "loading") {
    content = (
      <>
        {fallbackSummary}
        {contentAfterSummary}
        <section
          role="status"
          aria-label="Đang tải bài viết Wiki"
          className="rounded-2xl border border-nova-border bg-nova-surface-soft p-5"
        >
          <p className="text-sm font-semibold text-nova-text">Đang tải bài viết Wiki...</p>
          <div
            aria-hidden="true"
            className="mt-4 animate-pulse space-y-3 motion-reduce:animate-none"
          >
            <div className="h-5 w-2/5 rounded bg-nova-border" />
            <div className="h-3 w-full rounded bg-nova-border" />
            <div className="h-3 w-5/6 rounded bg-nova-border" />
          </div>
        </section>
      </>
    );
  } else if (state.status === "error") {
    content = (
      <>
        {fallbackSummary}
        {contentAfterSummary}
        <section className="rounded-2xl border border-nova-border bg-nova-surface-soft p-5">
          <div className="flex items-start gap-3">
            <WarningCircle
              aria-hidden="true"
              size={22}
              weight="duotone"
              className="mt-0.5 shrink-0 text-nova-warning"
            />
            <div>
              <h3 className="font-semibold text-nova-text">
                Không tải được bài viết Wiki
              </h3>
              <p className="mt-1 text-sm leading-6 text-nova-muted">
                Chi tiết cơ bản vẫn dùng được. Bạn có thể thử lại hoặc mở nguồn gốc.
              </p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => {
                setState({ status: "loading", pageId });
                setAttempt((current) => current + 1);
              }}
              className="min-h-11 cursor-pointer rounded-xl bg-nova-accent px-4 py-2 text-sm font-semibold text-nova-surface-soft transition hover:bg-nova-accent active:scale-[0.98]"
            >
              Thử lại
            </button>
            <a
              href={canonicalUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-nova-accent/30 px-3 py-2 text-sm font-semibold text-nova-accent transition hover:bg-nova-accent/10 active:scale-[0.98]"
            >
              Mở trên Don&apos;t Starve Wiki
              <ArrowSquareOut aria-hidden="true" size={17} />
            </a>
          </div>
        </section>
      </>
    );
  } else {
    content = (
      <WikiArticle
        detail={state.detail}
        itemsById={itemsById}
        onSelectItem={onSelectItem}
        fallbackSummary={fallbackSummary}
        contentAfterSummary={contentAfterSummary}
      />
    );
  }

  return (
    <div data-testid="wiki-content" className={cn(wikiContentClassName, className)}>
      {content}
    </div>
  );
}
