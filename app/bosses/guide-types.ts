export type GuideSection = {
  id: string;
  title: string;
  paragraphs?: string[];
  steps?: string[];
  tips?: string[];
  sources: { page: string; label?: string }[];
};

export type BossGuide = {
  slug: string;
  title: string;
  description: string;
  difficulty: string;
  location: string;
  summary: string;
  preparations: string[];
  sections: GuideSection[];
  rewards: { name: string; use: string; page: string }[];
  mistakes: { question: string; answer: string }[];
  next: { label: string; href: string }[];
};
