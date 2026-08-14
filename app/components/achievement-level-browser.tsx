"use client";

import { useDeferredValue, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { dstControlClassName, DstField } from "@/app/components/dst-field";
import { DstPanel } from "@/app/components/dst-panel";
import { DstState } from "@/app/components/dst-state";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/app/components/ui/tabs";
import {
  filterAchievements,
  filterPerks,
  filterTasks,
  type AchievementLevelData,
  type AchievementRecord,
  type CharacterReward,
  type PerkRecord,
  type Season,
  type TaskResult,
  type TaskSlot,
} from "@/app/lib/achievement-level";

const tabClassName =
  "shrink-0 cursor-pointer rounded-xl px-4 py-2 text-sm font-semibold text-nova-muted transition-colors data-[state=active]:bg-nova-accent data-[state=active]:text-white hover:text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent focus-visible:ring-offset-2 focus-visible:ring-offset-nova-bg";

const resetButtonClassName =
  "inline-flex min-h-11 cursor-pointer items-center justify-center whitespace-nowrap rounded-xl border border-nova-border bg-nova-surface-raised px-4 text-sm font-semibold text-nova-text transition hover:border-nova-accent hover:text-nova-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent focus-visible:ring-offset-2 focus-visible:ring-offset-nova-surface active:scale-[0.98] motion-reduce:transform-none";

const cardClassName =
  "h-full rounded-2xl border border-nova-border bg-nova-surface-soft p-4 sm:p-5";

const seasonOptions: readonly { value: Season | "all"; label: string }[] = [
  { value: "all", label: "Tất cả mùa" },
  { value: "spring", label: "Mùa xuân" },
  { value: "winter", label: "Mùa đông" },
  { value: "summer", label: "Mùa hè" },
  { value: "autumn", label: "Mùa thu" },
  { value: "fallback", label: "Ngoài mùa" },
];

const slotOptions: readonly { value: TaskSlot | "all"; label: string }[] = [
  { value: "all", label: "Tất cả loại" },
  { value: "character", label: "Nhiệm vụ nhân vật" },
  { value: "seasonal", label: "Nhiệm vụ theo mùa" },
  { value: "repeat", label: "Nhiệm vụ lặp" },
];

function uniqueSorted(values: readonly string[]): readonly string[] {
  return [...new Set(values)].toSorted((left, right) => left.localeCompare(right, "vi"));
}

function Filters({ children }: { children: ReactNode }) {
  return (
    <DstPanel className="grid gap-4 p-4 md:grid-cols-2 xl:grid-cols-4">
      {children}
    </DstPanel>
  );
}

function SearchField({
  id,
  label,
  value,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <DstField label={label} htmlFor={id} className="md:col-span-2">
      <input
        id={id}
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Tên, mô tả hoặc ID..."
        className={dstControlClassName}
      />
    </DstField>
  );
}

function SelectField({
  id,
  label,
  value,
  onChange,
  children,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  children: ReactNode;
}) {
  return (
    <DstField label={label} htmlFor={id}>
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={dstControlClassName}
      >
        {children}
      </select>
    </DstField>
  );
}

function ResultHeading({ label }: { label: string }) {
  return (
    <div className="mt-6 flex items-center justify-between gap-4">
      <h2 className="text-lg font-semibold tracking-[-0.02em] text-nova-text">Kết quả</h2>
      <p role="status" aria-live="polite" className="text-sm font-medium text-nova-muted">
        {label}
      </p>
    </div>
  );
}

function MetaList({ children }: { children: ReactNode }) {
  return <dl className="mt-4 grid gap-2 text-xs sm:grid-cols-2">{children}</dl>;
}

function MetaItem({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="min-w-0 rounded-xl bg-nova-surface-raised px-3 py-2">
      <dt className="font-semibold text-nova-faint">{label}</dt>
      <dd className="mt-1 break-words text-nova-muted">{children}</dd>
    </div>
  );
}

function TaskCard({ task }: { task: TaskResult }) {
  return (
    <li
      data-testid="task-record"
      className="[content-visibility:auto] [contain-intrinsic-size:auto_13rem]"
    >
      <article className={cardClassName}>
        <h3 className="text-base font-semibold leading-6 text-nova-text">{task.name}</h3>
        <p className="mt-2 text-sm leading-6 text-nova-muted">{task.instructions}</p>
        <MetaList>
          <MetaItem label="Event"><code className="break-all">{task.event}</code></MetaItem>
          <MetaItem label="ID"><code className="break-all">{task.sourceId}</code></MetaItem>
          <MetaItem label="Số lần">{task.repeatCount}</MetaItem>
          {task.character ? <MetaItem label="Nhân vật">{task.character}</MetaItem> : null}
        </MetaList>
      </article>
    </li>
  );
}

function AchievementCard({ achievement }: { achievement: AchievementRecord }) {
  return (
    <li
      data-testid="achievement-record"
      className="[content-visibility:auto] [contain-intrinsic-size:auto_15rem]"
    >
      <article className={cardClassName}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <h3 className="text-base font-semibold leading-6 text-nova-text">{achievement.name}</h3>
          <span className="rounded-full border border-nova-accent/30 bg-nova-accent/10 px-2.5 py-1 font-mono text-xs font-semibold text-nova-accent">
            {achievement.stars} Sao
          </span>
        </div>
        <p className="mt-2 text-sm leading-6 text-nova-muted">{achievement.description}</p>
        <MetaList>
          <MetaItem label="Danh mục">{achievement.category}</MetaItem>
          <MetaItem label="Mục tiêu">{achievement.target}</MetaItem>
          <MetaItem label="Nhân vật">{achievement.characterRequirement}</MetaItem>
          <MetaItem label="ID"><code className="break-all">{achievement.id}</code></MetaItem>
        </MetaList>
      </article>
    </li>
  );
}

function PerkCard({ perk }: { perk: PerkRecord }) {
  return (
    <li
      data-testid="perk-record"
      className="[content-visibility:auto] [contain-intrinsic-size:auto_16rem]"
    >
      <article className={cardClassName}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <h3 className="text-base font-semibold leading-6 text-nova-text">{perk.name}</h3>
          <span className="rounded-full border border-nova-accent/30 bg-nova-accent/10 px-2.5 py-1 font-mono text-xs font-semibold text-nova-accent">
            {perk.cost} Sao
          </span>
        </div>
        <p className="mt-2 text-sm leading-6 text-nova-muted">{perk.description}</p>
        <MetaList>
          <MetaItem label="Danh mục">{perk.category}</MetaItem>
          <MetaItem label="Phạm vi">{perk.scope}</MetaItem>
          <MetaItem label="ID"><code className="break-all">{perk.id}</code></MetaItem>
          {perk.notes ? <MetaItem label="Ghi chú">{perk.notes}</MetaItem> : null}
        </MetaList>
      </article>
    </li>
  );
}

function RewardSection({ heading, rewards }: { heading: string; rewards: readonly CharacterReward[] }) {
  return (
    <section className="mt-8" aria-labelledby={`${heading.replaceAll(" ", "-")}-heading`}>
      <h2
        id={`${heading.replaceAll(" ", "-")}-heading`}
        className="text-xl font-semibold tracking-[-0.025em] text-nova-text"
      >
        {heading}
      </h2>
      <ul className="mt-4 grid gap-3 md:grid-cols-2">
        {rewards.map((reward) => (
          <li key={reward.character} className={cardClassName}>
            <h3 className="font-semibold text-nova-text">{reward.character}</h3>
            <p className="mt-2 text-sm leading-6 text-nova-muted">{reward.effect}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}

function ResetButton({ label, onClick }: { label: string; onClick: () => void }) {
  return <button type="button" onClick={onClick} className={resetButtonClassName}>{label}</button>;
}

export function AchievementLevelBrowser({ data }: { data: AchievementLevelData }) {
  const [taskQuery, setTaskQuery] = useState("");
  const [taskSlot, setTaskSlot] = useState<TaskSlot | "all">("all");
  const [taskSeason, setTaskSeason] = useState<Season | "all">("all");
  const [taskCharacter, setTaskCharacter] = useState("all");
  const [achievementQuery, setAchievementQuery] = useState("");
  const [achievementCategory, setAchievementCategory] = useState("all");
  const [perkQuery, setPerkQuery] = useState("");
  const [perkCategory, setPerkCategory] = useState("all");
  const [perkCharacter, setPerkCharacter] = useState("all");

  const deferredTaskQuery = useDeferredValue(taskQuery);
  const deferredAchievementQuery = useDeferredValue(achievementQuery);
  const deferredPerkQuery = useDeferredValue(perkQuery);

  const taskCharacters = useMemo(
    () => uniqueSorted(data.taskGroups.flatMap((group) => group.character ? [group.character] : [])),
    [data.taskGroups],
  );
  const achievementCategories = useMemo(
    () => uniqueSorted(data.achievements.map((achievement) => achievement.category)),
    [data.achievements],
  );
  const perkCategories = useMemo(
    () => uniqueSorted(data.perks.map((perk) => perk.category)),
    [data.perks],
  );
  const perkCharacters = useMemo(
    () => taskCharacters.filter((character) => data.perks.some((perk) => perk.scope.includes(character))),
    [data.perks, taskCharacters],
  );

  const taskResults = useMemo(
    () => filterTasks(data, {
      query: deferredTaskQuery,
      slot: taskSlot,
      season: taskSeason,
      character: taskCharacter,
    }),
    [data, deferredTaskQuery, taskCharacter, taskSeason, taskSlot],
  );
  const groupedTaskResults = useMemo(() => {
    const groups = new Map<string, { label: string; tasks: TaskResult[] }>();
    for (const task of taskResults) {
      const group = groups.get(task.groupId);
      if (group) group.tasks.push(task);
      else groups.set(task.groupId, { label: task.groupLabel, tasks: [task] });
    }
    return [...groups.entries()];
  }, [taskResults]);
  const achievementResults = useMemo(
    () => filterAchievements(data, {
      query: deferredAchievementQuery,
      category: achievementCategory,
    }),
    [achievementCategory, data, deferredAchievementQuery],
  );
  const perkResults = useMemo(
    () => filterPerks(data, {
      query: deferredPerkQuery,
      category: perkCategory,
      character: perkCharacter,
    }),
    [data, deferredPerkQuery, perkCategory, perkCharacter],
  );

  function resetTaskFilters() {
    setTaskQuery("");
    setTaskSlot("all");
    setTaskSeason("all");
    setTaskCharacter("all");
  }

  function resetAchievementFilters() {
    setAchievementQuery("");
    setAchievementCategory("all");
  }

  function resetPerkFilters() {
    setPerkQuery("");
    setPerkCategory("all");
    setPerkCharacter("all");
  }

  return (
    <Tabs defaultValue="tasks" className="mt-8">
      <TabsList
        aria-label="Nội dung Achievement & Level"
        className="max-w-full gap-1 overflow-x-auto rounded-2xl border border-nova-border bg-nova-surface p-1"
      >
        <TabsTrigger value="tasks" className={tabClassName}>Nhiệm vụ</TabsTrigger>
        <TabsTrigger value="achievements" className={tabClassName}>Thành tựu</TabsTrigger>
        <TabsTrigger value="perks" className={tabClassName}>Kỹ năng</TabsTrigger>
      </TabsList>

      <TabsContent value="tasks" className="mt-5">
        <Filters>
          <SearchField id="task-search" label="Tìm nhiệm vụ" value={taskQuery} onChange={setTaskQuery} />
          <SelectField id="task-slot" label="Loại nhiệm vụ" value={taskSlot} onChange={(value) => setTaskSlot(value as TaskSlot | "all")}>
            {slotOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </SelectField>
          <SelectField id="task-season" label="Mùa" value={taskSeason} onChange={(value) => setTaskSeason(value as Season | "all")}>
            {seasonOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </SelectField>
          <SelectField id="task-character" label="Nhân vật yêu cầu" value={taskCharacter} onChange={setTaskCharacter}>
            <option value="all">Tất cả nhân vật</option>
            {taskCharacters.map((character) => <option key={character} value={character}>{character}</option>)}
          </SelectField>
          <div className="flex items-end">
            {taskResults.length ? <ResetButton label="Xóa bộ lọc nhiệm vụ" onClick={resetTaskFilters} /> : null}
          </div>
        </Filters>
        <ResultHeading label={`${taskResults.length} nhiệm vụ`} />
        {taskResults.length ? (
          <div className="mt-4 grid gap-7">
            {groupedTaskResults.map(([groupId, group]) => (
              <section key={groupId} aria-labelledby={`${groupId}-heading`}>
                <div className="flex flex-wrap items-baseline justify-between gap-3">
                  <h2 id={`${groupId}-heading`} className="text-xl font-semibold tracking-[-0.025em] text-nova-text">{group.label}</h2>
                  <p className="font-mono text-xs text-nova-muted">{group.tasks.length} mục</p>
                </div>
                <ul className="mt-3 grid gap-3 md:grid-cols-2">
                  {group.tasks.map((task) => <TaskCard key={task.key} task={task} />)}
                </ul>
              </section>
            ))}
          </div>
        ) : (
          <div className="mt-4">
            <DstState
              tone="empty"
              title="Không có nhiệm vụ phù hợp"
              description="Hãy đổi từ khóa hoặc bộ lọc để xem lại danh sách."
              actions={<ResetButton label="Xóa bộ lọc nhiệm vụ" onClick={resetTaskFilters} />}
            />
          </div>
        )}
      </TabsContent>

      <TabsContent value="achievements" className="mt-5">
        <Filters>
          <SearchField id="achievement-search" label="Tìm thành tựu" value={achievementQuery} onChange={setAchievementQuery} />
          <SelectField id="achievement-category" label="Danh mục thành tựu" value={achievementCategory} onChange={setAchievementCategory}>
            <option value="all">Tất cả danh mục</option>
            {achievementCategories.map((category) => <option key={category} value={category}>{category}</option>)}
          </SelectField>
          <div className="flex items-end">
            {achievementResults.length ? <ResetButton label="Xóa bộ lọc thành tựu" onClick={resetAchievementFilters} /> : null}
          </div>
        </Filters>
        <ResultHeading label={`${achievementResults.length} thành tựu`} />
        {achievementResults.length ? (
          <ul aria-label="Danh sách thành tựu" className="mt-4 grid gap-3 md:grid-cols-2">
            {achievementResults.map((achievement) => <AchievementCard key={achievement.id} achievement={achievement} />)}
          </ul>
        ) : (
          <div className="mt-4">
            <DstState
              tone="empty"
              title="Không có thành tựu phù hợp"
              description="Hãy đổi từ khóa hoặc danh mục để xem lại danh sách."
              actions={<ResetButton label="Xóa bộ lọc thành tựu" onClick={resetAchievementFilters} />}
            />
          </div>
        )}
      </TabsContent>

      <TabsContent value="perks" className="mt-5">
        <Filters>
          <SearchField id="perk-search" label="Tìm kỹ năng" value={perkQuery} onChange={setPerkQuery} />
          <SelectField id="perk-category" label="Danh mục kỹ năng" value={perkCategory} onChange={setPerkCategory}>
            <option value="all">Tất cả danh mục</option>
            {perkCategories.map((category) => <option key={category} value={category}>{category}</option>)}
          </SelectField>
          <SelectField id="perk-character" label="Nhân vật của kỹ năng" value={perkCharacter} onChange={setPerkCharacter}>
            <option value="all">Tất cả nhân vật</option>
            {perkCharacters.map((character) => <option key={character} value={character}>{character}</option>)}
          </SelectField>
          <div className="flex items-end">
            {perkResults.length ? <ResetButton label="Xóa bộ lọc kỹ năng" onClick={resetPerkFilters} /> : null}
          </div>
        </Filters>
        <ResultHeading label={`${perkResults.length} kỹ năng`} />
        {perkResults.length ? (
          <ul aria-label="Danh sách kỹ năng" className="mt-4 grid gap-3 md:grid-cols-2">
            {perkResults.map((perk) => <PerkCard key={perk.id} perk={perk} />)}
          </ul>
        ) : (
          <div className="mt-4">
            <DstState
              tone="empty"
              title="Không có kỹ năng phù hợp"
              description="Hãy đổi từ khóa, danh mục hoặc nhân vật để xem lại danh sách."
              actions={<ResetButton label="Xóa bộ lọc kỹ năng" onClick={resetPerkFilters} />}
            />
          </div>
        )}
        <RewardSection heading="Thưởng khi hoàn thành 2 nhiệm vụ" rewards={data.rewards.task2} />
        <RewardSection heading="Thưởng khi hoàn thành 4 nhiệm vụ" rewards={data.rewards.task4} />
      </TabsContent>
    </Tabs>
  );
}
