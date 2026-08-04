import type { ReactNode } from "react";

export type DstStateTone = "loading" | "empty" | "danger";

export interface DstStateProps {
  tone: DstStateTone;
  title: string;
  description?: string;
  actions?: ReactNode;
}

const toneClassNames: Record<DstStateTone, string> = {
  loading: "border-nova-border bg-nova-surface text-nova-text",
  empty: "border-nova-border bg-nova-surface text-nova-text",
  danger: "border-nova-danger/40 bg-nova-danger/10 text-nova-text",
};

export function DstState({ tone, title, description, actions }: DstStateProps) {
  return (
    <section
      role={tone === "danger" ? "alert" : "status"}
      className={`rounded-2xl border p-6 ${toneClassNames[tone]}`}
    >
      <h2 className="text-lg font-semibold">{title}</h2>
      {description ? <p className="mt-2 text-sm leading-6 text-nova-muted">{description}</p> : null}
      {actions ? <div className="mt-4">{actions}</div> : null}
    </section>
  );
}
