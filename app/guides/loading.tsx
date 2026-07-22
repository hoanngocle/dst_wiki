import { SiteHeader } from "@/app/components/site-header";

export default function LoadingGuides() {
  return (
    <div className="min-h-[100dvh] bg-[#edf1f5]">
      <SiteHeader active="guides" />
      <main aria-busy="true" className="mx-auto max-w-7xl animate-pulse px-4 py-9 sm:px-6 lg:px-8">
        <div className="h-3 w-28 rounded bg-[#c7d2df]" />
        <div className="mt-5 h-12 max-w-2xl rounded bg-[#d7dfe8]" />
        <div className="mt-10 h-24 rounded-2xl border border-[#c7d2df] bg-[#f8fafc]" />
        <div className="mt-7 grid gap-5 md:grid-cols-2">{[0, 1, 2, 3].map((value) => <div key={value} className="h-64 rounded-2xl border border-[#c7d2df] bg-[#f8fafc]" />)}</div>
      </main>
    </div>
  );
}
