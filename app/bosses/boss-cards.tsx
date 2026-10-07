import Image from "next/image";
import Link from "next/link";

const cards = [
  { name: "Lunar Rift", boss: "Celestial Champion", href: "/lunar-rift", image: "Celestial_Champion_Phase_3" },
  { name: "Ancient & Shadow", boss: "Ancient Fuelweaver", href: "/ancient", image: "Ancient_Fuelweaver" },
  { name: "Bee Queen", boss: "Ong Chúa", href: "/bosses/bee-queen", image: "Bee_Queen" },
  { name: "Dragonfly", boss: "Sa mạc dung nham", href: "/bosses/dragonfly", image: "Dragonfly" },
  { name: "Klaus", boss: "Loot Stash mùa đông", href: "/bosses/klaus", image: "Klaus" },
  { name: "Eye & Twins of Terror", boss: "Tuyến Terraria", href: "/bosses/terraria", image: "Eye_of_Terror_Phase_1" },
  { name: "Toadstool & Misery", boss: "Cóc Nấm trong hang", href: "/bosses/toadstool", image: "Toadstool" },
  { name: "Nightmare & Scrappy", boss: "Tuyến Werepig", href: "/bosses/werepig", image: "Nightmare_Werepig" },
  { name: "Ancient Sanctum", boss: "Ancient Guard Towers", href: "/bosses/ancient-sanctum", image: "Ancient_Guard_Tower" },
  { name: "Boss theo mùa", boss: "Deerclops · Moose · Antlion · Bearger", href: "/bosses/seasonal", image: "Deerclops" },
  { name: "Boss biển", boss: "Malbatross & Frostjaw", href: "/bosses/ocean", image: "Malbatross" },
] as const;

export function BossCards() {
  return <section id="cac-guide" aria-label="Chọn boss để đọc hướng dẫn" className="scroll-mt-6">
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-5 lg:grid-cols-4">
      {cards.map((card, index) => <Link key={card.href} href={card.href} className="group overflow-hidden rounded-2xl border border-nova-border bg-nova-surface transition-colors hover:border-nova-accent hover:bg-nova-surface-raised focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-nova-accent">
        <div className="relative h-36 bg-nova-surface-soft/70 sm:h-44">
          <Image src={`/assets/bosses/${card.image}.png`} alt={card.name} fill unoptimized={card.image === "Deerclops"} sizes="(max-width: 640px) 45vw, (max-width: 1024px) 30vw, 280px" priority={index < 4} className="object-contain p-4 transition-transform duration-200 group-hover:scale-105 motion-reduce:transform-none" />
          <span aria-hidden="true" className="absolute right-3 top-3 grid h-7 w-7 place-items-center rounded-full bg-nova-surface text-nova-accent">↗</span>
        </div>
        <div className="px-3 py-4 sm:px-5">
          <h2 className="text-base font-semibold tracking-tight group-hover:text-nova-accent sm:text-lg">{card.name}</h2>
          <p className="mt-1 text-xs leading-5 text-nova-muted">{card.boss}</p>
        </div>
      </Link>)}
    </div>
  </section>;
}
