"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useApp } from "@/lib/store";

const LINKS = [
  { href: "/closet", label: "My Closet" },
  { href: "/studio", label: "Style Studio" },
  { href: "/looks", label: "My Looks" },
];

export function Nav() {
  const pathname = usePathname();
  const { health, wardrobe } = useApp();
  return (
    <header className="sticky top-0 z-30 border-b border-line/70 bg-paper/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 sm:px-8">
        <Link href="/" className="font-display text-2xl tracking-tight text-forest">
          Rewear
        </Link>
        <nav className="ml-auto flex items-center gap-1 sm:gap-2" aria-label="Main">
          {LINKS.map((l) => {
            const active = pathname.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                aria-current={active ? "page" : undefined}
                className={`rounded-full px-3 py-1.5 text-sm transition-colors sm:px-4 ${
                  active ? "bg-forest text-card" : "text-ink hover:bg-well"
                }`}
              >
                {l.label}
                {l.href === "/closet" && wardrobe && wardrobe.length > 0 && (
                  <span className={`ml-1.5 text-xs ${active ? "text-sage-soft" : "text-muted"}`}>{wardrobe.length}</span>
                )}
              </Link>
            );
          })}
        </nav>
        {health && !health.ai_enabled && (
          <span
            className="hidden rounded-full border border-clay/40 px-2.5 py-1 text-[11px] text-clay md:inline"
            title="Gemini isn't configured on this deployment: sample inspirations and the rule-based matcher are used."
          >
            Demo mode
          </span>
        )}
      </div>
    </header>
  );
}
