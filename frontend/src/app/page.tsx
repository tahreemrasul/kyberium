import Link from "next/link";

const STEPS = [
  { n: "01", title: "Digitise your closet", body: "Snap a garment — Gemini tags its category, colours, cut and formality. You confirm." },
  { n: "02", title: "Drop an inspiration", body: "A Pinterest screenshot or saved post. We read what makes the look work." },
  { n: "03", title: "Rediscover what you own", body: "Fresh combinations from your own clothes, with styling advice and honest gaps." },
];

const LADDER = [
  { step: "1", title: "Restyle what you own", body: "Every look starts in your closet — creative substitutions first." },
  { step: "2", title: "Borrow, rent or buy pre-loved", body: "If a real gap remains, secondhand ideas come before new." },
  { step: "3", title: "Buy new, intentionally", body: "Only when you choose to — and only for a piece you'll re-wear." },
];

function Leaf({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden>
      <path d="M5 19c0-8 5-13 14-14 0 9-5 14-13 14" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5 19l7-7" strokeLinecap="round" />
    </svg>
  );
}

export default function Home() {
  return (
    <div className="flex flex-col gap-20 pt-14 sm:pt-20">
      <section className="grid items-center gap-12 lg:grid-cols-[1.2fr_1fr]">
        <div className="animate-rise">
          <p className="inline-flex items-center gap-2 rounded-full bg-sage-soft px-3 py-1 text-xs font-medium text-forest">
            <Leaf className="h-4 w-4" /> Shop your closet first
          </p>
          <h1 className="mt-6 font-display text-5xl leading-[1.04] sm:text-7xl">
            Love a look?
            <br />
            <span className="italic text-forest-2">Recreate it with what you own.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
            Meet your AI stylist. Turn outfit inspiration into fresh combinations from your own wardrobe, with creative
            substitutions and thoughtful styling advice before you buy anything new.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Link
              href="/studio"
              className="rounded-full bg-forest px-7 py-3.5 text-sm font-medium text-card transition-colors hover:bg-forest-2"
            >
              Recreate a look
            </Link>
            <Link
              href="/closet"
              className="rounded-full border border-line bg-card px-7 py-3.5 text-sm font-medium transition-colors hover:border-forest/40"
            >
              Build my closet
            </Link>
          </div>
        </div>
        <div className="relative hidden aspect-[4/5] lg:block" aria-hidden>
          <div className="absolute inset-0 rotate-[-3deg] rounded-[2.5rem] bg-sage-soft" />
          <div className="absolute inset-6 flex flex-col justify-between rounded-[2rem] bg-card p-8 shadow-sm">
            <p className="eyebrow">Inspiration → from your closet</p>
            <div className="grid grid-cols-2 gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element -- static sample art */}
              <img src="/api/media/samples/garments/s_camel_blazer.svg" alt="" className="rounded-2xl bg-well p-4" />
              {/* eslint-disable-next-line @next/next/no-img-element -- static sample art */}
              <img src="/api/media/samples/garments/s_sage_blazer.svg" alt="" className="rounded-2xl bg-well p-4" />
            </div>
            <p className="text-sm text-muted">
              “Your sage tailored blazer keeps the structured shoulders of the camel original — a fresh colour, the same
              polish.”
            </p>
            <p className="flex items-center gap-2 rounded-xl bg-sage-soft px-3 py-2 text-sm text-forest">
              <Leaf className="h-4 w-4 shrink-0" />
              4/4 pieces already in your closet · No new purchase needed
            </p>
          </div>
        </div>
      </section>

      {/* Sustainability, front and centre */}
      <section className="overflow-hidden rounded-[2rem] bg-forest text-card">
        <div className="grid gap-10 px-8 py-12 sm:px-12 lg:grid-cols-[1fr_1.3fr] lg:items-center">
          <div>
            <Leaf className="h-9 w-9 text-sage" />
            <h2 className="mt-4 font-display text-4xl leading-tight sm:text-5xl">
              The most sustainable outfit is the one already in your wardrobe.
            </h2>
            <p className="mt-4 max-w-md text-sage-soft">
              Rewear is built reuse-first: before anything new, it finds the look in clothes you already own — and
              tells you honestly when something is genuinely missing.
            </p>
          </div>
          <ol className="space-y-3">
            {LADDER.map((r, i) => (
              <li
                key={r.step}
                className={`flex gap-4 rounded-2xl px-5 py-4 ${i === 0 ? "bg-sage-soft text-forest" : "bg-forest-2/60"}`}
              >
                <span className="font-display text-3xl leading-none">{r.step}</span>
                <div>
                  <p className="font-medium">{r.title}</p>
                  <p className={`text-sm ${i === 0 ? "text-forest/80" : "text-sage-soft"}`}>{r.body}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
        <ul className="grid gap-4 border-t border-forest-2 px-8 py-6 text-sm text-sage-soft sm:grid-cols-3 sm:px-12">
          <li>Every suggested piece is a real garment from your closet — never an invented one.</li>
          <li>We count pieces reused and purchases potentially avoided. No made-up CO₂ figures.</li>
          <li>Shopping ideas appear only if you allow them — pre-loved first.</li>
        </ul>
      </section>

      <section className="grid gap-8 border-t border-line pt-12 sm:grid-cols-3">
        {STEPS.map((s) => (
          <div key={s.n}>
            <p className="font-display text-3xl text-sage">{s.n}</p>
            <h2 className="mt-3 font-display text-xl">{s.title}</h2>
            <p className="mt-2 text-sm leading-relaxed text-muted">{s.body}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
