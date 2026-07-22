import { SiteHeader } from "@/app/components/site-header";

export default function LoadingGuide() {
  return (
    <div className="min-h-[100dvh] bg-[#edf1f5]">
      <SiteHeader active="guides" />
      <main aria-busy="true" className="mx-auto max-w-7xl animate-pulse px-4 py-10 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-2">
          <div><div className="h-3 w-24 rounded bg-[#c7d2df]" /><div className="mt-6 h-14 rounded bg-[#d7dfe8]" /><div className="mt-5 h-24 rounded bg-[#d7dfe8]" /></div>
          <div className="aspect-[16/9] rounded-2xl bg-[#d7dfe8]" />
        </div>
        <div className="mx-auto mt-12 h-[40rem] max-w-4xl rounded-2xl bg-[#f8fafc]" />
      </main>
    </div>
  );
}
