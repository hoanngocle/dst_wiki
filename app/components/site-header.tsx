import Link from "next/link";

const links = [
  { id: "items", href: "/", label: "Prefabs" },
  { id: "characters", href: "/characters", label: "Nhân vật" },
  { id: "base", href: "/base", label: "Base" },
  { id: "guides", href: "/guides", label: "Guide" },
] as const;

export function SiteHeader({ active }: { active: (typeof links)[number]["id"] }) {
  return (
    <header className="border-b border-[#cbd5e1] bg-[#f8fafc]/90">
      <div className="mx-auto flex min-h-16 max-w-7xl flex-wrap items-center justify-between gap-x-4 px-4 py-2 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="flex min-h-11 items-center gap-3 font-semibold tracking-[-0.02em] text-[#14233b]"
        >
          <span
            aria-hidden="true"
            className="h-4 w-4 rotate-45 border-2 border-[#2e5fb3]"
          />
          <span>Don&apos;t Starve Together</span>
        </Link>
        <nav
          aria-label="Điều hướng chính"
          className="-mx-2 flex max-w-full items-center gap-1 overflow-x-auto px-2"
        >
          {links.map((link) => {
            const selected = active === link.id;

            return (
              <Link
                key={link.id}
                href={link.href}
                aria-current={selected ? "page" : undefined}
                className={
                  selected
                    ? "inline-flex min-h-11 items-center rounded-full bg-[#2e5fb3] px-4 text-sm font-semibold text-[#f8fafc]"
                    : "inline-flex min-h-11 items-center rounded-full px-4 text-sm font-semibold text-[#53647a] hover:bg-[#e9eff6] hover:text-[#2e5fb3]"
                }
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
