"use client";

import { useEffect, useRef, useState } from "react";
import { api, errorMessage } from "@/lib/api";
import { useApp } from "@/lib/store";
import {
  CATEGORIES,
  OCCASIONS,
  type Garment,
  type GarmentAnalysis,
  type GarmentAttributes,
  type Formality,
  type Layer,
} from "@/lib/types";
import {
  Banner,
  Button,
  CATEGORY_SINGULAR,
  Chip,
  Dialog,
  FORMALITY_LABEL,
  GarmentImage,
  Icon,
  OCCASION_LABEL,
  Spinner,
} from "../ui";

const MAX_BYTES = 8 * 1024 * 1024;
const ACCEPTED = ["image/jpeg", "image/png", "image/webp"];
const LAYER_LABEL: Record<Layer, string> = { base: "Base", mid: "Mid layer", outer: "Outer layer", none: "Not a layer" };

/** Form state keeps list fields as raw text so typing commas feels natural. */
export interface GarmentFormState extends Omit<GarmentAttributes, "colors" | "style_tags"> {
  colorsText: string;
  tagsText: string;
}

export function toFormState(a: Partial<GarmentAttributes> | null | undefined): GarmentFormState {
  return {
    name: a?.name ?? "",
    category: a?.category ?? "top",
    subcategory: a?.subcategory ?? "",
    silhouette: a?.silhouette ?? "",
    pattern: a?.pattern ?? "",
    formality: a?.formality ?? "casual",
    layer: a?.layer ?? "none",
    occasions: a?.occasions ?? [],
    material_appearance: a?.material_appearance ?? "",
    colorsText: (a?.colors ?? []).join(", "),
    tagsText: (a?.style_tags ?? []).join(", "),
  };
}

const splitList = (s: string) =>
  s
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);

export function fromFormState(f: GarmentFormState): GarmentAttributes {
  const blank = (s?: string | null) => (s && s.trim() ? s.trim() : null);
  return {
    name: f.name.trim(),
    category: f.category,
    subcategory: blank(f.subcategory),
    colors: splitList(f.colorsText),
    silhouette: blank(f.silhouette),
    pattern: blank(f.pattern),
    formality: f.formality,
    layer: f.layer,
    style_tags: splitList(f.tagsText),
    occasions: f.occasions,
    material_appearance: blank(f.material_appearance),
  };
}

export function formProblems(f: GarmentFormState): string | null {
  if (!f.name.trim()) return "Give the garment a short name.";
  if (!splitList(f.colorsText).length) return "Add at least one colour.";
  return null;
}

function Field({
  label,
  flagged,
  children,
  hint,
}: {
  label: string;
  flagged?: boolean;
  children: React.ReactNode;
  hint?: string;
}) {
  return (
    <div className="space-y-1.5">
      <span className="flex items-center gap-2 text-xs font-medium text-muted">
        {label}
        {flagged && (
          <span className="rounded-full bg-clay-soft px-2 py-0.5 text-[10px] text-clay">AI unsure — please check</span>
        )}
      </span>
      {children}
      {hint && <span className="block text-[11px] text-muted">{hint}</span>}
    </div>
  );
}

const inputCls =
  "w-full rounded-xl border border-line bg-card px-3 py-2 text-sm outline-none transition-colors focus:border-forest/60";

export function GarmentForm({
  value,
  onChange,
  flagged = [],
}: {
  value: GarmentFormState;
  onChange: (v: GarmentFormState) => void;
  flagged?: string[];
}) {
  const set = <K extends keyof GarmentFormState>(k: K, v: GarmentFormState[K]) => onChange({ ...value, [k]: v });
  const flag = (k: string) => flagged.includes(k);
  const text = (k: "name" | "subcategory" | "silhouette" | "pattern" | "material_appearance" | "colorsText" | "tagsText", label: string) => (
    <input
      aria-label={label}
      className={inputCls}
      value={(value[k] as string | null) ?? ""}
      onChange={(e) => set(k, e.target.value)}
      maxLength={80}
    />
  );
  return (
    <div className="space-y-4">
      <Field label="Name" flagged={flag("name")}>
        {text("name", "Name")}
      </Field>
      <Field label="Category" flagged={flag("category")}>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((c) => (
            <Chip key={c} selected={value.category === c} onClick={() => set("category", c)}>
              {CATEGORY_SINGULAR[c]}
            </Chip>
          ))}
        </div>
      </Field>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Type" flagged={flag("subcategory")} hint="e.g. blazer, jeans, loafers">
          {text("subcategory", "Type")}
        </Field>
        <Field label="Colours" flagged={flag("colors")} hint="Main colour first, comma separated">
          {text("colorsText", "Colours")}
        </Field>
        <Field label="Silhouette / cut" flagged={flag("silhouette")}>
          {text("silhouette", "Silhouette")}
        </Field>
        <Field label="Pattern" flagged={flag("pattern")}>
          {text("pattern", "Pattern")}
        </Field>
      </div>
      <Field label="Formality" flagged={flag("formality")}>
        <div className="flex flex-wrap gap-2">
          {(Object.keys(FORMALITY_LABEL) as Formality[]).map((f) => (
            <Chip key={f} selected={value.formality === f} onClick={() => set("formality", f)}>
              {FORMALITY_LABEL[f]}
            </Chip>
          ))}
        </div>
      </Field>
      <Field label="Layering role" flagged={flag("layer")}>
        <div className="flex flex-wrap gap-2">
          {(Object.keys(LAYER_LABEL) as Layer[]).map((l) => (
            <Chip key={l} selected={value.layer === l} onClick={() => set("layer", l)}>
              {LAYER_LABEL[l]}
            </Chip>
          ))}
        </div>
      </Field>
      <Field label="Good for" flagged={flag("occasions")}>
        <div className="flex flex-wrap gap-2">
          {OCCASIONS.map((o) => (
            <Chip
              key={o}
              selected={value.occasions.includes(o)}
              onClick={() =>
                set(
                  "occasions",
                  value.occasions.includes(o) ? value.occasions.filter((x) => x !== o) : [...value.occasions, o],
                )
              }
            >
              {OCCASION_LABEL[o]}
            </Chip>
          ))}
        </div>
      </Field>
      <Field label="Style tags" flagged={flag("style_tags")} hint="Comma separated, e.g. minimal, tailored">
        {text("tagsText", "Style tags")}
      </Field>
      <Field
        label="Fabric appearance"
        flagged={flag("material_appearance")}
        hint="How it looks — Rewear never infers exact fabric, brand or sourcing from a photo."
      >
        {text("material_appearance", "Fabric appearance")}
      </Field>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Upload -> AI tagging -> review -> save
// ---------------------------------------------------------------------------

type Phase = "pick" | "analyzing" | "review";

export function AddGarmentDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { refreshWardrobe, health } = useApp();
  const [phase, setPhase] = useState<Phase>("pick");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<GarmentAnalysis | null>(null);
  const [form, setForm] = useState<GarmentFormState>(toFormState(null));
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => () => void (preview && URL.revokeObjectURL(preview)), [preview]);

  function reset() {
    setPhase("pick");
    setFile(null);
    setPreview(null);
    setAnalysis(null);
    setForm(toFormState(null));
    setError(null);
  }

  function close() {
    reset();
    onClose();
  }

  async function analyze(f: File) {
    setPhase("analyzing");
    setError(null);
    try {
      const res = await api.analyzeGarment(f);
      setAnalysis(res);
      setForm(toFormState(res.draft));
      setPhase("review");
    } catch (err) {
      setError(errorMessage(err));
      setPhase("pick");
    }
  }

  function choose(f: File | undefined) {
    if (!f) return;
    if (!ACCEPTED.includes(f.type)) return setError("Please choose a JPEG, PNG or WebP photo.");
    if (f.size > MAX_BYTES) return setError("That photo is over 8 MB — try a smaller one.");
    setFile(f);
    setPreview(URL.createObjectURL(f));
    void analyze(f);
  }

  async function retryTagging() {
    if (!analysis) return;
    setBusy(true);
    setError(null);
    try {
      const res = await api.reanalyzeUpload(analysis.upload_id);
      setAnalysis(res);
      if (res.draft) setForm(toFormState(res.draft));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function save() {
    if (!analysis) return;
    const problem = formProblems(form);
    if (problem) return setError(problem);
    setBusy(true);
    setError(null);
    try {
      await api.createGarment(analysis.upload_id, fromFormState(form));
      await refreshWardrobe();
      close();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Dialog open={open} onClose={close} title="Add a garment">
      {phase === "pick" && (
        <div className="space-y-4">
          {error && <Banner tone="error">{error}</Banner>}
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              choose(e.dataTransfer.files[0]);
            }}
            className="flex w-full flex-col items-center gap-3 rounded-3xl border border-dashed border-sage bg-card px-6 py-14 text-center hover:bg-sage-soft/40"
          >
            <Icon name="upload" className="h-8 w-8 text-forest" />
            <span className="font-display text-xl">Drop a photo of one garment</span>
            <span className="text-sm text-muted">Flat lay or on a hanger works best · JPEG, PNG or WebP up to 8 MB</span>
          </button>
          {file && error && (
            <Button onClick={() => analyze(file)} variant="secondary">
              <Icon name="refresh" className="h-4 w-4" /> Try this photo again
            </Button>
          )}
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED.join(",")}
            className="hidden"
            data-testid="garment-file"
            onChange={(e) => choose(e.target.files?.[0])}
          />
        </div>
      )}

      {phase !== "pick" && (
        <div className="grid gap-6 sm:grid-cols-[200px_1fr]">
          <div className="space-y-3">
            {analysis?.display_url ? (
              <GarmentImage
                src={analysis.display_url}
                alt="Your garment, standardised for the closet"
                kind="cutout"
                className="aspect-[4/5] rounded-2xl"
              />
            ) : (
              preview && (
                <div className="aspect-[4/5] overflow-hidden rounded-2xl bg-well">
                  {/* eslint-disable-next-line @next/next/no-img-element -- local preview */}
                  <img src={preview} alt="Your garment" className="h-full w-full object-cover" />
                </div>
              )
            )}
            {analysis?.engine === "gemini" && (
              <p className="flex items-center gap-1.5 text-xs text-muted">
                <Icon name="sparkle" className="h-3.5 w-3.5 text-sage" />
                Tagged by Gemini{analysis.cached ? " (cached)" : ""} — edit anything that&apos;s off.
              </p>
            )}
          </div>
          <div>
            {phase === "analyzing" ? (
              <div className="flex h-full min-h-60 flex-col items-center justify-center gap-3 text-center text-sm text-muted">
                <Spinner className="h-7 w-7 text-forest" />
                <p>Reading your garment — category, colours, cut and formality…</p>
              </div>
            ) : (
              <div className="space-y-4">
                {analysis?.message && (
                  <Banner
                    tone={analysis.draft ? "info" : "error"}
                    action={
                      !analysis.draft && health?.ai_enabled ? (
                        <Button variant="ghost" busy={busy} onClick={retryTagging}>
                          Retry AI tagging
                        </Button>
                      ) : undefined
                    }
                  >
                    {analysis.message}
                  </Banner>
                )}
                <GarmentForm value={form} onChange={setForm} flagged={analysis?.draft?.low_confidence_fields} />
                {error && <Banner tone="error">{error}</Banner>}
                <div className="flex justify-end gap-3 pt-2">
                  <Button variant="ghost" onClick={reset}>
                    Choose another photo
                  </Button>
                  <Button variant="primary" busy={busy} onClick={save}>
                    <Icon name="check" className="h-4 w-4" /> Save to closet
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Details / edit / delete
// ---------------------------------------------------------------------------

export function GarmentDrawer({ garment, onClose }: { garment: Garment | null; onClose: () => void }) {
  const { refreshWardrobe } = useApp();
  const [form, setForm] = useState<GarmentFormState>(toFormState(garment));
  const [busy, setBusy] = useState<"save" | "delete" | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastId, setLastId] = useState<string | null>(null);

  if (garment && garment.id !== lastId) {
    // Reset local edit state when a different garment is opened.
    setLastId(garment.id);
    setForm(toFormState(garment));
    setConfirmDelete(false);
    setError(null);
  }

  async function save() {
    if (!garment) return;
    const problem = formProblems(form);
    if (problem) return setError(problem);
    setBusy("save");
    setError(null);
    try {
      await api.updateGarment(garment.id, fromFormState(form));
      await refreshWardrobe();
      onClose();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(null);
    }
  }

  async function remove() {
    if (!garment) return;
    setBusy("delete");
    try {
      await api.deleteGarment(garment.id);
      await refreshWardrobe();
      onClose();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(null);
    }
  }

  return (
    <Dialog open={!!garment} onClose={onClose} title={garment?.name ?? "Garment"} side>
      {garment && (
        <div className="space-y-5">
          <GarmentImage
            src={garment.image_url}
            alt={garment.name}
            kind={garment.image_kind}
            className="aspect-[4/5] w-full rounded-2xl"
          />
          <GarmentForm value={form} onChange={setForm} />
          {error && <Banner tone="error">{error}</Banner>}
          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
            {confirmDelete ? (
              <div className="flex items-center gap-2">
                <Button variant="danger" busy={busy === "delete"} onClick={remove}>
                  Yes, delete
                </Button>
                <Button variant="ghost" onClick={() => setConfirmDelete(false)}>
                  Keep it
                </Button>
              </div>
            ) : (
              <Button variant="ghost" onClick={() => setConfirmDelete(true)} className="text-clay">
                <Icon name="trash" className="h-4 w-4" /> Delete
              </Button>
            )}
            <Button variant="primary" busy={busy === "save"} onClick={save}>
              Save changes
            </Button>
          </div>
        </div>
      )}
    </Dialog>
  );
}
