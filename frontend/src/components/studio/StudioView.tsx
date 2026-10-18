"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { api, ApiError, errorMessage, mediaUrl } from "@/lib/api";
import { useApp } from "@/lib/store";
import type { Fidelity, InspirationAnalysis, Occasion, SampleInspiration, Shopping, StylePreferences } from "@/lib/types";
import { Banner, Button, ChipGroup, FIDELITY_LABEL, GarmentImage, Icon, OCCASION_LABEL, SHOPPING_LABEL, Spinner } from "../ui";
import { StylingBoard } from "./StylingBoard";

const MAX_BYTES = 8 * 1024 * 1024;
const ACCEPTED = ["image/jpeg", "image/png", "image/webp"];
type Phase = "idle" | "analyzing" | "composing";

export function StudioView() {
  const { wardrobe, health, studio, updateStudio, resetStudio, setWardrobe } = useApp();
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState<{ message: string; retryable: boolean } | null>(null);
  const [editing, setEditing] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [pendingPreview, setPendingPreview] = useState<string | null>(null);
  const [pendingSample, setPendingSample] = useState<SampleInspiration | null>(null);
  const [samples, setSamples] = useState<SampleInspiration[]>([]);
  const [loadingSamples, setLoadingSamples] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api
      .sampleInspirations()
      .then(setSamples)
      .catch(() => setSamples([]));
  }, []);
  useEffect(() => () => void (pendingPreview && URL.revokeObjectURL(pendingPreview)), [pendingPreview]);

  const prefs = studio.prefs;
  const setPrefs = (patch: Partial<StylePreferences>) => updateStudio({ prefs: { ...prefs, ...patch } });
  const previewSrc = pendingPreview ?? (pendingSample ? mediaUrl(pendingSample.image_url) : null);
  const currentImage = previewSrc ?? (studio.inspiration ? mediaUrl(studio.inspiration.image_url) : null);
  const closetEmpty = wardrobe !== null && wardrobe.length === 0;

  function chooseFile(f: File | undefined) {
    if (!f) return;
    if (!ACCEPTED.includes(f.type)) return setError({ message: "Please choose a JPEG, PNG or WebP image.", retryable: false });
    if (f.size > MAX_BYTES) return setError({ message: "That image is over 8 MB — try a smaller one.", retryable: false });
    setError(null);
    setPendingSample(null);
    setPendingFile(f);
    setPendingPreview(URL.createObjectURL(f));
  }

  function chooseSample(s: SampleInspiration) {
    setError(null);
    setPendingFile(null);
    setPendingPreview(null);
    setPendingSample(s);
  }

  function clearImage() {
    setPendingFile(null);
    setPendingPreview(null);
    setPendingSample(null);
    updateStudio({ inspiration: null, generation: null, activeLookId: null });
  }

  async function loadSampleCloset() {
    setLoadingSamples(true);
    try {
      setWardrobe((await api.loadSampleWardrobe()).items);
      setError(null);
    } catch (err) {
      setError({ message: errorMessage(err), retryable: true });
    } finally {
      setLoadingSamples(false);
    }
  }

  async function findOutfits() {
    setError(null);
    let inspiration = studio.inspiration;
    try {
      if (pendingFile || pendingSample) {
        setPhase("analyzing");
        inspiration = await api.createInspiration(
          pendingFile ? { file: pendingFile } : { sampleId: (pendingSample as SampleInspiration).id },
        );
        updateStudio({ inspiration, generation: null, activeLookId: null });
        setPendingFile(null);
        setPendingPreview(null);
        setPendingSample(null);
      }
      if (!inspiration) {
        return setError({ message: "Add an inspiration image first.", retryable: false });
      }
      setPhase("composing");
      const generation = await api.generateLooks(inspiration.id, prefs);
      updateStudio({ generation, activeLookId: generation.looks[0]?.id ?? null });
      setEditing(false);
    } catch (err) {
      setError({ message: errorMessage(err), retryable: err instanceof ApiError ? err.retryable : true });
    } finally {
      setPhase("idle");
    }
  }

  if (studio.generation && !editing && phase === "idle") {
    return (
      <StylingBoard
        generation={studio.generation}
        activeLookId={studio.activeLookId}
        onSelectLook={(id) => updateStudio({ activeLookId: id })}
        onChange={(generation, activeLookId) =>
          updateStudio({
            generation,
            prefs: generation.preferences,
            activeLookId: activeLookId ?? generation.looks[0]?.id ?? null,
          })
        }
        onEdit={() => setEditing(true)}
        onStartOver={() => {
          resetStudio();
          setEditing(false);
        }}
      />
    );
  }

  const busy = phase !== "idle";
  const canRun = !!currentImage && !busy && !closetEmpty;

  return (
    <div className="grid gap-10 pt-8 sm:pt-12 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)]">
      <section className="space-y-4">
        <p className="eyebrow">1 · Inspiration</p>
        {currentImage ? (
          <div className="relative overflow-hidden rounded-3xl border border-line bg-well">
            {/* eslint-disable-next-line @next/next/no-img-element -- local preview or API media */}
            <img src={currentImage} alt="Inspiration outfit" className="max-h-[68vh] w-full object-contain" />
            {!busy && (
              <div className="absolute right-3 top-3 flex gap-2">
                <button
                  onClick={() => inputRef.current?.click()}
                  className="rounded-full bg-card/90 px-3 py-1.5 text-xs font-medium shadow-sm hover:bg-card"
                >
                  Replace
                </button>
                <button
                  onClick={clearImage}
                  className="rounded-full bg-card/90 px-3 py-1.5 text-xs font-medium shadow-sm hover:bg-card"
                >
                  Remove
                </button>
              </div>
            )}
            {busy && <div className="skeleton absolute inset-x-0 bottom-0 h-1.5" />}
          </div>
        ) : (
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              chooseFile(e.dataTransfer.files[0]);
            }}
            className="flex aspect-[4/5] max-h-[68vh] w-full flex-col items-center justify-center gap-3 rounded-3xl border border-dashed border-sage bg-card px-6 text-center transition-colors hover:bg-sage-soft/40"
          >
            <Icon name="upload" className="h-9 w-9 text-forest" />
            <span className="font-display text-2xl">Drop an outfit you love</span>
            <span className="max-w-xs text-sm text-muted">
              A Pinterest or Instagram screenshot works well. JPEG, PNG or WebP up to 8 MB.
            </span>
          </button>
        )}
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED.join(",")}
          className="hidden"
          data-testid="inspiration-file"
          onChange={(e) => {
            chooseFile(e.target.files?.[0]);
            e.target.value = "";
          }}
        />
        {samples.length > 0 && !busy && (
          <div>
            <p className="mb-2 text-xs text-muted">
              Or try a sample inspiration{health && !health.ai_enabled ? " (live photo analysis needs Gemini)" : ""}
            </p>
            <div className="grid grid-cols-4 gap-2">
              {samples.map((s) => (
                <button
                  key={s.id}
                  onClick={() => chooseSample(s)}
                  title={s.scenario}
                  aria-pressed={pendingSample?.id === s.id}
                  className={`overflow-hidden rounded-xl border-2 text-left transition ${
                    pendingSample?.id === s.id ? "border-forest" : "border-transparent hover:border-line"
                  }`}
                >
                  <GarmentImage src={s.image_url} alt={s.title} className="aspect-[9/11]" />
                  <span className="block truncate px-1 py-1 text-[11px] text-muted">{s.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </section>

      <section className="space-y-7">
        <div>
          <p className="eyebrow">2 · Your brief</p>
          <h1 className="mt-2 font-display text-4xl sm:text-5xl">Style Studio</h1>
          <p className="mt-2 text-sm text-muted">
            We&apos;ll read the outfit — its pieces, proportions, palette and mood — and rebuild it from your closet.
          </p>
        </div>
        <ChipGroup<Occasion>
          label="Occasion"
          value={prefs.occasion}
          onChange={(occasion) => setPrefs({ occasion })}
          options={(Object.keys(OCCASION_LABEL) as Occasion[]).map((o) => ({ value: o, label: OCCASION_LABEL[o] }))}
        />
        <ChipGroup<Fidelity>
          label="How close to the photo?"
          value={prefs.fidelity}
          onChange={(fidelity) => setPrefs({ fidelity })}
          options={(Object.keys(FIDELITY_LABEL) as Fidelity[]).map((f) => ({ value: f, ...FIDELITY_LABEL[f] }))}
        />
        <ChipGroup<Shopping>
          label="Shopping"
          value={prefs.shopping}
          onChange={(shopping) => setPrefs({ shopping })}
          options={(Object.keys(SHOPPING_LABEL) as Shopping[]).map((s) => ({ value: s, ...SHOPPING_LABEL[s] }))}
        />
        <p className="-mt-4 flex items-start gap-2 rounded-xl bg-sage-soft/70 px-3 py-2 text-xs text-forest">
          <Icon name="leaf" className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          Reuse first, always: every look is built from your closet. Shopping ideas only appear for genuine gaps — and
          only if you allow them, pre-loved first.
        </p>
        <details className="group rounded-2xl border border-line bg-card/60 px-4 py-3">
          <summary className="cursor-pointer text-sm text-muted group-open:text-ink">More preferences</summary>
          <label className="mt-3 block space-y-1.5">
            <span className="text-xs text-muted">Anything else for the stylist?</span>
            <textarea
              value={prefs.notes ?? ""}
              onChange={(e) => setPrefs({ notes: e.target.value || null })}
              maxLength={300}
              rows={2}
              placeholder="e.g. no heels, I prefer warmer colours"
              className="w-full rounded-xl border border-line bg-card px-3 py-2 text-sm outline-none focus:border-forest/60"
            />
          </label>
          {(prefs.keep_garment_ids.length > 0 || prefs.exclude_garment_ids.length > 0) && (
            <div className="mt-3 flex items-center justify-between gap-3 text-xs text-muted">
              <span>
                Keeping {prefs.keep_garment_ids.length}, avoiding {prefs.exclude_garment_ids.length} piece(s) from earlier
                refinements.
              </span>
              <button className="underline" onClick={() => setPrefs({ keep_garment_ids: [], exclude_garment_ids: [] })}>
                Clear
              </button>
            </div>
          )}
        </details>

        {closetEmpty && (
          <Banner
            tone="error"
            action={
              <div className="flex gap-2">
                <Button variant="ghost" busy={loadingSamples} onClick={loadSampleCloset}>
                  Load sample wardrobe
                </Button>
                <Link href="/closet" className="rounded-full px-3 py-2 text-sm text-forest hover:bg-sage-soft/60">
                  Add garments
                </Link>
              </div>
            }
          >
            Your closet is empty — Rewear only styles with clothes you own.
          </Banner>
        )}

        {error && (
          <Banner
            tone="error"
            action={
              error.retryable ? (
                <Button variant="ghost" onClick={findOutfits}>
                  <Icon name="refresh" className="h-4 w-4" /> Try again
                </Button>
              ) : undefined
            }
          >
            {error.message} Your image and choices are kept.
          </Banner>
        )}

        {busy ? (
          <Progress phase={phase} analysis={studio.inspiration?.analysis ?? null} />
        ) : (
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="primary" className="px-7 py-3 text-base" disabled={!canRun} onClick={findOutfits}>
              <Icon name="sparkle" className="h-5 w-5" /> Find my outfits
            </Button>
            {studio.generation && (
              <Button variant="ghost" onClick={() => setEditing(false)}>
                Back to board
              </Button>
            )}
            {!currentImage && <span className="text-xs text-muted">Add an inspiration image to start.</span>}
          </div>
        )}
      </section>
    </div>
  );
}

const STEPS = [
  "Analysing your inspiration's DNA",
  "Stylist composing complete outfits from your closet",
  "Critic reviewing each look against the inspiration",
  "Refining anything the critic flagged",
];
// Typical timings of the stylist -> critic -> refinement workflow; the board's
// "How your stylist decided" panel shows what actually happened.
const STEP_AFTER_MS = [0, 0, 13000, 24000];

function Progress({ phase, analysis }: { phase: Phase; analysis: InspirationAnalysis | null }) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    if (phase !== "composing") return;
    const started = Date.now();
    const id = window.setInterval(() => setElapsed(Date.now() - started), 1000);
    return () => window.clearInterval(id);
  }, [phase]);
  const current =
    phase === "analyzing" ? 0 : Math.max(1, STEP_AFTER_MS.filter((t, i) => i > 0 && phase === "composing" && elapsed >= t).length);
  return (
    <div className="space-y-4 rounded-2xl border border-line bg-card px-5 py-4" aria-live="polite">
      <ol className="space-y-2.5">
        {STEPS.map((label, i) => {
          const state = i < current ? "done" : i === current ? "active" : "todo";
          return (
            <li key={label} className={`flex items-center gap-3 text-sm ${state === "todo" ? "text-muted" : "text-ink"}`}>
              {state === "done" ? (
                <Icon name="check" className="h-4 w-4 text-forest" />
              ) : state === "active" ? (
                <Spinner className="h-4 w-4 text-forest" />
              ) : (
                <span className="h-4 w-4 rounded-full border border-line" />
              )}
              {label}
            </li>
          );
        })}
      </ol>
      {phase === "composing" && elapsed > 8000 && (
        <p className="text-xs text-muted">Quality takes a moment — weak looks are sent back, not shown.</p>
      )}
      {phase === "composing" && analysis && analysis.pieces.length > 0 && (
        <div className="animate-rise border-t border-line pt-3">
          <p className="text-xs text-muted">We spotted</p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {analysis.pieces.map((p) => (
              <span key={p.slot_id} className="rounded-full bg-sage-soft px-2.5 py-0.5 text-xs text-forest">
                {p.description}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
