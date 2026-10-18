"use client";

import { useMemo, useState } from "react";
import { api, errorMessage } from "@/lib/api";
import { useApp } from "@/lib/store";
import { CATEGORIES, type Category, type Garment } from "@/lib/types";
import { Banner, Button, CATEGORY_LABEL, EmptyState, FORMALITY_LABEL, GarmentImage, Icon } from "../ui";
import { AddGarmentDialog, GarmentDrawer } from "./GarmentEditor";

function matches(g: Garment, q: string): boolean {
  if (!q) return true;
  const hay = [g.name, g.subcategory, g.category, g.silhouette, g.pattern, ...g.colors, ...g.style_tags, ...g.occasions]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return q
    .toLowerCase()
    .split(/\s+/)
    .every((w) => hay.includes(w));
}

export function GarmentCard({ garment, onClick }: { garment: Garment; onClick?: () => void }) {
  return (
    <button type="button" onClick={onClick} className="group animate-rise text-left" aria-label={`${garment.name} — edit`}>
      <GarmentImage
        src={garment.image_url}
        alt={garment.name}
        kind={garment.image_kind}
        className="aspect-[4/5] rounded-2xl transition-transform duration-300 group-hover:-translate-y-0.5"
      />
      <div className="mt-2.5 px-0.5">
        <p className="truncate text-sm font-medium">{garment.name}</p>
        <p className="truncate text-xs text-muted">
          {garment.colors.join(", ")} · {FORMALITY_LABEL[garment.formality]}
        </p>
      </div>
    </button>
  );
}

export function ClosetView() {
  const { wardrobe, wardrobeError, refreshWardrobe, setWardrobe } = useApp();
  const [category, setCategory] = useState<Category | "all">("all");
  const [query, setQuery] = useState("");
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<Garment | null>(null);
  const [busy, setBusy] = useState<"load" | "remove" | null>(null);
  const [notice, setNotice] = useState<{ tone: "success" | "error"; text: string } | null>(null);

  const items = useMemo(() => wardrobe ?? [], [wardrobe]);
  const counts = useMemo(() => {
    const c: Record<string, number> = { all: items.length };
    for (const g of items) c[g.category] = (c[g.category] ?? 0) + 1;
    return c;
  }, [items]);
  const visible = items.filter((g) => (category === "all" || g.category === category) && matches(g, query.trim()));
  const hasSamples = items.some((g) => g.source === "sample");

  async function loadSamples() {
    setBusy("load");
    setNotice(null);
    try {
      const res = await api.loadSampleWardrobe();
      setWardrobe(res.items);
      setNotice({
        tone: "success",
        text: res.added
          ? `Added ${res.added} sample pieces. Your own uploads are untouched.`
          : "The sample wardrobe is already loaded.",
      });
    } catch (err) {
      setNotice({ tone: "error", text: errorMessage(err) });
    } finally {
      setBusy(null);
    }
  }

  async function removeSamples() {
    setBusy("remove");
    try {
      const res = await api.removeSampleWardrobe();
      setWardrobe(res.items);
      setNotice({ tone: "success", text: "Removed the sample pieces. Your uploads stay." });
    } catch (err) {
      setNotice({ tone: "error", text: errorMessage(err) });
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-8 pt-8 sm:pt-12">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="eyebrow">Your wardrobe, digitised</p>
          <h1 className="mt-2 font-display text-4xl sm:text-5xl">My Closet</h1>
          <p className="mt-2 max-w-xl text-sm text-muted">Every outfit Rewear suggests is built only from what&apos;s here.</p>
          {items.length > 0 && (
            <p className="mt-3 inline-flex items-center gap-2 rounded-full bg-sage-soft px-3 py-1 text-xs text-forest">
              <Icon name="leaf" className="h-3.5 w-3.5" />
              {items.length} piece{items.length === 1 ? "" : "s"} ready to restyle — shop your closet before the store
            </p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {hasSamples ? (
            <Button variant="ghost" busy={busy === "remove"} onClick={removeSamples}>
              Remove sample pieces
            </Button>
          ) : (
            <Button variant="secondary" busy={busy === "load"} onClick={loadSamples}>
              Load sample wardrobe
            </Button>
          )}
          <Button variant="primary" onClick={() => setAdding(true)}>
            <Icon name="plus" className="h-4 w-4" /> Add garment
          </Button>
        </div>
      </header>

      {notice && <Banner tone={notice.tone}>{notice.text}</Banner>}
      {wardrobeError && (
        <Banner
          tone="error"
          action={
            <Button variant="ghost" onClick={() => refreshWardrobe()}>
              Retry
            </Button>
          }
        >
          {wardrobeError}
        </Banner>
      )}

      {items.length > 0 && (
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <div className="-mx-1 flex gap-1 overflow-x-auto px-1 pb-1" role="tablist" aria-label="Category">
            {(["all", ...CATEGORIES] as const).map((c) => (
              <button
                key={c}
                role="tab"
                aria-selected={category === c}
                onClick={() => setCategory(c)}
                className={`whitespace-nowrap rounded-full px-3.5 py-1.5 text-sm transition-colors ${
                  category === c ? "bg-ink text-card" : "text-ink hover:bg-well"
                }`}
              >
                {c === "all" ? "All" : CATEGORY_LABEL[c]}
                <span className="ml-1 text-xs opacity-60">{counts[c] ?? 0}</span>
              </button>
            ))}
          </div>
          <label className="relative sm:ml-auto sm:w-72">
            <span className="sr-only">Search your closet</span>
            <Icon name="search" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search colour, cut, tag…"
              className="w-full rounded-full border border-line bg-card py-2 pl-9 pr-4 text-sm outline-none focus:border-forest/60"
            />
          </label>
        </div>
      )}

      {wardrobe === null && !wardrobeError && (
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-5">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="skeleton aspect-[4/5] rounded-2xl" />
          ))}
        </div>
      )}

      {wardrobe !== null && items.length === 0 && (
        <EmptyState
          title="Your closet is empty"
          body="Photograph a few favourite pieces, or load our 20-piece sample wardrobe to try Rewear right away."
        >
          <Button variant="primary" onClick={() => setAdding(true)}>
            <Icon name="upload" className="h-4 w-4" /> Upload a garment
          </Button>
          <Button busy={busy === "load"} onClick={loadSamples}>
            Load sample wardrobe
          </Button>
        </EmptyState>
      )}

      {items.length > 0 && visible.length === 0 && (
        <p className="py-10 text-center text-sm text-muted">Nothing matches “{query}”. Try another colour or tag.</p>
      )}

      <div className="grid grid-cols-2 gap-x-5 gap-y-7 sm:grid-cols-3 lg:grid-cols-5">
        {visible.map((g) => (
          <GarmentCard key={g.id} garment={g} onClick={() => setEditing(g)} />
        ))}
      </div>

      <AddGarmentDialog open={adding} onClose={() => setAdding(false)} />
      <GarmentDrawer garment={editing} onClose={() => setEditing(null)} />
    </div>
  );
}
