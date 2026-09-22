import Link from "next/link";

export function PhamNhanNav({ active }: { active: "catalog" | "progression" | "hotkey" }) {
  return (
    <nav aria-label="Danh mục Phàm Nhân" className="my-6 flex flex-wrap gap-2">
      {[
        { id: "catalog", href: "/pham-nhan-tu-tien", label: "Danh mục vật phẩm" },
        { id: "progression", href: "/pham-nhan-tu-tien/tien-trinh", label: "Tiến trình" },
        { id: "hotkey", href: "/hot-key", label: "Hotkey" },
      ].map((link) => (
        <Link key={link.id} href={link.href} aria-current={active === link.id ? "page" : undefined}
          className={`inline-flex min-h-11 items-center rounded-full border px-4 text-sm font-semibold ${active === link.id ? "border-nova-accent bg-nova-accent text-white" : "border-nova-border bg-nova-surface text-nova-muted hover:text-nova-text"}`}>
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
