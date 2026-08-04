import type { Metadata } from "next";
import Link from "next/link";

import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { DstPanel } from "@/app/components/dst-panel";
import { SiteHeader } from "@/app/components/site-header";
import { StaticGameSprite } from "@/app/components/static-game-sprite";
import { buildCultivationStages, type CultivationStage } from "@/app/lib/cultivation-guide";
import { parseItemCatalog } from "@/app/lib/item-catalog";
import itemPayload from "@/public/data/items.json";

export const metadata: Metadata = {
  title: "Cảnh giới Tu Tiên | DST Wiki",
  description: "Lộ trình 15 lần thăng cấp Tu Tiên cùng đan dược và nguyên liệu tương ứng.",
};

const items = parseItemCatalog(itemPayload);
const stages = buildCultivationStages(items);

function StageRow({ stage }: { stage: CultivationStage }) {
  return (
    <div
      role="row"
      aria-label={`Cảnh giới ${stage.rank}: ${stage.currentRealm} → ${stage.resultingRealm}`}
      className={`grid gap-4 border-t border-nova-border p-4 lg:grid-cols-[4.5rem_11rem_15rem_11rem_minmax(0,1fr)] lg:items-center lg:gap-5 lg:px-5 ${stage.rank % 2 === 0 ? "bg-nova-surface-soft" : "bg-nova-surface"}`}
    >
      <div role="cell">
        <span className="grid size-11 place-items-center rounded-xl border border-nova-border bg-nova-surface-raised font-mono text-xs font-bold text-nova-accent lg:mx-auto">{String(stage.rank).padStart(2, "0")}</span>
      </div>
      <div role="cell" className="min-w-0">
        <p className="text-xs font-semibold tracking-[0.1em] text-nova-faint uppercase lg:hidden">Cảnh giới hiện tại</p>
        <h2 className="mt-1 text-base font-semibold tracking-[-0.02em] text-nova-text lg:mt-0">{stage.currentRealm}</h2>
      </div>
      <div role="cell" className="min-w-0">
        <p className="text-xs font-semibold tracking-[0.1em] text-nova-faint uppercase lg:hidden">Đan dược</p>
        <div className="mt-2 flex min-h-14 items-center gap-3 rounded-xl border border-nova-border bg-nova-surface-raised p-2 lg:mt-0">
          <StaticGameSprite sprite={stage.pill.sprite} size={40} />
          <span className="text-sm font-semibold text-nova-text">{stage.pill.name}</span>
        </div>
      </div>
      <div role="cell" className="min-w-0">
        <p className="text-xs font-semibold tracking-[0.1em] text-nova-faint uppercase lg:hidden">Cảnh giới đạt được</p>
        <div className="mt-1 flex flex-wrap items-center gap-2 lg:mt-0">
          <p className="text-base font-semibold tracking-[-0.02em] text-nova-text">{stage.resultingRealm}</p>
          {stage.breakthrough ? <span className="rounded-full border border-nova-accent/30 bg-nova-accent/10 px-2 py-0.5 text-[0.62rem] font-semibold tracking-[0.08em] text-nova-accent uppercase">Đột phá</span> : null}
        </div>
      </div>
      <div role="cell" className="min-w-0">
        <p className="text-xs font-semibold tracking-[0.1em] text-nova-faint uppercase lg:hidden">Vật phẩm yêu cầu</p>
        <div className="mt-2 flex flex-wrap gap-2 lg:mt-0">
          {stage.recipe ? stage.recipe.ingredients.map((ingredient) => (
            <span key={ingredient.id} className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-nova-border bg-nova-surface-raised py-1 pl-1 pr-3 text-sm font-semibold text-nova-text">
              <StaticGameSprite sprite={ingredient.sprite} size={32} />
              {ingredient.name} ×{ingredient.amount}
            </span>
          )) : <span className="text-sm text-nova-muted">Không có công thức</span>}
        </div>
      </div>
    </div>
  );
}

export default function CultivationGuidePage() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="guides" />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <Link href="/guides" className="inline-flex min-h-11 items-center rounded-lg text-sm font-semibold text-nova-accent underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent">
            ← Trở lại thư viện Guide
          </Link>
          <div className="mt-5">
            <DstHero
              testId="cultivation-hero"
              eyebrow="Tu Tiên · Thứ tự tu luyện"
              title="Cảnh giới Tu Tiên"
              description="Lộ trình 15 lần thăng cấp, từ cảnh giới hiện tại qua đan dược tương ứng đến cảnh giới đạt được."
              stats={[
                { label: "Bước thăng cấp", value: stages.length },
                { label: "Mốc đột phá", value: stages.filter((stage) => stage.breakthrough).length },
              ]}
              statsAriaLabel="Tổng quan lộ trình Tu Tiên"
            />
          </div>
          <p className="mt-8 text-sm leading-6 text-nova-muted">Công thức Đoán Thể Hoàn đã bổ sung Vòi Voi theo dữ liệu đã kiểm tra.</p>
          <DstPanel className="mt-3 overflow-hidden">
            <div role="table" aria-label="Thứ tự cảnh giới Tu Tiên" className="border border-nova-border bg-nova-surface">
              <div role="row" className="hidden bg-nova-surface-raised px-5 py-3 text-xs font-semibold tracking-[0.1em] text-nova-muted uppercase lg:grid lg:grid-cols-[4.5rem_11rem_15rem_11rem_minmax(0,1fr)] lg:gap-5">
                <span role="columnheader" className="text-center">STT</span>
                <span role="columnheader">Cảnh giới hiện tại</span>
                <span role="columnheader">Đan dược</span>
                <span role="columnheader">Cảnh giới đạt được</span>
                <span role="columnheader">Vật phẩm yêu cầu</span>
              </div>
              {stages.map((stage) => <StageRow key={stage.pillId} stage={stage} />)}
            </div>
          </DstPanel>
        </div>
      </DstPageShell>
    </div>
  );
}
