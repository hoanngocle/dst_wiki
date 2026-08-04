import type { ReactNode } from "react";

export interface DstFieldProps {
  label: string;
  htmlFor: string;
  children: ReactNode;
  className?: string;
}

export const dstControlClassName =
  "min-h-11 w-full rounded-xl border border-nova-border bg-nova-surface-soft px-3 text-sm text-nova-text outline-none placeholder:text-nova-faint focus-visible:border-nova-accent focus-visible:ring-2 focus-visible:ring-nova-accent/30";

export function DstField({ label, htmlFor, children, className }: DstFieldProps) {
  return (
    <div className={className}>
      <label htmlFor={htmlFor} className="mb-2 block text-sm font-medium text-nova-muted">
        {label}
      </label>
      {children}
    </div>
  );
}
