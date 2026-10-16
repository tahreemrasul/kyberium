import Link from "next/link";

const STEPS = [
  { n: "01", title: "Digitise your closet", body: "Snap a garment — Gemini tags its category, colours, cut and formality. You confirm." },
  { n: "02", title: "Drop an inspiration", body: "A Pinterest screenshot or saved post. We read its pieces, proportions and mood." },
  { n: "03", title: "Rediscover what you own", body: "Get explained recreations made only from your clothes — and honest gaps." },
];

export default function Home() {
  return (
    <div className="flex flex-col gap-20 pt-14 sm:pt-24">
      <section className="grid items-center gap-12 lg:grid-cols-[1.2fr_1fr]">
        <div className="animate-rise">
          <p className="eyebrow">Reuse first · Your choice always</p>
          <h1 className="mt-5 font-display text-5xl leading-[1.04] sm:text-7xl">
            Love the look.
            <br />
            <span className="italic text-forest-2">You already own it.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
            Rewear is an AI styling studio that recreates the outfits you save online using the clothes already in your
            wardrobe — explaining every substitution before you ever think about buying.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Link
              href="/studio"
              className="rounded-full bg-forest px-7 py-3.5 text-sm font-medium text-card transition-colors hover:bg-forest-2"
            >
              Open the Style Studio
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
            <p className="rounded-xl bg-sage-soft px-3 py-2 text-sm text-forest">
              4/4 pieces already in your closet · No new purchase needed
            </p>
          </div>
        </div>
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

      <section className="rounded-3xl bg-forest px-8 py-10 text-card sm:px-12">
        <h2 className="font-display text-3xl">Honest by design</h2>
        <ul className="mt-5 grid gap-4 text-sm text-sage-soft sm:grid-cols-3">
          <li>Every suggested piece is a real garment from your closet — never an invented one.</li>
          <li>We count pieces reused and purchases potentially avoided. No made-up CO₂ figures.</li>
          <li>When something is genuinely missing, we say so — and only suggest shopping if you allow it.</li>
        </ul>
      </section>
    </div>
  );
}
