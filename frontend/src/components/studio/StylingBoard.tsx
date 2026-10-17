"use client";

import { useState } from "react";
import { api, errorMessage } from "@/lib/api";
import { useApp } from "@/lib/store";
import type { Garment, Generation, Look, LookItem } from "@/lib/types";
import { Banner, Button, CATEGORY_SINGULAR, Dialog, EmptyState, GarmentImage, Icon, Spinner } from "../ui";

const REFINE_SUGGESTIONS = [
  "Make it more formal",
  "Give me a more colourful option",
  "Closer to the photo",
  "Only use items I already own",
];

export function StylingBoard({
  generation,
  activeLookId,
  onSelectLook,
  onChange,
  onEdit,
  onStartOver,
}: {
  generation: Generation;
  activeLookId: string | null;
  onSelectLook: (id: string) => void;
  onChange: (g: Generation, activeLookId?: string) => void;
  onEdit: () => void;
  onStartOver: () => void;
}) {
  const look = generation.looks.find((l) => l.id === activeLookId) ?? generation.looks[0];
  const [swapping, setSwapping] = useState<LookItem | null>(null);

  return (
    <div className="space-y-6 pt-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="eyebrow">Styling board</p>
          <h1 className="mt-1 font-display text-3xl sm:text-4xl">Your closet, restyled</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={onEdit}>
            <Icon name="edit" className="h-4 w-4" /> Edit preferences
          </Button>
          <Button variant="ghost" onClick={onStartOver}>
            New inspiration
          </Button>
        </div>
      </div>

      {generation.engine_note && <Banner tone="info">{generation.engine_note}</Banner>}

      <div className="grid gap-8 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
        <InspirationColumn generation={generation} />
        <div className="min-w-0 space-y-6">
          <div className="flex items-center gap-3 text-sm text-muted">
            <span className="eyebrow">Inspiration</span>
            <Icon name="arrow" className="h-4 w-4 text-sage" />
            <span className="eyebrow !text-forest">From your closet</span>
          </div>
          {!look ? (
            <EmptyState
              title="No honest match yet"
              body={
                generation.no_match_reason ??
                "None of your garments can stand in for this outfit's key pieces. Try a creative match or add pieces."
              }
            >
              <Button variant="primary" onClick={onEdit}>
                Try different preferences
              </Button>
            </EmptyState>
          ) : (
            <>
              {generation.looks.length > 1 && (
                <div className="flex flex-wrap gap-2" role="tablist" aria-label="Outfit options">
                  {generation.looks.map((l, i) => (
                    <button
                      key={l.id}
                      role="tab"
                      aria-selected={l.id === look.id}
                      onClick={() => onSelectLook(l.id)}
                      className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                        l.id === look.id ? "border-forest bg-forest text-card" : "border-line bg-card hover:border-forest/40"
                      }`}
                    >
                      <span className="mr-1.5 text-xs opacity-60">{i + 1}</span>
                      {l.title}
                    </button>
                  ))}
                </div>
              )}
              <LookPanel key={look.id} generation={generation} look={look} onSwap={setSwapping} onChange={onChange} />
            </>
          )}
        </div>
      </div>

      {look && (
        <SwapDrawer
          generation={generation}
          look={look}
          item={swapping}
          onClose={() => setSwapping(null)}
          onSwapped={(g) => {
            onChange(g, look.id);
            setSwapping(null);
          }}
        />
      )}
    </div>
  );
}

function InspirationColumn({ generation }: { generation: Generation }) {
  const a = generation.analysis;
  return (
    <aside className="min-w-0 space-y-5 lg:sticky lg:top-24 lg:self-start">
      <div className="overflow-hidden rounded-3xl border border-line bg-well">
        <GarmentImage
          src={generation.inspiration_image_url}
          alt="Your inspiration outfit"
          contain
          className="h-[46vh] w-full lg:h-[62vh]"
        />
      </div>
      <div className="space-y-3 text-sm">
        <p className="leading-relaxed">{a.summary}</p>
        {a.aesthetic.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {a.aesthetic.map((t) => (
              <span key={t} className="rounded-full bg-sage-soft px-2.5 py-0.5 text-xs text-forest">
                {t}
              </span>
            ))}
          </div>
        )}
        {(a.essential_traits?.length ?? 0) > 0 && (
          <div>
            <p className="eyebrow">What makes it work</p>
            <ul className="mt-1.5 space-y-1 text-xs">
              {a.essential_traits!.map((t) => (
                <li key={t} className="flex gap-2">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-forest" />
                  {t}
                </li>
              ))}
            </ul>
          </div>
        )}
        {(a.proportions || a.layering) && (
          <dl className="space-y-1.5 border-l-2 border-sage pl-3 text-xs text-muted">
            {a.proportions && (
              <div>
                <dt className="inline font-medium text-ink">Proportions · </dt>
                <dd className="inline">{a.proportions}</dd>
              </div>
            )}
            {a.layering && (
              <div>
                <dt className="inline font-medium text-ink">Layering · </dt>
                <dd className="inline">{a.layering}</dd>
              </div>
            )}
          </dl>
        )}
        <details>
          <summary className="cursor-pointer text-xs text-muted hover:text-ink">{a.pieces.length} pieces detected</summary>
          <ul className="mt-2 space-y-1 text-xs">
            {a.pieces.map((p) => (
              <li key={p.slot_id} className="flex gap-2">
                <span className="w-20 shrink-0 text-muted">{CATEGORY_SINGULAR[p.category]}</span>
                <span>
                  {p.description}
                  {p.visibility !== "clear" && <span className="text-muted"> ({p.visibility})</span>}
                </span>
              </li>
            ))}
          </ul>
          {a.ambiguities.length > 0 && (
            <p className="mt-2 text-xs text-muted">Not fully visible: {a.ambiguities.join("; ")}</p>
          )}
        </details>
      </div>
    </aside>
  );
}

function ImpactLine({ look }: { look: Look }) {
  const ok = !look.impact.purchase_needed;
  const avoided = look.impact.potential_purchases_avoided;
  return (
    <div
      className={`flex items-start gap-3 rounded-2xl px-4 py-3 text-sm ${ok ? "bg-sage-soft text-forest" : "bg-clay-soft/70 text-ink"}`}
    >
      <Icon name={ok ? "leaf" : "alert"} className={`mt-0.5 h-5 w-5 shrink-0 ${ok ? "text-forest" : "text-clay"}`} />
      <div>
        <p className="font-medium">{look.impact.headline}</p>
        <p className="mt-0.5 text-xs opacity-80">
          {look.impact.owned_count} owned piece{look.impact.owned_count === 1 ? "" : "s"} reused
          {avoided > 0 && ` · ${avoided} potential purchase${avoided === 1 ? "" : "s"} avoided (estimate)`}
        </p>
      </div>
      {look.review?.verdict === "approve" && (
        <span
          className="ml-auto inline-flex shrink-0 items-center gap-1 rounded-full bg-card/80 px-2.5 py-1 text-[11px] text-forest"
          title={look.review.strengths.join(" · ") || "Approved by the critic"}
        >
          <Icon name="check" className="h-3.5 w-3.5" />
          Critic-reviewed{look.review.rounds > 0 ? ` · revised ${look.review.rounds}×` : ""}
        </span>
      )}
    </div>
  );
}

function HowToWear({ look }: { look: Look }) {
  const steps = look.styling_instructions ?? [];
  if (!steps.length && !look.coherence) return null;
  return (
    <section className="rounded-2xl border border-sage/60 bg-card px-5 py-4">
      <h3 className="eyebrow !text-forest">How to wear it</h3>
      {steps.length > 0 && (
        <ol className="mt-2 space-y-1.5 text-sm">
          {steps.map((s, i) => (
            <li key={s} className="flex gap-2.5">
              <span className="font-display text-sage">{i + 1}</span>
              {s}
            </li>
          ))}
        </ol>
      )}
      {look.coherence && <p className="mt-3 text-sm leading-relaxed text-muted">{look.coherence}</p>}
    </section>
  );
}

function DecisionTrace({ generation }: { generation: Generation }) {
  const trace = generation.trace;
  if (!trace || trace.steps.length === 0) return null;
  const secs = trace.total_latency_ms ? (trace.total_latency_ms / 1000).toFixed(0) : null;
  return (
    <details className="rounded-2xl border border-line bg-card/60 px-4 py-3 text-sm">
      <summary className="cursor-pointer text-muted hover:text-ink">
        How your stylist decided · {trace.final_decision}
        {secs && <span className="text-xs"> · {secs}s</span>}
      </summary>
      <ol className="mt-3 space-y-3">
        {trace.steps.map((s, i) => (
          <li key={i} className="border-l-2 border-sage pl-3">
            <p className="text-xs uppercase tracking-wider text-muted">
              {s.step === "critic" ? "Critic" : "Stylist"} · pass {s.round}
              {s.latency_ms ? ` · ${(s.latency_ms / 1000).toFixed(1)}s` : ""}
            </p>
            <p className="font-medium">{s.summary}</p>
            {s.details.length > 0 && (
              <ul className="mt-1 space-y-0.5 text-xs text-muted">
                {s.details.map((d, j) => (
                  <li key={j}>{d}</li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ol>
      <p className="mt-3 text-[11px] text-muted">
        Orchestrated with Google ADK: a stylist agent proposes complete outfits, deterministic checks keep them to
        your real garments, and an independent critic agent reviews them against the inspiration — sending specific
        fixes back for at most {Math.max(0, trace.rounds - 1)} revision round(s). Critic verdicts are judgments, not
        scores.
      </p>
    </details>
  );
}

function LookPanel({
  generation,
  look,
  onSwap,
  onChange,
}: {
  generation: Generation;
  look: Look;
  onSwap: (item: LookItem) => void;
  onChange: (g: Generation, activeLookId?: string) => void;
}) {
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [instruction, setInstruction] = useState("");
  const [refining, setRefining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function save() {
    setSaving(true);
    setError(null);
    try {
      await api.saveLook(generation.id, look.id);
      setSaved(true);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function refine(text: string) {
    if (!text.trim()) return;
    setRefining(true);
    setError(null);
    try {
      const g = await api.refineLooks(generation.id, text.trim(), look.id);
      setInstruction("");
      onChange(g, g.looks[0]?.id);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setRefining(false);
    }
  }

  return (
    <div className="animate-rise space-y-6">
      <ImpactLine look={look} />
      <HowToWear look={look} />

      <ul className="grid grid-cols-2 gap-x-4 gap-y-7 xl:grid-cols-3">
        {look.items.map((item) => (
          <li key={item.garment_id} className="min-w-0" data-testid="look-item">
            <div className="relative">
              <GarmentImage
                src={item.garment.image_url}
                alt={item.garment.name}
                kind={item.garment.image_kind}
                className="aspect-[4/5] rounded-2xl"
              />
              <button
                onClick={() => onSwap(item)}
                className="absolute right-2 top-2 inline-flex items-center gap-1 rounded-full bg-card/90 px-3 py-1.5 text-xs font-medium text-forest shadow-sm hover:bg-card"
                aria-label={`Swap ${item.garment.name}`}
              >
                <Icon name="swap" className="h-3.5 w-3.5" /> Swap
              </button>
            </div>
            <p className="mt-3 text-[11px] uppercase tracking-wider text-muted">
              {item.replaces_description ? `Stands in for · ${item.replaces_description}` : "Completes the look"}
            </p>
            <h3 className="mt-0.5 font-display text-lg leading-snug">{item.garment.name}</h3>
            {item.role && <p className="text-xs italic text-forest-2">{item.role}</p>}
            <p className="mt-1.5 text-sm leading-relaxed text-ink/85">{item.explanation}</p>
            {(item.preserved.length > 0 || item.changed.length > 0) && (
              <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
                {item.preserved.map((p) => (
                  <span key={`k-${p}`} className="rounded-full bg-sage-soft px-2 py-0.5 text-forest">
                    keeps {p}
                  </span>
                ))}
                {item.changed.map((c) => (
                  <span key={`c-${c}`} className="rounded-full border border-line px-2 py-0.5 text-muted">
                    {c}
                  </span>
                ))}
              </div>
            )}
          </li>
        ))}
      </ul>

      {look.gaps.length > 0 && (
        <section className="space-y-3">
          <h3 className="eyebrow">Wardrobe gaps</h3>
          {look.gaps.map((gap) => (
            <div key={gap.slot_id} className="rounded-2xl border border-dashed border-line bg-card/60 px-4 py-3 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{gap.description}</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-[11px] ${
                    gap.essential ? "bg-clay-soft text-clay" : "bg-well text-muted"
                  }`}
                >
                  {gap.essential ? "Key piece missing" : "Optional — the look works without it"}
                </span>
              </div>
              <p className="mt-1 text-muted">{gap.reason}</p>
              {gap.sourcing_hint && (
                <p className="mt-2 text-xs text-ink/80">
                  <span className="font-medium">Search idea:</span> {gap.sourcing_hint}{" "}
                  <span className="text-muted">(not a product recommendation)</span>
                </p>
              )}
            </div>
          ))}
        </section>
      )}

      {(look.why_it_works.length > 0 || look.styling_tip) && (
        <section className="rounded-2xl bg-card px-5 py-4">
          <h3 className="eyebrow">Why it works</h3>
          <ul className="mt-2 space-y-1.5 text-sm">
            {look.why_it_works.map((w) => (
              <li key={w} className="flex gap-2">
                <Icon name="check" className="mt-0.5 h-4 w-4 shrink-0 text-sage" />
                {w}
              </li>
            ))}
          </ul>
          {look.styling_tip && <p className="mt-3 text-sm italic text-muted">Tip: {look.styling_tip}</p>}
          {((look.preserved_traits?.length ?? 0) > 0 || (look.deviations?.length ?? 0) > 0) && (
            <details className="mt-3 text-sm">
              <summary className="cursor-pointer text-xs text-muted hover:text-ink">
                What&apos;s kept and what changes
              </summary>
              <dl className="mt-2 space-y-2 text-xs">
                {(look.preserved_traits?.length ?? 0) > 0 && (
                  <div>
                    <dt className="font-medium text-forest">Kept from the inspiration</dt>
                    <dd className="text-muted">{look.preserved_traits!.join(" · ")}</dd>
                  </div>
                )}
                {(look.deviations?.length ?? 0) > 0 && (
                  <div>
                    <dt className="font-medium text-ink">Intentional differences</dt>
                    <dd className="text-muted">{look.deviations!.join(" · ")}</dd>
                  </div>
                )}
              </dl>
            </details>
          )}
        </section>
      )}

      <DecisionTrace generation={generation} />

      {look.warnings.length > 0 && (
        <ul className="space-y-1 text-xs text-muted">
          {look.warnings.map((w) => (
            <li key={w}>· {w}</li>
          ))}
        </ul>
      )}

      {generation.knowledge.length > 0 && (
        <details className="text-xs text-muted">
          <summary className="cursor-pointer hover:text-ink">Styling principles considered</summary>
          <ul className="mt-2 space-y-1">
            {generation.knowledge.map((k) => (
              <li key={k.id}>
                {k.text}{" "}
                {k.source_url ? (
                  <a href={k.source_url} target="_blank" rel="noreferrer" className="underline">
                    {k.source_title ?? "source"}
                  </a>
                ) : (
                  k.source_title && <span>— {k.source_title}</span>
                )}
              </li>
            ))}
          </ul>
        </details>
      )}

      {error && <Banner tone="error">{error}</Banner>}

      <div className="space-y-3 border-t border-line pt-5">
        <Button variant="primary" busy={saving} disabled={saved} onClick={save}>
          <Icon name={saved ? "check" : "bookmark"} className="h-4 w-4" />
          {saved ? "Saved to My Looks" : "Save this look"}
        </Button>
        <form
          className="flex flex-col gap-2 sm:flex-row"
          onSubmit={(e) => {
            e.preventDefault();
            void refine(instruction);
          }}
        >
          <label className="flex-1">
            <span className="sr-only">Ask the stylist to refine</span>
            <input
              value={instruction}
              onChange={(e) => setInstruction(e.target.value)}
              placeholder="Refine: “keep the blazer, but change the trousers”"
              maxLength={300}
              className="w-full rounded-full border border-line bg-card px-4 py-2.5 text-sm outline-none focus:border-forest/60"
            />
          </label>
          <Button type="submit" variant="secondary" busy={refining} disabled={!instruction.trim()}>
            <Icon name="sparkle" className="h-4 w-4" /> Restyle
          </Button>
        </form>
        <div className="flex flex-wrap gap-2">
          {REFINE_SUGGESTIONS.map((s) => (
            <button
              key={s}
              disabled={refining}
              onClick={() => refine(s)}
              className="rounded-full bg-well px-3 py-1 text-xs text-ink hover:bg-sage-soft disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>
        {refining && (
          <p className="flex items-center gap-2 text-xs text-muted">
            <Spinner className="h-3.5 w-3.5" /> Restyling with your request…
          </p>
        )}
      </div>
    </div>
  );
}

function compatible(a: Garment, b: Garment): boolean {
  if (a.category === b.category) return true;
  // A mid-layer knit or cardigan can take an outer layer's role (and vice versa); base layers can't.
  const top = a.category === "top" ? a : b.category === "top" ? b : null;
  const other = top === a ? b : a;
  return !!top && other.category === "outerwear" && top.layer === "mid";
}

function SwapDrawer({
  generation,
  look,
  item,
  onClose,
  onSwapped,
}: {
  generation: Generation;
  look: Look;
  item: LookItem | null;
  onClose: () => void;
  onSwapped: (g: Generation) => void;
}) {
  const { wardrobe } = useApp();
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const inLook = new Set(look.items.map((i) => i.garment_id));
  const ranked = item?.replaces_slot_id ? (generation.candidates[item.replaces_slot_id] ?? []) : [];
  const rank = new Map(ranked.map((c, i) => [c.garment_id, i]));
  const options = item
    ? (wardrobe ?? [])
        .filter((g) => !inLook.has(g.id) && compatible(g, item.garment))
        .sort((a, b) => (rank.get(a.id) ?? 99) - (rank.get(b.id) ?? 99))
    : [];

  async function swap(g: Garment) {
    if (!item) return;
    setBusyId(g.id);
    setError(null);
    try {
      onSwapped(await api.swapItem(generation.id, look.id, item.garment_id, g.id));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <Dialog open={!!item} onClose={onClose} title={item ? `Swap ${item.garment.name}` : "Swap"} side>
      {item && (
        <div className="space-y-4">
          <p className="text-sm text-muted">
            Only pieces you own that can play the same role
            {item.replaces_description ? ` as the ${item.replaces_description.toLowerCase()}` : ""}.
          </p>
          {error && <Banner tone="error">{error}</Banner>}
          {options.length === 0 && <p className="text-sm text-muted">No other owned pieces fit this role yet.</p>}
          <ul className="grid grid-cols-2 gap-4">
            {options.map((g) => (
              <li key={g.id}>
                <button onClick={() => swap(g)} disabled={!!busyId} className="group w-full text-left disabled:opacity-60">
                  <div className="relative">
                    <GarmentImage
                      src={g.image_url}
                      alt={g.name}
                      kind={g.image_kind}
                      className="aspect-[4/5] rounded-xl transition group-hover:ring-2 group-hover:ring-forest/40"
                    />
                    {rank.has(g.id) && (
                      <span className="absolute right-2 top-2 rounded-full bg-forest px-2 py-0.5 text-[10px] text-card">
                        good match
                      </span>
                    )}
                    {busyId === g.id && (
                      <span className="absolute inset-0 flex items-center justify-center bg-card/60">
                        <Spinner />
                      </span>
                    )}
                  </div>
                  <p className="mt-1.5 truncate text-sm">{g.name}</p>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Dialog>
  );
}
