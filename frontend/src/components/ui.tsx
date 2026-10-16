"use client";

import { useEffect, useRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { mediaUrl } from "@/lib/api";
import type { Category, Fidelity, Formality, Occasion, Shopping } from "@/lib/types";

// ---------------------------------------------------------------------------
// Labels
// ---------------------------------------------------------------------------

export const CATEGORY_LABEL: Record<Category, string> = {
  top: "Tops",
  bottom: "Bottoms",
  outerwear: "Outerwear",
  dress: "Dresses",
  shoes: "Shoes",
  accessory: "Accessories",
};
export const CATEGORY_SINGULAR: Record<Category, string> = {
  top: "Top",
  bottom: "Bottom",
  outerwear: "Outerwear",
  dress: "Dress",
  shoes: "Shoes",
  accessory: "Accessory",
};
export const FORMALITY_LABEL: Record<Formality, string> = {
  casual: "Casual",
  smart_casual: "Smart casual",
  formal: "Formal",
};
export const OCCASION_LABEL: Record<Occasion, string> = {
  work: "Work / conference",
  everyday: "Everyday",
  event: "Special event",
  travel: "Travel",
};
export const FIDELITY_LABEL: Record<Fidelity, { label: string; hint: string }> = {
  close: { label: "Very close", hint: "Similar pieces, cuts and colours" },
  aesthetic: { label: "Same aesthetic", hint: "Keep the mood, flex colours and pieces" },
  creative: { label: "Creative", hint: "Broader remixes that keep each role" },
};
export const SHOPPING_LABEL: Record<Shopping, { label: string; hint: string }> = {
  wardrobe_first: { label: "My wardrobe first", hint: "Only what I own" },
  secondhand_rental: { label: "Secondhand / rental", hint: "Suggest pre-loved ideas for gaps" },
  open_to_new: { label: "Open to new", hint: "Suggest buying ideas for gaps" },
};

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

type Variant = "primary" | "secondary" | "ghost" | "danger";

export function Button({
  variant = "secondary",
  busy,
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; busy?: boolean }) {
  const styles: Record<Variant, string> = {
    primary: "bg-forest text-card hover:bg-forest-2 disabled:bg-forest/40",
    secondary: "border border-line bg-card text-ink hover:border-forest/40 disabled:opacity-50",
    ghost: "text-forest hover:bg-sage-soft/60 disabled:opacity-40",
    danger: "border border-clay/40 text-clay hover:bg-clay-soft disabled:opacity-50",
  };
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium transition-colors disabled:cursor-not-allowed ${styles[variant]} ${className}`}
      disabled={busy || props.disabled}
      aria-busy={busy || undefined}
      {...props}
    >
      {busy && <Spinner className="h-4 w-4" />}
      {children}
    </button>
  );
}

export function Chip({
  selected,
  onClick,
  children,
  title,
}: {
  selected: boolean;
  onClick: () => void;
  children: ReactNode;
  title?: string;
}) {
  return (
    <button
      type="button"
      title={title}
      aria-pressed={selected}
      onClick={onClick}
      className={`rounded-full border px-3.5 py-1.5 text-sm transition-colors ${
        selected ? "border-forest bg-forest text-card" : "border-line bg-card text-ink hover:border-forest/40"
      }`}
    >
      {children}
    </button>
  );
}

export function ChipGroup<T extends string>({
  label,
  options,
  value,
  onChange,
  hint,
}: {
  label: string;
  options: { value: T; label: string; hint?: string }[];
  value: T;
  onChange: (v: T) => void;
  hint?: string;
}) {
  const current = options.find((o) => o.value === value);
  return (
    <fieldset className="space-y-2">
      <legend className="eyebrow">{label}</legend>
      <div className="flex flex-wrap gap-2" role="group" aria-label={label}>
        {options.map((o) => (
          <Chip key={o.value} selected={o.value === value} onClick={() => onChange(o.value)} title={o.hint}>
            {o.label}
          </Chip>
        ))}
      </div>
      {(current?.hint || hint) && <p className="text-xs text-muted">{current?.hint ?? hint}</p>}
    </fieldset>
  );
}

export function Spinner({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.2" strokeWidth="3" />
      <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export function Banner({
  tone = "info",
  children,
  action,
}: {
  tone?: "info" | "error" | "success";
  children: ReactNode;
  action?: ReactNode;
}) {
  const tones = {
    info: "border-line bg-card text-ink",
    error: "border-clay/40 bg-clay-soft/60 text-ink",
    success: "border-sage bg-sage-soft/70 text-forest",
  };
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={`flex flex-wrap items-center gap-3 rounded-2xl border px-4 py-3 text-sm ${tones[tone]}`}
    >
      <div className="min-w-0 flex-1">{children}</div>
      {action}
    </div>
  );
}

/** Garment/inspiration image. Illustrations are labelled so they're never mistaken for photos. */
export function GarmentImage({
  src,
  alt,
  kind = "photo",
  className = "",
  contain = false,
}: {
  src: string;
  alt: string;
  kind?: "photo" | "illustration";
  className?: string;
  contain?: boolean;
}) {
  return (
    <div className={`relative overflow-hidden bg-well ${className}`}>
      {/* eslint-disable-next-line @next/next/no-img-element -- user uploads are served by the API */}
      <img
        src={mediaUrl(src)}
        alt={alt}
        loading="lazy"
        className={`h-full w-full ${contain || kind === "illustration" ? "object-contain p-[6%]" : "object-cover"}`}
      />
      {kind === "illustration" && (
        <span className="absolute bottom-2 left-2 rounded-full bg-card/85 px-2 py-0.5 text-[10px] tracking-wide text-muted">
          sample illustration
        </span>
      )}
    </div>
  );
}

export function Dialog({
  open,
  onClose,
  title,
  children,
  side = false,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  side?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    if (!open && el.open) el.close();
  }, [open]);
  return (
    <dialog
      ref={ref}
      onClose={onClose}
      onClick={(e) => e.target === ref.current && onClose()}
      aria-label={title}
      className={`m-0 max-h-none max-w-none bg-transparent p-0 backdrop:bg-ink/30 backdrop:backdrop-blur-[2px] ${
        side ? "ml-auto h-full w-full sm:w-[440px]" : "mx-auto my-auto w-full max-w-2xl px-3"
      }`}
    >
      <div className={`flex flex-col bg-paper shadow-2xl ${side ? "h-full" : "max-h-[90vh] rounded-3xl"} animate-rise`}>
        <div className="flex items-center justify-between border-b border-line/80 px-6 py-4">
          <h2 className="font-display text-xl">{title}</h2>
          <button onClick={onClose} className="rounded-full p-2 text-muted hover:bg-well" aria-label="Close">
            <Icon name="x" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-5">{children}</div>
      </div>
    </dialog>
  );
}

export function EmptyState({ title, body, children }: { title: string; body: string; children?: ReactNode }) {
  return (
    <div className="flex flex-col items-center rounded-3xl border border-dashed border-line bg-card/60 px-6 py-16 text-center">
      <Icon name="hanger" className="h-10 w-10 text-sage" />
      <h3 className="mt-4 font-display text-2xl">{title}</h3>
      <p className="mt-2 max-w-md text-sm text-muted">{body}</p>
      {children && <div className="mt-6 flex flex-wrap justify-center gap-3">{children}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Icons (inline, stroke-based)
// ---------------------------------------------------------------------------

const PATHS: Record<string, ReactNode> = {
  x: <path d="M6 6l12 12M18 6L6 18" />,
  plus: <path d="M12 5v14M5 12h14" />,
  upload: (
    <>
      <path d="M12 16V4M7 9l5-5 5 5" />
      <path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </>
  ),
  leaf: (
    <>
      <path d="M5 19c0-8 5-13 14-14 0 9-5 14-13 14" />
      <path d="M5 19l7-7" />
    </>
  ),
  swap: <path d="M7 7h11l-3-3M17 17H6l3 3" />,
  arrow: <path d="M4 12h15M14 6l6 6-6 6" />,
  sparkle: <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z" />,
  check: <path d="M5 12.5l4.5 4.5L19 7" />,
  trash: <path d="M5 7h14M10 7V4h4v3M7 7l1 13h8l1-13" />,
  bookmark: <path d="M7 4h10v16l-5-4-5 4z" />,
  refresh: <path d="M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7" />,
  edit: <path d="M4 20h4L19 9l-4-4L4 16v4z" />,
  hanger: (
    <>
      <path d="M12 7a2 2 0 1 1 2-2" />
      <path d="M12 7v1.5L3 15h18l-9-6.5" />
    </>
  ),
  alert: (
    <>
      <path d="M12 8v5M12 16.5v.5" />
      <circle cx="12" cy="12" r="9" />
    </>
  ),
};

export function Icon({ name, className = "h-5 w-5" }: { name: string; className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      {PATHS[name]}
    </svg>
  );
}
