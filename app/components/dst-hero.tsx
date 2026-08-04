import type { ReactNode } from "react";

export interface DstStat {
  label: string;
  value: ReactNode;
}

export interface DstHeroProps {
  eyebrow: string;
  title: string;
  description: string;
  stats?: readonly DstStat[];
  children?: ReactNode;
  testId?: string;
}

export function DstHero({
  eyebrow,
  title,
  description,
  stats,
  children,
  testId,
}: DstHeroProps) {
  const hasStats = stats ? stats.length > 0 : false;
  const layoutTestId = testId ? `${testId}-layout` : undefined;
  const statsTestId = testId ? `${testId}-stats` : undefined;

  return (
    <section
      data-testid={testId}
      className="rounded-2xl border border-nova-border bg-nova-surface p-6 sm:p-8"
    >
      <div
        data-testid={layoutTestId}
        className={
          hasStats
            ? "grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(18rem,auto)] lg:items-start lg:gap-8"
            : undefined
        }
      >
        <div className="min-w-0">
          <p className="text-xs font-semibold tracking-[0.16em] text-nova-muted uppercase">
            {eyebrow}
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.04em] text-nova-text sm:text-5xl">
            {title}
          </h1>
          <p className="mt-4 max-w-[62ch] text-base leading-7 text-nova-muted">
            {description}
          </p>
        </div>

        {hasStats ? (
          <dl
            data-testid={statsTestId}
            className="grid gap-3 sm:grid-cols-2 lg:max-w-[34rem] lg:min-w-80 lg:justify-self-end"
          >
            {stats?.map((stat) => (
              <div key={stat.label} className="rounded-xl bg-nova-surface-soft p-4">
                <dt className="text-sm text-nova-muted">{stat.label}</dt>
                <dd className="mt-1 text-2xl font-semibold text-nova-text">{stat.value}</dd>
              </div>
            ))}
          </dl>
        ) : null}
      </div>
      {children ? <div className="mt-6">{children}</div> : null}
    </section>
  );
}
