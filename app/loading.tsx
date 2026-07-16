function ItemCardSkeleton() {
  return (
    <div
      data-testid="item-card-skeleton"
      aria-hidden="true"
      className="h-[220px] animate-pulse rounded-2xl border border-[#c8d3df] bg-[#f8fafc] p-5 motion-reduce:animate-none"
    >
      <div className="flex items-center gap-3">
        <div className="h-11 w-11 rounded-xl bg-[#dce6f4]" />
        <div className="h-16 w-16 rounded-xl bg-[#dce6f4]" />
        <div className="flex-1 space-y-2">
          <div className="h-4 w-2/3 rounded bg-[#d5dde6]" />
          <div className="h-3 w-1/2 rounded bg-[#e1e7ee]" />
        </div>
      </div>
      <div className="mt-5 h-3 w-full rounded bg-[#e1e7ee]" />
      <div className="mt-2 h-3 w-4/5 rounded bg-[#e1e7ee]" />
      <div className="mt-5 border-t border-[#d5dde6] pt-4">
        <div className="h-8 w-28 rounded-xl bg-[#dce6f4]" />
      </div>
    </div>
  );
}

export default function Loading() {
  return (
    <main className="min-h-[100dvh] bg-[#edf1f5] px-4 py-12 text-[#14233b] sm:px-6">
      <div className="mx-auto max-w-6xl">
        <p role="status" className="text-sm font-medium text-[#53647a]">
          Đang tải danh mục vật phẩm...
        </p>
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }, (_, index) => (
            <ItemCardSkeleton key={index} />
          ))}
        </div>
      </div>
    </main>
  );
}
