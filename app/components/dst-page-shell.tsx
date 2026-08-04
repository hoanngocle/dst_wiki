import type { ReactNode } from "react";

export interface DstPageShellProps {
  children: ReactNode;
}

export function DstPageShell({ children }: DstPageShellProps) {
  return (
    <main data-testid="dst-page-shell" className="w-full text-nova-text">
      <div className="mx-auto w-full max-w-7xl pb-10">{children}</div>
    </main>
  );
}
