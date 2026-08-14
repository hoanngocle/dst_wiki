import Link from "next/link";

import { cn } from "@/app/lib/cn";

type SiteSection = "items" | "characters" | "tu-tien" | "achievement-level";

const links = [
  { id: "items", href: "/", label: "Vật phẩm" },
  { id: "characters", href: "/characters", label: "Nhân vật" },
  { id: "tu-tien", href: "/tu-tien", label: "Cảnh giới Tu Tiên" },
  { id: "achievement-level", href: "/achievement-level", label: "Achievement & Level" },
] as const;

export function SiteHeader({ active }: { active?: SiteSection }) {
  return (
    <header className="border-b border-nova-border bg-nova-surface-raised/95 text-nova-text backdrop-blur">
      <div className="mx-auto flex min-h-16 max-w-7xl flex-wrap items-center justify-between gap-x-4 px-4 py-2 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="flex min-h-11 items-center gap-3 font-semibold tracking-[-0.02em] text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent focus-visible:ring-offset-2 focus-visible:ring-offset-nova-bg"
        >
          <span aria-hidden="true" className="h-3 w-3 rotate-45 bg-nova-accent" />
          <span>Don&apos;t Starve Together</span>
        </Link>
        <nav
          aria-label="Điều hướng chính"
          className="-mx-2 flex max-w-full items-center gap-1 overflow-x-auto px-2 py-1"
        >
          {links.map((link) => {
            const selected = active === link.id;

            return (
              <Link
                key={link.id}
                href={link.href}
                aria-current={selected ? "page" : undefined}
                className={cn(
                  "inline-flex min-h-11 items-center rounded-full px-4 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent focus-visible:ring-offset-2 focus-visible:ring-offset-nova-bg",
                  selected
                    ? "bg-nova-accent text-white"
                    : "text-nova-muted hover:bg-nova-surface-soft hover:text-nova-text",
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
