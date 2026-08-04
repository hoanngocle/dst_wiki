import { ArrowSquareOut } from "@phosphor-icons/react";
import Image from "next/image";
import type { ReactNode } from "react";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import type { WikiPageDetail } from "@/app/lib/wiki-detail";
import { WikiStructuredSections } from "./wiki-structured-sections";

const EMPTY_ITEMS = new Map<string, ItemListEntry>();
const IGNORE_ITEM_SELECTION = () => undefined;

function CanonicalLink({ href }: { href: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-nova-accent/30 px-3 py-2 text-sm font-semibold text-nova-accent transition hover:bg-nova-accent/10 active:scale-[0.98]"
    >
      Mở trên Don&apos;t Starve Wiki
      <ArrowSquareOut aria-hidden="true" size={17} />
    </a>
  );
}

export function WikiArticle({
  detail,
  itemsById = EMPTY_ITEMS,
  onSelectItem = IGNORE_ITEM_SELECTION,
  fallbackSummary = null,
  contentAfterSummary = null,
}: {
  detail: WikiPageDetail;
  itemsById?: ReadonlyMap<string, ItemListEntry>;
  onSelectItem?: (item: ItemListEntry) => void;
  fallbackSummary?: ReactNode;
  contentAfterSummary?: ReactNode;
}) {
  const hasSummary = detail.summaryViHtml !== null;

  return (
    <>
      {hasSummary ? (
        <section className="overflow-hidden rounded-2xl border border-nova-border bg-nova-surface-soft">
          <div
            className="wiki-article p-4 sm:p-5"
            dangerouslySetInnerHTML={{ __html: detail.summaryViHtml ?? "" }}
          />
        </section>
      ) : (
        fallbackSummary
      )}

      {contentAfterSummary}

      <section className="overflow-hidden rounded-2xl border border-nova-border bg-nova-surface-soft">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-nova-border px-4 py-3">
          <h3 className="font-semibold text-nova-text">Bài viết Wiki</h3>
          <CanonicalLink href={detail.canonicalUrl} />
        </div>
        {detail.images.length ? (
          <section
            aria-label="Gallery"
            className="border-b border-nova-border bg-nova-surface-raised px-4 py-4 sm:px-5"
          >
            <h4 className="text-sm font-semibold text-nova-text">Gallery</h4>
            <div
              data-gallery-grid
              className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4"
            >
              {detail.images.slice(0, 12).map((image) => {
                const caption = image.title.replace(/^File:/i, "");
                return (
                  <figure
                    key={`${image.title}:${image.src}`}
                    tabIndex={0}
                    aria-label={caption}
                    className="group relative aspect-square overflow-hidden rounded-xl border border-nova-border bg-nova-surface-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent/40"
                  >
                    <Image
                      src={image.src}
                      alt={image.title}
                      width={image.width ?? 256}
                      height={image.height ?? 256}
                      unoptimized
                      className="h-full w-full object-contain p-3"
                    />
                    <figcaption className="absolute inset-x-0 bottom-0 line-clamp-3 bg-nova-text/90 px-3 py-2 text-xs leading-5 text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
                      {caption}
                    </figcaption>
                  </figure>
                );
              })}
            </div>
          </section>
        ) : null}
        {detail.normalized ? (
          <div className="border-b border-nova-border bg-nova-bg p-4 sm:p-5">
            <WikiStructuredSections
              sections={detail.normalized}
              itemsById={itemsById}
              onSelectItem={onSelectItem}
            />
          </div>
        ) : null}
        {!hasSummary ? (
          <div
            className="wiki-article p-4 sm:p-5"
            dangerouslySetInnerHTML={{ __html: detail.html }}
          />
        ) : null}
      </section>
    </>
  );
}
