# Rewear — MVP Product & UX Handoff

**Team:** Kyberium  
**Last updated:** 14 October 2026  
**Target:** Integrated MVP by 14 October; hackathon submission by 18 October  
**Figma:** https://www.figma.com/design/cW1t6DUsCFmoZMyK32LCia  
**Tracking:** [Product scope #2](https://github.com/tahreemrasul/kyberium/issues/2) · [Wireframes #14](https://github.com/tahreemrasul/kyberium/issues/14) · [Frontend #7](https://github.com/tahreemrasul/kyberium/issues/7)

> **Status:** Working product/UX baseline. Confirm decisions with the team; implementation details below are proposed contracts, not claims of finished code.

## 1. Vision and product principles

**Rewear** is a visual, AI-powered wardrobe styling studio that turns inspiration images into creative, explainable outfits made primarily from clothes the user already owns.

- **The board is the product; chat is a secondary control.** Primary UX is structured and visual, not a chat-first interface.
- **Reuse-first by default, user choice always.** Preferences and overrides can prioritize inspiration fidelity or allow shopping.
- **Interpret the inspiration, don't merely match colors.** Preserve garment roles, silhouette, proportions, layers, occasion and mood; creatively change colors/items using owned garments.
- **Keep the reference visible.** Original inspiration is always shown beside the proposed recreation.
- **No fabricated wardrobe items.** Every “owned” suggestion must reference a real wardrobe item ID.
- **Evidence, not greenwashing.** Count existing pieces used and potential purchases avoided; don't state precise CO2/water savings or ethical ratings without verifiable evidence and a transparent methodology.

## 2. MVP feature scope

### P0 — Build for first integrated demo

1. Wardrobe gallery; upload individual clothing images; Gemini-based garment attributes; review and edit tagging before saving.
2. Preloaded demo wardrobe (approximately 15–20 items) to make the demo repeatable.
3. Inspiration image upload, replacement and preview.
4. Three basic preference categories: **occasion** (work/everyday/event/travel); **match fidelity** (very close/same aesthetic/creative); **shopping** (wardrobe first/include secondhand or rental/open to buying).
5. Multimodal inspiration parsing into outfit slots; retrieval/ranking of existing garments; 1–3 reasoned options using real wardrobe item IDs.
6. Editorial styling board: inspiration beside best recreation, other suggestions, owned-item count, actual gaps, and “why this works.”
7. Refinement: change preferences and regenerate; ideally swap one garment from existing closet.
8. Deployed accessible frontend and backend on Google Cloud/Firebase; basic error/loading states.

### P1 — After core workflow

- Contextual AI stylist chat; updates/refines the board rather than producing unrelated text.
- Curated product catalog and sourced shopping recommendations for genuine gaps.
- Simple outfit saving/history, if persistent storage is ready.
- Evaluation cases and user-facing transparency improvements.

### Out of MVP / stretch

- Live Pinterest board sync, retailer scraping, real-time rental/secondhand provider integrations, automatic garment segmentation from crowded photos, virtual try-on, drag-and-drop canvas, travel packing, precise environmental footprint, full certification scoring.

## 3. Primary user flow

```text
Open app
  ├─ Existing wardrobe → My Closet / Style Studio
  └─ New user → upload items OR load sample wardrobe
           ↓
Style Studio → upload inspiration photo
           ↓
Choose occasion, match fidelity, shopping preference
           ↓
Find my outfits
           ↓
AI parses visual garment slots, retrieves owned candidates,
validates owned IDs, composes & ranks combinations
           ↓
Results board: ORIGINAL IMAGE | CLOSET RECREATION
           ↓
Best match + alternates + explanations + owned count / genuine gaps
           ├─ Swap wardrobe piece → apply → update current recommendation
           ├─ Edit preferences → re-run, preserve form values
           ├─ Save look → save item IDs and preferences (if ready)
           └─ Explore gap → owned substitute first;
                            sourcing only if enabled and data available
```

**Edge cases:** no wardrobe → invite upload or sample; no inspiration → disable submit with explanation; model timeout → retry while preserving state; no matching closet pieces → show honest gap and suggestions, not invented garments; ambiguous image → acknowledge uncertainty or request another image.

## 4. Screens and interactions

### A. My Closet

- **Add items:** open file picker/upload modal → upload → Gemini extracts category, color, silhouette, formality and other visible tags → user reviews/edits → save → new garment card in gallery.
- **Search:** filter existing metadata as typed; no LLM needed.
- **Category tabs:** client-side filtering (All/Tops/Bottoms/Outerwear/Shoes/Accessories).
- **Garment card:** details/drawer; editable tags, replace image, delete with confirmation.
- **Sample wardrobe:** explicit action to load demo data without silently overwriting real uploads.
- **Empty state:** clear CTA to upload or explore demo.

### B. Style Studio

- **Upload / replace inspiration:** preview; remove/replace image.
- **Occasion:** single-choice selection.
- **Match fidelity:** Very close = weight color/details more; Same aesthetic = preserve structure and mood; Creative = allow broader substitutions while satisfying garment roles/occasion.
- **Shopping preference:** Wardrobe first by default; optionally enable secondhand/rental or new. This controls whether sourcing appears, not whether the outfit generation is allowed to work.
- **More preferences:** optional collapsed panel for budget/colors (defer actual enforcement unless backend supports it).
- **Find my outfits:** require inspiration and wardrobe; show progress (“Analyzing inspiration” → “Looking in your closet” → “Styling your options”); call API; render results or actionable error.
- **Back/edit:** preserve inspiration and selected preferences.

### C. Styling board / Results

- **Original reference remains visible** beside primary closet-based recreation.
- **Main card:** name, item images/slots, owned count, missing slot count, grounded explanation of preserved silhouette/structure/aesthetic, subtle reuse indicator.
- **Alternatives:** distinct matching strategies (closest recreation vs creative interpretation), not arbitrary LLM fashion generations.
- **View details:** list every garment with source inventory item ID, role and rationale.
- **Swap a piece:** open alternative-items drawer filtered to compatible items → choose an existing item → update outfit → optionally re-evaluate rationale.
- **Edit preferences:** restore Style Studio state; regenerate as requested.
- **Save look:** persist selected garment IDs/inspiration/preferences if storage available; otherwise hide rather than provide an inert control.
- **Refine with AI:** optional contextual chat drawer; must operate on selected board and wardrobe.
- **Missing item CTA:** show owned substitutes before externally sourced items. Do not promise real-time product availability unless supported.
- **Impact summary:** e.g. “4/4 pieces owned” or “1 gap”; if tracking avoided purchases, label as potential/estimated, not confirmed environmental savings.

## 5. Proposed API/data contract (confirm with backend owner)

These are interface suggestions, not implementation mandates.

```ts
type Garment = {
  id: string;
  imageUrl: string;
  category: string; // top, bottom, outerwear, shoes, etc.
  colors: string[];
  silhouette?: string;
  formality?: string;
  styleTags?: string[];
};

type StylePreferences = {
  occasion: "work" | "everyday" | "event" | "travel";
  fidelity: "close" | "aesthetic" | "creative";
  shopping: "wardrobe_first" | "secondhand_rental" | "open_to_new";
};

type InspirationSlot = {
  slot: string;
  attributes: Record<string, string | string[]>;
};

type OutfitItem = {
  slot: string;
  garmentId?: string; // existing wardrobe only; absent means unresolved gap
  reason: string;
};

type LookRecommendation = {
  id: string;
  title: string;
  items: OutfitItem[];
  unmatchedSlots: string[];
  whyItWorks: string[];
  wardrobeItemsUsed: number;
  requiredNewItems: number; // do not assert a purchase occurred
};
```

Potential endpoints: `POST /wardrobe/items/analyze`, `POST /wardrobe/items`, `GET /wardrobe/items`, `POST /inspiration/analyze`, `POST /looks/generate`, `POST /looks/refine` (optional). Agree on error envelopes and upload strategy before parallel implementation.

**Model pipeline:** wardrobe tagging → inspiration slot extraction → candidate retrieval/attribute comparison → whole-outfit reasoning → ID validation / gap assessment → ranked looks and explanations. Use model calls only where reasoning is useful; filter/search inventory deterministically.

## 6. UI direction

- Minimal editorial fashion studio: cream/off-white backgrounds, forest/sage green accents, restrained warm orange for occasional emphasis.
- Large real imagery with generous whitespace; avoid dense analytics dashboard, excessive badges or multiple competing primary buttons.
- Three navigation destinations: **My Closet**, **Style Studio**, **My Looks**. Results can live within Studio; My Looks stores previously saved looks once persistence is ready.
- For hackathon, prioritize responsive desktop and a usable mobile layout.
- Real garment photography and simple garment compositions should represent actual inventory; AI-generated fashion photos must not falsely depict owned items.

## 7. Acceptance tests

- Can upload/confirm one wardrobe garment and see it in My Closet.
- Can load sample wardrobe and upload an inspiration image.
- Can select/change all three basic preferences.
- Can generate at least one real item-ID-grounded recommendation.
- Original inspiration and recommended owned garments are visible simultaneously.
- Exact and creative matches produce explainable, meaningfully different alternatives when inventory permits.
- With no match, app exposes genuine gap instead of pretending to own the reference item.
- With shopping disabled, no new item is quietly introduced.
- Failed network/model calls preserve inputs and offer retry.
- Public deployment works without the developer’s local credentials.

## 8. Remaining design work / ownership

- [ ] Team sign-off on MVP scope and feature boundaries — #2
- [ ] Design upload → AI tagging review modal — #14
- [ ] Design garment details/edit state — #14
- [ ] Design results → swap-item drawer and optional missing-item panel — #14
- [ ] Add loading, empty, error and mobile states — #14
- [ ] Connect a clickable Figma prototype where helpful — #14
- [ ] Finalize shared API contract with backend/frontend owners — #3
- [ ] Implement UI — #7
- [ ] Integrate actual model responses — #8
- [ ] Deploy — #9
- [ ] Verify with curated sample wardrobe and cases — #10, #12
- [ ] Submission deck and demo video — #13

## 9. Links

- [Editable Figma UX wireframes](https://www.figma.com/design/cW1t6DUsCFmoZMyK32LCia)
- [GitHub implementation issues](https://github.com/tahreemrasul/kyberium/issues)

**Source of truth rule:** this Markdown file describes behavior and scope; Figma defines visual arrangement; GitHub Issues track implementation and ownership. If they conflict, resolve in the team and update the handoff.
