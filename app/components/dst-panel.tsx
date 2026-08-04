import type { ReactNode } from "react";

import { cn } from "@/app/lib/cn";

export interface DstPanelProps {
  children: ReactNode;
  className?: string;
  testId?: string;
}

const panelClassName =
  "rounded-2xl border border-nova-border bg-nova-surface shadow-[0_16px_44px_rgba(0,0,0,0.18)]";

export function DstPanel({ children, className, testId }: DstPanelProps) {
  return (
    <section data-testid={testId} className={cn(panelClassName, className)}>
      {children}
    </section>
  );
}
