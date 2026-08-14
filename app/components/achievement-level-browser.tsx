"use client";

import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/app/components/ui/tabs";
import type { AchievementLevelData } from "@/app/lib/achievement-level";

export function AchievementLevelBrowser({ data }: { data: AchievementLevelData }) {
  const taskCount = data.taskGroups.reduce((total, group) => total + group.tasks.length, 0);

  return (
    <Tabs defaultValue="tasks" className="mt-8">
      <TabsList
        aria-label="Nội dung Achievement & Level"
        className="max-w-full gap-1 overflow-x-auto rounded-2xl border border-nova-border bg-nova-surface p-1"
      >
        <TabsTrigger value="tasks">Nhiệm vụ</TabsTrigger>
        <TabsTrigger value="achievements">Thành tựu</TabsTrigger>
        <TabsTrigger value="perks">Kỹ năng</TabsTrigger>
      </TabsList>
      <TabsContent value="tasks">
        <p>{taskCount} nhiệm vụ</p>
      </TabsContent>
      <TabsContent value="achievements">
        <p>{data.achievements.length} thành tựu</p>
      </TabsContent>
      <TabsContent value="perks">
        <p>{data.perks.length} kỹ năng</p>
      </TabsContent>
    </Tabs>
  );
}
