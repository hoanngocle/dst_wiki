"use client";

import Link from "next/link";
import { useId, useState } from "react";
import { cn } from "@/app/lib/cn";
import { tuTienTabs } from "@/app/lib/tu-tien-tabs";

type SiteSection = "items" | "tu-tien" | "solo-leveling" | "linh-gioi" | "bosses";
const links = [
  { id: "items", href: "/", label: "Vật phẩm" },
  { id: "tu-tien", href: "/tu-tien", label: "Tu Tiên" },
  { id: "solo-leveling", href: "/solo-leveling", label: "Solo Leveling" },
  { id: "linh-gioi", href: "/linh-gioi", label: "Linh Giới" },
  { id: "bosses", href: "/bosses", label: "Lộ trình boss" },
] as const;

export function SiteHeader({ active }: { active?: SiteSection }) {
  const [open, setOpen] = useState(false);
  const submenuId = useId();
  const linkStyle = (selected: boolean) => cn(
    "inline-flex min-h-11 items-center rounded-full px-4 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent focus-visible:ring-offset-2 focus-visible:ring-offset-nova-bg",
    selected ? "bg-nova-accent text-white" : "text-nova-muted hover:bg-nova-surface-soft hover:text-nova-text",
  );
  return <header className="relative z-30 border-b border-nova-border bg-nova-surface-raised/95 text-nova-text backdrop-blur">
    <div className="mx-auto flex min-h-16 max-w-7xl flex-wrap items-center justify-between gap-x-4 px-4 py-2 sm:px-6 lg:px-8">
      <Link href="/" className="flex min-h-11 items-center gap-3 font-semibold tracking-[-0.02em] text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent">
        <span aria-hidden="true" className="h-3 w-3 rotate-45 bg-nova-accent" />
        <span>Don&apos;t Starve Together</span>
      </Link>
      <nav aria-label="Điều hướng chính" className="-mx-2 flex max-w-full flex-wrap items-center gap-1 px-2 py-1">
        {links.map(link => link.id === "tu-tien" ? <div key={link.id} className="relative flex items-center" onPointerEnter={event => { if (event.pointerType === "mouse") setOpen(true); }} onPointerLeave={event => { if (event.pointerType === "mouse") setOpen(false); }} onFocus={event => { if ((event.target as HTMLElement).tagName === "A") setOpen(true); }} onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setOpen(false); }} onKeyDown={event => { if (event.key === "Escape") { setOpen(false); event.currentTarget.querySelector("button")?.focus(); } }}>
          <Link href={link.href} aria-current={active === link.id ? "page" : undefined} className={linkStyle(active === link.id)}>{link.label}</Link>
          <button type="button" aria-label={`${open ? "Đóng" : "Mở"} các mục Tu Tiên`} aria-expanded={open} aria-controls={submenuId} onClick={() => setOpen(value => !value)} className="grid min-h-11 min-w-9 place-items-center rounded-full text-nova-muted hover:bg-nova-surface-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent"><span aria-hidden="true">▾</span></button>
          <div id={submenuId} hidden={!open} className="absolute left-0 top-full w-60 pt-2">
            <div className="rounded-2xl border border-nova-border bg-nova-surface p-2 shadow-xl">
              {tuTienTabs.map(tab => <Link key={tab.id} href={`/tu-tien#${tab.id}`} onClick={event => { setOpen(false); if (window.location.pathname === "/tu-tien" && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) { event.preventDefault(); window.history.pushState(null, "", `/tu-tien#${tab.id}`); window.dispatchEvent(new Event("tu-tien-tab")); } }} className="block min-h-10 rounded-lg px-3 py-2 text-sm font-medium text-nova-muted hover:bg-nova-surface-soft hover:text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent">{tab.label}</Link>)}
            </div>
          </div>
        </div> : <Link key={link.id} href={link.href} aria-current={active === link.id ? "page" : undefined} className={linkStyle(active === link.id)}>{link.label}</Link>)}
      </nav>
    </div>
  </header>;
}
