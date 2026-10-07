import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { bossGuides, findBossGuide } from "../guides";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return bossGuides.map(({ slug }) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const guide = findBossGuide((await params).slug);
  if (!guide) return { title: "Không tìm thấy guide | DST Wiki" };
  return { title: `${guide.title}: hướng dẫn chi tiết | DST Wiki`, description: guide.description };
}

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return <section id={id} aria-labelledby={`${id}-title`} className="scroll-mt-6 rounded-2xl border border-nova-border bg-nova-surface p-5 sm:p-8">
    <h2 id={`${id}-title`} className="text-2xl font-semibold tracking-tight text-nova-text">{title}</h2>
    <div className="mt-5 space-y-4 text-sm leading-7 text-nova-muted">{children}</div>
  </section>;
}

function Source({ page, label }: { page: string; label?: string }) {
  return <a href={`https://dontstarve.wiki.gg/wiki/${page}`} target="_blank" rel="noreferrer" className="font-medium text-nova-accent underline decoration-nova-accent/40 underline-offset-4 focus-visible:outline-2 focus-visible:outline-nova-accent">{label ?? page.replaceAll("_", " ")} ↗</a>;
}

export default async function BossGuidePage({ params }: Props) {
  const guide = findBossGuide((await params).slug);
  if (!guide) notFound();
  const chapters = [{ id: "chuan-bi", title: "Chuẩn bị trước khi đi" }, ...guide.sections, { id: "phan-thuong", title: "Phần thưởng & công dụng" }, { id: "go-roi", title: "Gỡ rối khi bị kẹt" }, { id: "tiep-theo", title: "Đi tuyến nào tiếp?" }];
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
    <SiteHeader active="bosses" />
    <DstPageShell>
      <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
        <Link href="/bosses" className="mb-5 inline-flex min-h-11 items-center text-sm font-semibold text-nova-accent underline underline-offset-4">← Tất cả tuyến boss & lộ trình đi hết</Link>
        <DstHero eyebrow="Cẩm nang boss • Don't Starve Together" title={guide.title} description={guide.description} stats={[{ label: "Khu vực", value: guide.location }, { label: "Mức chuẩn bị", value: guide.difficulty }]} statsAriaLabel="Thông tin tuyến boss">
          <p className="text-sm leading-6 text-nova-muted">Cơ chế DST gốc • Đối chiếu ngày <time dateTime="2026-10-07">07/10/2026</time>. Server Tu Tiên có thể thay đổi chỉ số và thiết lập. Các cách đánh bên dưới là gợi ý thực hành, không yêu cầu một nhân vật cụ thể.</p>
        </DstHero>
        <p className="mt-6 rounded-xl border border-nova-accent/20 bg-nova-accent/5 p-5 text-sm leading-7 text-nova-text">{guide.summary}</p>
        <div className="mt-8 grid items-start gap-6 lg:grid-cols-[15rem_minmax(0,1fr)]">
          <aside className="rounded-2xl border border-nova-border bg-nova-surface p-4 lg:sticky lg:top-6">
            <p className="px-3 text-xs font-semibold uppercase tracking-wider text-nova-faint">Trong guide này</p>
            <nav aria-label={`Mục lục ${guide.title}`} className="mt-3 grid gap-1 sm:grid-cols-2 lg:grid-cols-1">
              {chapters.map((section, index) => <a key={section.id} href={`#${section.id}`} className="flex min-h-11 items-center gap-3 rounded-lg px-3 py-2 text-sm text-nova-muted hover:bg-nova-surface-soft hover:text-nova-text focus-visible:outline-2 focus-visible:outline-nova-accent"><span className="text-xs text-nova-faint">{String(index + 1).padStart(2, "0")}</span>{section.title}</a>)}
            </nav>
          </aside>
          <article aria-label={`Hướng dẫn ${guide.title}`} className="min-w-0 space-y-6">
            <Section id="chuan-bi" title="Chuẩn bị trước khi đi">
              <ul className="list-disc space-y-3 pl-5">{guide.preparations.map(text => <li key={text}>{text}</li>)}</ul>
              <Link href="/bosses#hanh-trang" className="inline-block font-semibold text-nova-accent underline underline-offset-4">Chưa biết lấy vũ khí, giáp và đồ hồi máu? Xem hành trang chung →</Link>
            </Section>
            {guide.sections.map(section => <Section key={section.id} id={section.id} title={section.title}>
              {section.paragraphs?.map(text => <p key={text}>{text}</p>)}
              {section.steps && <ol className="list-decimal space-y-3 pl-5 marker:font-semibold marker:text-nova-accent">{section.steps.map(text => <li key={text}>{text}</li>)}</ol>}
              {section.tips && <div className="rounded-xl bg-nova-surface-soft p-4"><p className="mb-2 font-semibold text-nova-text">Ghi nhớ khi thực hành</p><ul className="list-disc space-y-2 pl-5">{section.tips.map(text => <li key={text}>{text}</li>)}</ul></div>}
              <div className="flex flex-wrap gap-x-4 gap-y-1 border-t border-nova-border pt-3 text-xs"><span>Nguồn cơ chế:</span>{section.sources.map(source => <Source key={source.page} {...source} />)}</div>
            </Section>)}
            <Section id="phan-thuong" title="Phần thưởng & công dụng">
              <div className="grid gap-3 sm:grid-cols-2">{guide.rewards.map(item => <div key={item.name} className="rounded-xl border border-nova-border p-4"><h3 className="font-semibold text-nova-text">{item.name}</h3><p className="my-2">{item.use}</p><Source page={item.page} label="Xem vật phẩm" /></div>)}</div>
            </Section>
            <Section id="go-roi" title="Gỡ rối khi bị kẹt">
              <dl className="space-y-5">{guide.mistakes.map(item => <div key={item.question}><dt className="font-semibold text-nova-text">{item.question}</dt><dd className="mt-1">{item.answer}</dd></div>)}</dl>
            </Section>
            <Section id="tiep-theo" title="Đi tuyến nào tiếp?">
              <p>Đây là gợi ý để tận dụng đồ vừa kiếm được. Các nhánh độc lập có thể đổi thứ tự theo mùa và trang bị của nhóm.</p>
              <div className="grid gap-3 sm:grid-cols-2">{guide.next.map(link => <Link key={link.href} href={link.href} className="rounded-xl bg-nova-surface-soft px-4 py-3 font-semibold text-nova-accent underline underline-offset-4">{link.label} →</Link>)}</div>
              <Link href="/bosses#lo-trinh" className="inline-block font-semibold text-nova-accent underline underline-offset-4">Quay về lộ trình tổng →</Link>
            </Section>
          </article>
        </div>
      </div>
    </DstPageShell>
  </div>;
}
