import type { ItemListEntry } from "@/app/lib/item-catalog";

export function ItemUsageFacts({ item, includeUsage = true }: { item: ItemListEntry; includeUsage?: boolean }) {
  const fact = item.summary?.usage;
  const text = fact?.status === "known" ? fact.text : fact?.status === "not_applicable" ? "Không áp dụng." : "Chưa có dữ liệu.";
  return (
    <>
      <CharacterRequirement item={item} mode="usage" />
      {includeUsage ? <ul className="list-disc space-y-2 py-4 pl-9 pr-4 text-sm leading-6 text-nova-muted">
        <li>{text}</li>
      </ul> : null}
    </>
  );
}

export function CharacterRequirement({ item, mode }: { item: ItemListEntry; mode: "crafting" | "usage" }) {
  const requirement = item.characterRequirements?.[mode];
  if (requirement?.status !== "known") return null;
  return <p className="px-4 py-3 text-sm leading-6 text-nova-muted"><strong className="font-semibold text-nova-text">Nhân vật yêu cầu ({mode === "crafting" ? "chế tạo" : "sử dụng"}):</strong> {requirement.text}</p>;
}

export function ItemUsage({ item, titleId }: { item: ItemListEntry; titleId: string }) {
  return (
    <section aria-labelledby={`${titleId}-usage`} className="overflow-hidden rounded-2xl border border-nova-border bg-nova-surface-soft">
      <h3 id={`${titleId}-usage`} className="border-b border-nova-border px-4 py-3 text-sm font-semibold text-nova-text">Cách Sử dụng</h3>
      <ItemUsageFacts item={item} />
    </section>
  );
}
