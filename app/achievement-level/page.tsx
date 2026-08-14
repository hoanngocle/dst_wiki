import type { Metadata } from "next";

import { AchievementLevelBrowser } from "@/app/components/achievement-level-browser";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { DstPanel } from "@/app/components/dst-panel";
import { SiteHeader } from "@/app/components/site-header";
import {
  getAchievementLevelCounts,
  parseAchievementLevelData,
  type LevelAttribute,
} from "@/app/lib/achievement-level";
import achievementLevelPayload from "@/data/manual/achievement-level.json";

export const metadata: Metadata = {
  title: "Achievement & Level | DST Wiki",
  description:
    "Toàn bộ nhiệm vụ, thành tựu, kỹ năng và hệ thống cấp độ của mod Achievement & Level.",
};

const data = parseAchievementLevelData(achievementLevelPayload);
const counts = getAchievementLevelCounts(data);

function LevelTable({
  label,
  attributes,
}: {
  label: string;
  attributes: readonly LevelAttribute[];
}) {
  return (
    <div className="overflow-x-auto rounded-xl border border-nova-border">
      <table aria-label={label} className="w-full min-w-[32rem] border-collapse text-left text-sm">
        <thead className="bg-nova-surface-raised text-nova-muted">
          <tr>
            <th scope="col" className="px-4 py-3 font-semibold">Thuộc tính</th>
            <th scope="col" className="px-4 py-3 font-semibold">Mức tăng</th>
            <th scope="col" className="px-4 py-3 font-semibold">Chu kỳ tăng giá</th>
          </tr>
        </thead>
        <tbody className="bg-nova-surface-soft text-nova-text">
          {attributes.map((attribute) => (
            <tr key={attribute.name} className="border-t border-nova-border">
              <th scope="row" className="px-4 py-3 font-semibold">{attribute.name}</th>
              <td className="px-4 py-3 text-nova-muted">{attribute.increase}</td>
              <td className="px-4 py-3 font-mono text-nova-muted">{attribute.multi}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function AchievementLevelPage() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="achievement-level" />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <DstHero
            testId="achievement-level-hero"
            eyebrow={`Workshop ${data.meta.workshopId} · Bản ${data.meta.version}`}
            title="Achievement & Level"
            description="Tra cứu toàn bộ nhiệm vụ, thành tựu, kỹ năng và quy tắc lên cấp được trích trực tiếp từ mod."
            stats={[
              { label: "Lượt nhiệm vụ", value: counts.tasks },
              { label: "Thành tựu", value: counts.achievements },
              { label: "Kỹ năng", value: counts.perks },
              { label: "Nhóm nhân vật", value: counts.characterTaskGroups },
            ]}
            statsAriaLabel="Tổng quan Achievement & Level"
          />

          <DstPanel className="mt-8 p-5 sm:p-6">
            <h2 className="text-2xl font-semibold tracking-[-0.03em] text-nova-text">
              Hệ thống Level
            </h2>
            <ul className="mt-4 grid gap-3 text-sm leading-6 text-nova-muted lg:grid-cols-3">
              {data.level.summary.map((line) => (
                <li key={line} className="rounded-xl bg-nova-surface-soft p-4">{line}</li>
              ))}
            </ul>
            <section className="mt-6" aria-labelledby="task-milestones-heading">
              <h3 id="task-milestones-heading" className="text-lg font-semibold text-nova-text">
                Sao và mốc thưởng
              </h3>
              <p className="mt-2 text-sm leading-6 text-nova-muted">{data.level.starCurrency}</p>
              <ol className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {data.level.taskMilestones.map((milestone) => (
                  <li key={milestone.completed} className="rounded-xl bg-nova-surface-soft p-4">
                    <span className="font-mono text-xs font-semibold text-nova-accent">
                      {milestone.completed} nhiệm vụ
                    </span>
                    <p className="mt-2 text-sm leading-6 text-nova-muted">{milestone.reward}</p>
                  </li>
                ))}
              </ol>
            </section>
            <div className="mt-6 grid gap-6 xl:grid-cols-2">
              <div className="min-w-0">
                <h3 className="mb-3 text-base font-semibold text-nova-text">Thuộc tính người chơi</h3>
                <LevelTable label="Thuộc tính người chơi" attributes={data.level.playerAttributes} />
              </div>
              <div className="min-w-0">
                <h3 className="mb-3 text-base font-semibold text-nova-text">Thuộc tính pet</h3>
                <LevelTable label="Thuộc tính pet" attributes={data.level.petAttributes} />
              </div>
            </div>
          </DstPanel>

          <AchievementLevelBrowser data={data} />
        </div>
      </DstPageShell>
    </div>
  );
}
