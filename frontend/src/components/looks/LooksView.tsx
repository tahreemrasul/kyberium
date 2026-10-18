"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, errorMessage } from "@/lib/api";
import type { SavedLook } from "@/lib/types";
import { Banner, Button, EmptyState, GarmentImage, Icon, OCCASION_LABEL } from "../ui";

export function LooksView() {
  const [looks, setLooks] = useState<SavedLook[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    return api.listSaved().then(
      (items) => {
        setLooks(items);
        setError(null);
      },
      (err) => setError(errorMessage(err)),
    );
  }

  useEffect(() => {
    void load();
  }, []);

  async function remove(id: string) {
    try {
      await api.deleteSaved(id);
      setLooks((prev) => prev?.filter((l) => l.id !== id) ?? null);
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  const totalReused = looks?.reduce((n, l) => n + l.look.impact.owned_count, 0) ?? 0;

  return (
    <div className="space-y-8 pt-8 sm:pt-12">
      <header>
        <p className="eyebrow">Saved from the studio</p>
        <h1 className="mt-2 font-display text-4xl sm:text-5xl">My Looks</h1>
        {looks && looks.length > 0 && (
          <p className="mt-2 flex items-center gap-2 text-sm text-forest">
            <Icon name="leaf" className="h-4 w-4" />
            {looks.length} look{looks.length === 1 ? "" : "s"} built from {totalReused} pieces you already own.
          </p>
        )}
      </header>

      {error && (
        <Banner
          tone="error"
          action={
            <Button variant="ghost" onClick={load}>
              Retry
            </Button>
          }
        >
          {error}
        </Banner>
      )}

      {looks === null && !error && (
        <div className="grid gap-6 md:grid-cols-2">
          {[0, 1].map((i) => (
            <div key={i} className="skeleton h-64 rounded-3xl" />
          ))}
        </div>
      )}

      {looks?.length === 0 && (
        <EmptyState title="No saved looks yet" body="Save a recreation from the styling board to keep it here.">
          <Link href="/studio" className="rounded-full bg-forest px-5 py-2.5 text-sm font-medium text-card">
            Go to Style Studio
          </Link>
        </EmptyState>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {looks?.map((s) => (
          <article key={s.id} className="animate-rise rounded-3xl border border-line bg-card p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="font-display text-xl">{s.look.title}</h2>
                <p className="text-xs text-muted">
                  {OCCASION_LABEL[s.preferences.occasion]} · {new Date(s.created_at).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={() => remove(s.id)}
                className="rounded-full p-2 text-muted hover:bg-well hover:text-clay"
                aria-label={`Delete ${s.look.title}`}
              >
                <Icon name="trash" className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-4 flex gap-3 overflow-x-auto pb-1">
              <div className="w-24 shrink-0">
                <GarmentImage src={s.inspiration_image_url} alt="Inspiration" contain className="aspect-[4/5] rounded-xl" />
                <p className="mt-1 text-center text-[10px] uppercase tracking-wider text-muted">Inspiration</p>
              </div>
              <Icon name="arrow" className="mt-12 h-4 w-4 shrink-0 text-sage" />
              {s.look.items.map((it) => (
                <div key={it.garment_id} className="w-24 shrink-0">
                  <GarmentImage
                    src={it.garment.image_url}
                    alt={it.garment.name}
                    contain={it.garment.image_kind === "illustration"}
                    className="aspect-[4/5] rounded-xl"
                  />
                  <p className="mt-1 truncate text-[11px]">{it.garment.name}</p>
                </div>
              ))}
            </div>
            <p className="mt-3 rounded-xl bg-sage-soft px-3 py-2 text-xs text-forest">{s.look.impact.headline}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
