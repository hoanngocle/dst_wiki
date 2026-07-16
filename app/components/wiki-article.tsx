"use client";

import { ArrowSquareOut, WarningCircle } from "@phosphor-icons/react";
import Image from "next/image";
import { useEffect, useState } from "react";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import {
  parseWikiPageDetail,
  type WikiPageDetail,
} from "@/app/lib/wiki-detail";
import { WikiStructuredSections } from "./wiki-structured-sections";

const EMPTY_ITEMS = new Map<string, ItemListEntry>();
const IGNORE_ITEM_SELECTION = () => undefined;

type ArticleState =
  | { status: "loading" }
  | { status: "ready"; detail: WikiPageDetail }
  | { status: "error" };

function CanonicalLink({ href }: { href: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-[#b9cce8] px-3 py-2 text-sm font-semibold text-[#2e5fb3] transition hover:bg-[#e9f1fb] active:scale-[0.98]"
    >
      Mở trên Don&apos;t Starve Wiki
      <ArrowSquareOut aria-hidden="true" size={17} />
    </a>
  );
}

export function WikiArticle({
  detailUrl,
  canonicalUrl,
  itemsById = EMPTY_ITEMS,
  onSelectItem = IGNORE_ITEM_SELECTION,
}: {
  detailUrl: string;
  canonicalUrl: string;
  itemsById?: ReadonlyMap<string, ItemListEntry>;
  onSelectItem?: (item: ItemListEntry) => void;
}) {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<ArticleState>({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    async function loadArticle() {
      try {
        const response = await fetch(detailUrl, { signal: controller.signal });
        if (!response.ok) throw new Error(`wiki detail request failed: ${response.status}`);
        const detail = parseWikiPageDetail(await response.json());
        if (active) setState({ status: "ready", detail });
      } catch (error) {
        if (active && !(error instanceof DOMException && error.name === "AbortError")) {
          setState({ status: "error" });
        }
      }
    }

    void loadArticle();
    return () => {
      active = false;
      controller.abort();
    };
  }, [attempt, detailUrl]);

  if (state.status === "loading") {
    return (
      <section
        role="status"
        aria-label="Đang tải bài viết Wiki"
        className="rounded-2xl border border-[#c8d3df] bg-[#f8fafc] p-5"
      >
        <p className="text-sm font-semibold text-[#263b58]">Đang tải bài viết Wiki...</p>
        <div aria-hidden="true" className="mt-4 animate-pulse space-y-3 motion-reduce:animate-none">
          <div className="h-5 w-2/5 rounded bg-[#d5dde6]" />
          <div className="h-3 w-full rounded bg-[#e1e7ee]" />
          <div className="h-3 w-5/6 rounded bg-[#e1e7ee]" />
        </div>
      </section>
    );
  }

  if (state.status === "error") {
    return (
      <section className="rounded-2xl border border-[#c8d3df] bg-[#f8fafc] p-5">
        <div className="flex items-start gap-3">
          <WarningCircle
            aria-hidden="true"
            size={22}
            weight="duotone"
            className="mt-0.5 shrink-0 text-[#9a5a2a]"
          />
          <div>
            <h3 className="font-semibold text-[#172943]">Không tải được bài viết Wiki</h3>
            <p className="mt-1 text-sm leading-6 text-[#607188]">
              Chi tiết cơ bản vẫn dùng được. Bạn có thể thử lại hoặc mở nguồn gốc.
            </p>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => {
              setState({ status: "loading" });
              setAttempt((current) => current + 1);
            }}
            className="min-h-11 cursor-pointer rounded-xl bg-[#2e5fb3] px-4 py-2 text-sm font-semibold text-[#f8fafc] transition hover:bg-[#264f96] active:scale-[0.98]"
          >
            Thử lại
          </button>
          <CanonicalLink href={canonicalUrl} />
        </div>
      </section>
    );
  }

  return (
    <section className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#d5dde6] px-4 py-3">
        <h3 className="font-semibold text-[#172943]">Bài viết Wiki</h3>
        <CanonicalLink href={state.detail.canonicalUrl} />
      </div>
      {state.detail.images.length ? (
        <section
          aria-label="Gallery"
          className="border-b border-[#d5dde6] bg-[#eef3f8] px-4 py-4 sm:px-5"
        >
          <h4 className="text-sm font-semibold text-[#263b58]">Gallery</h4>
          <div
            data-gallery-grid
            className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4"
          >
            {state.detail.images.slice(0, 12).map((image) => {
              const caption = image.title.replace(/^File:/i, "");
              return (
                <figure
                  key={`${image.title}:${image.src}`}
                  tabIndex={0}
                  aria-label={caption}
                  className="group relative aspect-square overflow-hidden rounded-xl border border-[#c8d3df] bg-[#f8fafc] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/40"
                >
                  <Image
                    src={image.src}
                    alt={image.title}
                    width={image.width ?? 256}
                    height={image.height ?? 256}
                    unoptimized
                    className="h-full w-full object-contain p-3"
                  />
                  <figcaption className="absolute inset-x-0 bottom-0 line-clamp-3 bg-[#172943]/90 px-3 py-2 text-xs leading-5 text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
                    {caption}
                  </figcaption>
                </figure>
              );
            })}
          </div>
        </section>
      ) : null}
      {state.detail.normalized ? (
        <div className="border-b border-[#d5dde6] bg-[#edf1f5] p-4 sm:p-5">
          <WikiStructuredSections
            sections={state.detail.normalized}
            itemsById={itemsById}
            onSelectItem={onSelectItem}
          />
        </div>
      ) : null}
      <div
        className="wiki-article p-4 sm:p-5"
        dangerouslySetInnerHTML={{
          __html: state.detail.summaryViHtml ?? state.detail.html,
        }}
      />
    </section>
  );
}
