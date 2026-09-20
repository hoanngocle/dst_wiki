import Link from "next/link";

export function PhamNhanNav({ active }: { active: "catalog" | "guides" | "config" }) {
  return (
    <nav aria-label="Danh mục Phàm Nhân" className="my-6 flex flex-wrap gap-2">
      {[
        { id: "catalog", href: "/pham-nhan-tu-tien", label: "Danh mục vật phẩm" },
        { id: "guides", href: "/pham-nhan-tu-tien/huong-dan", label: "Hướng dẫn" },
        { id: "config", href: "/pham-nhan-tu-tien/config", label: "Config" },
      ].map((link) => (
        <Link key={link.id} href={link.href} aria-current={active === link.id ? "page" : undefined}
          className={`inline-flex min-h-11 items-center rounded-full border px-4 text-sm font-semibold ${active === link.id ? "border-nova-accent bg-nova-accent text-white" : "border-nova-border bg-nova-surface text-nova-muted hover:text-nova-text"}`}>
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
