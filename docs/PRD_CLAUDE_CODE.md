# Rewear — Product Requirements Document for Claude Code
**Team:** Kyberium | **Version:** 1.0 | **Updated:** 2026-10-16 | **Hackathon submission:** 2026-10-18

## Critical orientation for implementation
The primary product is **a visual sustainable fashion styling board, not a generic chatbot**. Preserve the initial inspiration alongside creative, grounded outfit recreations using the user's own garment inventory. Default to reuse, allow user overrides, and show real wardrobe gaps. The app must be deployed and demoable. **Do not claim work is implemented until verified.**

**Repository:** https://github.com/tahreemrasul/kyberium  
**Existing UX document:** [MVP_UX_HANDOFF.md](./MVP_UX_HANDOFF.md)  
**Editable wireframes:** https://www.figma.com/design/cW1t6DUsCFmoZMyK32LCia  
**GitHub issues:** https://github.com/tahreemrasul/kyberium/issues  
**Repo status when PRD written:** main has only prior documentation commit; no implementation PRs or feature branches found via connected GitHub search on 2026-10-16. Check again at start of your session; teammates may have unpushed local work.

## 1. Objective and success criteria
Users upload garments (or select demo wardrobe), upload an inspiration outfit, select concise preferences, and receive 1–3 creative outfit suggestions composed **only of actual owned items** unless additions are explicitly identified as external suggestions. The AI explains preserved silhouette, proportions, occasion and style, notes where the colors/garments differ, and recommends *not buying* when ownership suffices.

A successful hackathon demo in under three minutes shows:
1. Load a curated sample closet, or upload and tag an item.
2. Upload an inspiration photo.
3. Choose occasion, match flexibility, shopping preference.
4. Generate a recommendation grounded in inventory, with original inspiration side by side.
5. Compare close recreation with creative alternative; understand why each works.
6. Optionally swap an item and show the updated board; show 100%-owned/no-purchase-needed or genuine gaps.
7. Open a public working deployment. PDF proposal + public 3-minute demo video are separate submission requirements.

### Non-negotiable quality conditions
- No fabricated owned-item IDs, products, retailer stock levels, brand certifications or quantified carbon/water savings.
- No AI-generated fashion model photograph passed off as the user's real garments; display original garment photos/flat lays.
- Explain substitutions and preserve inspiration image in results.
- Server-side Gemini/Vertex AI keys and auth only.
- Real uploads + preloaded demo fixture; predictable fallback/error/retry UX; mobile-friendly.
- **Reuse-first by default, user choice always.** Do not forcibly block shopping or override occasion requirements.

## 2. Personas and problem
Primary persona: a conference traveler/professional who often buys clothes for events despite owning many suitable items. Secondary: style-conscious users with inspiration boards who want creative new combinations and a way to shop intentionally.
Pain: fragmented wardrobe awareness; inspiration-to-purchase impulse; lack of styling creativity and visibility into reuse possibilities.
Differentiation vs digital closet catalog tools: **deconstruct inspiration → retrieve wardrobe pieces → reconstruct compelling outfits → justify any acquisition.**

## 3. Scope and priorities (two-day remaining window)
### P0 — Make functional and deploy first
- My Closet: browse sample and uploaded garments; image upload → Gemini structured analysis → review/edit tags → persist.
- Style Studio: image upload, occasion, match fidelity, shopping preference.
- Results board: reference inspiration beside closest recreation and creative alternative; grounded item photos, explanation, owned count, unmatched slots.
- Matching pipeline with real inventory IDs and genuine gap decisions.
- One easy refinement path: change preferences and regenerate, OR simple swap owned garment.
- Deployed application with persistent enough data/demo experience to survive reload; loading/empty/error states.
- Representative test cases and security configuration.

### P1 — Only after deployed P0 passes
- Save looks/My Looks persistent page, if backend ready.
- Contextual chat that operates on current wardrobe + selected look and returns structured changes.
- Small curated ethical/retail information with real source links; no unsupported ratings.
- Sourced secondhand/rental alternatives where actual data is legally available.

### Out of scope for the deadline
Live Pinterest authentication, Vogue scraping, crawling retailer sites, complex vector database, drag-and-drop canvas, virtual try-on, bulk item segmentation, travel packing planner, precise CO2/water figures, broad autonomous tool loops.

## 4. UI/UX details
Design style: **calm editorial fashion studio** — cream background, muted sage/forest green, rare orange accents, whitespace, large real garment images, low badge/button density. The core visual payoff is **inspiration → rediscovery of owned clothes**, not generic fashion photos.
Navigation: **My Closet**, **Style Studio**, **My Looks** (My Looks can be gated until saved looks implemented). Results appear within Style Studio or its focused subview.

### My Closet
- Load demo data CTA; do not overwrite users' items unexpectedly.
- Add items: pick image(s), show preview, asynchronous AI attribute extraction, review/edit extracted category, colors, silhouette, material *appearance only*, style/formality; confirm/save; card appears.
- Card click opens edit/details; search/filter by category/tags (deterministic).
- Empty state and errors with retry.

### Style Studio
- Upload original inspiration image; preview/remove/replace.
- Required selections with defaults:
  - occasion: work, everyday, event, travel;
  - fidelity: close, aesthetic (default), creative;
  - shopping: wardrobe_first (default), secondhand_rental, open_to_new.
- On Find my outfits: validate inspiration and wardrobe; progress states analyzing → searching closet → composing.
- Preserve input state on back, failure and retries; advanced options hidden until working.

### Result board
- Inspiration image remains visible alongside selected recommendation.
- Show recommended outfit built from actual owned garment images and slot labels; don't generate misleading photorealistic worn-outfit composites.
- Two strategies ideally visible: **Closest recreation** and **Creative remix**. Third only if distinct and high-quality.
- Why this works: explicit silhouette/layering/occasion and acknowledged deviations.
- Owned count e.g. 3/4; missing slots; no-purchase-needed when applicable.
- Swap a piece: eligible owned alternatives only; update outfit and explanation. If time short, make preference adjustment + regenerate the safe fallback.
- If genuine gaps: show available owned substitutes first, and only sourced purchase links when permitted by shopping preference and actual data.
- Optional Save Look and contextual chat drawer are P1, not decorative fake controls.
- Mobile layouts stack inspiration/results panels vertically.

## 5. Detailed AI pipeline
### Step A: garment cataloging
Input: one uploaded garment image. Output: Pydantic-validated typed metadata: category/slot, colors, cut/silhouette, patterns, approximate formality, possible layers, styleTags, low-confidence fields. **Do not assert exact fabric/composition, sustainability certification or brand from visual appearance.** User confirmation takes precedence.

### Step B: inspiration analysis
Parse visible clothing slots with colors, silhouettes, proportions, layering, occasion and overall aesthetic. Mark occlusions/ambiguity honestly. Keep the original image.

### Step C: retrieval/ranking
Use deterministic slot filters and category compatibility first; optional lightweight local similarity/embeddings as tie-breaker. Rank silhouette, garment roles/layering, occasion/formality and color/style, modulated by user fidelity setting. The demo wardrobe is small; don't add vector DB unless a measured need exists. No uncalibrated probability/confidence percentages.

### Step D: outfit composition
Use Gemini to reason across combinations shortlisted from existing garment IDs. Generate 1–3 distinct alternatives with explanations. A second validation step rejects IDs absent from the user inventory, duplicate incompatible slots and breached hard constraints. Make a reasoned 'no suitable match' instead of hallucinating a piece.

### Step E: sustainability reasoning
Compare viable looks prioritizing owned garments; clearly label optional new purchases and unmatched slots. Show reuse count, possible purchases avoided (estimate), garment versatility when it can be calculated from saved outfits/inventory. Never invent precise impact statistics.

### Step F: refinement
Structured request e.g. 'more formal', 'swap trousers', 'keep the blazer'; translate into updated preferences/constraints and reuse same wardrobe IDs. Can be future chat drawer.

## 6. Data shapes (adapt as actual backend warrants)
```ts
type Garment = {
  id: string;
  imageUrl: string;
  category: "top" | "bottom" | "outerwear" | "dress" | "shoes" | "accessory";
  colors: string[];
  silhouette?: string;
  pattern?: string;
  formality?: "casual" | "smart_casual" | "formal";
  styleTags: string[];
  verifiedByUser: boolean;
};
type Preferences = {
  occasion: "work" | "everyday" | "event" | "travel";
  fidelity: "close" | "aesthetic" | "creative";
  shopping: "wardrobe_first" | "secondhand_rental" | "open_to_new";
};
type OutfitSlot = {
  slot: string;
  sourceDescription: string;
  garmentId: string | null; // only real wardrobe ID; null means missing
  explanation: string;
};
type RecommendedLook = {
  id: string;
  strategy: "closest" | "creative" | "other";
  title: string;
  slots: OutfitSlot[];
  whyItWorks: string[];
  unmatchedSlots: string[];
  ownedItems: number;
  optionalPurchaseCount: number;
};
```
Store ownership associations (userId/demoId), source image references, creation timestamps, and IDs. Never take a client-submitted item ID as authorization to read another user's wardrobe.

### Proposed API (reconcile with existing code)
- `GET /health`
- `GET /wardrobe/items`
- `POST /wardrobe/items/analyze` (image upload → structured draft)
- `POST /wardrobe/items` (confirmed metadata → persist)
- `POST /looks/generate` (inspiration + preferences + known wardrobe)
- `POST /looks/refine` (stretch)
- `GET /demo/load` or explicit demo reset/seed action (careful with mutability)

HTTP responses should use consistent error envelopes and strict schemas; instrument model latency, retries, failures, and request cost when practical.

## 7. Architecture and deployment
Recommended (adapt existing project instead of rewriting):
- Next.js / TypeScript frontend; responsive layouts with typed client.
- Python FastAPI backend; Pydantic structured outputs; Google Gen AI SDK configured for Vertex AI with service-account / workload identity.
- Firebase/Firestore for garment metadata and Cloud Storage for uploaded images; alternatively lightweight persistence if faster and secure.
- Cloud Run for API, frontend on Firebase App Hosting or Cloud Run.
- Cloud credentials/Google project info from environment; no secrets in repo; provide `.env.example`.
- Budget guards, max image size/type validation, timeouts/retries and model error handling.
- Deployment URL and reproducible instructions required; don't postpone deployment to the final hours.

Engineering guidance: prefer one orchestrated pipeline and tool functions to a theatrical multiagent architecture. Cache the garment tags. Keep prompt templates and response schemas versioned and tested. Implement mock-data fallback only as an explicitly labeled demo fallback, not a secretly fabricated live AI response.

## 8. Optional fashion-knowledge retrieval (POST-MVP R&D)
**Hypothesis:** Style principles retrieval might improve creative substitutions: color harmony, balanced proportions, dress-code guidelines, garment versatility, layering and occasion-driven adaptations.

**Do not scrape Vogue, Vogue Business or similar sources without permission.** Condé Nast terms explicitly prohibit automated harvesting/indexing in relevant contexts, including some AI uses. See:
- https://www.voguebusiness.com/about/vogue-business-terms-of-service
- https://www.vogue.de/info/impressum

Instead, prototype with 20–50 **original, team-authored styling knowledge cards** or properly licensed/open material after checking terms. Example record:
```json
{
  "id": "styling-014",
  "concept": "visual balance with oversized blazer",
  "principle": "Balance a boxy top layer with a more defined lower silhouette or a deliberate wide-leg proportion.",
  "when_to_use": ["work", "smart_casual"],
  "tags": ["silhouette", "proportion", "blazer"],
  "source_type": "original",
  "source_url": null
}
```
Start with tag-based retrieval or a small local embedding index and evaluate against a no-retrieval baseline. Add pgvector/Vertex AI Vector Search only if demonstrably useful and legally sourced. Store provenance/license and show citations for external claims.

This is **different from wardrobe retrieval**: fashion knowledge describes principles; wardrobe retrieval identifies real owned garments. Do not contaminate one with unsupported inventory guesses.


## 8A. Future fashion-knowledge retrieval contract (IMPLEMENT INTERFACE NOW; INDEX COMES LATER)

A separate research/data workstream will gather legally usable fashion styling knowledge and construct a substantial searchable index. **Claude Code must not scrape publications, build the full index, or block MVP development waiting for it.** Treat this as an optional, replaceable dependency of outfit reasoning.

### Required integration seam
Implement a small `FashionKnowledgeRetriever` abstraction with an async `search(query, filters, topK)` method. Return typed `FashionKnowledgeHit` records:
```ts
type FashionKnowledgeQuery = {
  concepts: string[];              // silhouette, proportion, layering, palette, formality
  occasion?: string;
  garmentCategories?: string[];
  styleTags?: string[];
  topK?: number;
};
type FashionKnowledgeHit = {
  id: string;
  text: string;                    // concise styling principle, not an unsupported assertion
  score?: number;                  // ranking value, not a probability of correctness
  tags: string[];
  sourceTitle?: string;
  sourceUrl?: string;
  license?: string;
  provenance?: string;
};
```
Adapt naming to the actual language/backend (Pydantic in Python recommended), but preserve the semantics.

### Implementations
- `NoOpFashionKnowledgeRetriever`: default for initial deployed MVP, returns [] safely.
- `LocalFashionKnowledgeRetriever`: optional implementation for a small curated JSON dataset, tag/keyword match.
- `VectorFashionKnowledgeRetriever`: future adapter for chosen store (pgvector, Qdrant, Vertex AI Vector Search, etc.); **do not couple business logic to a vector database provider yet**.

### Execution and failure behavior
1. After inspiration parsing, generate retrieval queries from outfit attributes, not a raw image blob. Keep query focused on the styling decisions the agent is making.
2. Optionally retrieve a few short, relevant styling principles (e.g. 3–5) before final outfit composition; cap token budget.
3. If unconfigured, empty, slow or failing, run the **same core wardrobe-matching workflow** with no fashion hits. Fashion retrieval must never be required for garment ingestion, wardrobe lookup, or generation.
4. Include source IDs/URLs as metadata with any retrieved principles and never fabricate citations.
5. Store the source dataset's attribution, license and URL and enforce permitted use. Deep research can help locate knowledge, but research results are not themselves proof of indexing/reproduction rights.
6. Provide a configuration flag (e.g. `FASHION_KNOWLEDGE_BACKEND=none|local|vector`) and a dedicated retriever module. Unit test both retrieved and empty/error paths.
7. Keep retrieved styling principles **separate from wardrobe inventory records**. The knowledge index cannot create new “owned” garments.
8. Future vector infrastructure will be wired in via configuration, not through changes to endpoint contracts or frontend screens.

**Acceptance criterion for current implementation:** the styling pipeline imports the retriever interface, continues to work with the no-op implementation, and can consume a list of knowledge hits when supplied by a test double. Full-scale indexing is intentionally deferred.

## 9. Testing & evaluation
Create 10–15 labeled cases, with owned IDs and expected outfit constraints:
- exact piece match; same silhouette different color; creative but context-appropriate substitution;
- no plausible substitute; missing outerwear; layered outfit; ambiguous photos;
- very-close vs creative preferences; shopping disabled; work formality;
- invalid garment ID hallucination; malformed model response; request timeout; empty wardrobe.

Track:
- output schema validity;
- percentage of selected garment IDs existing in user inventory (**target 100%**);
- correct slot assignments;
- occasion and preference adherence;
- distinctness and explanation quality, human-reviewed;
- percentage of scenarios resolved with no purchase (descriptive, not gamed);
- end-to-end demo latency and error behavior.

Add unit tests for deterministic filters, response validation and APIs; a scripted happy-path browser or API smoke test if feasible.

## 10. Implementation order, coordination & PR process
**First task:** inspect actual repo, issues, recent PRs and branch changes. Do not overwrite teammates' work; notify if conflicts/unclear ownership. Check dependencies and agree on shared contracts.
1. Scaffold and deploy a simple, working skeleton **immediately**.
2. Seed curated demo items and integrate storage/upload.
3. Implement structured Gemini garment/inspiration interpretation.
4. Implement deterministic inventory candidate retrieval + AI outfit composer.
5. Integrate Style Studio UI and results board.
6. Run smoke tests of public deployment, polish errors/mobile, then stretch.
7. Record reproducible 3-minute demo; prepare PDF submission.

Use a feature branch and small reviewable commits/PRs, link GitHub issues. Avoid changing teammates' code unnecessarily.

**Issue references:**
- Product scope #2; API foundation #3; upload/tagging #4; inspiration #5; matching #6; frontend #7; integration #8; deployment #9; sample data #10; sustainability #11; evaluation #12; submission #13; UX wireframes #14.

## 11. Claude Code execution request
Read this PRD, existing `docs/MVP_UX_HANDOFF.md`, open issues, and inspect the repository. Report current implementation state, choose the smallest viable architecture, identify dependencies and likely conflicts, then **implement the core user journey** with production-minded tests. Use Google Gemini on Vertex AI, but keep a clearly labeled demo mode if cloud credentials are missing. Ensure the app can be deployed on supported Google Cloud hosting. Document setup commands, required environment variables, test results, deployment steps, limitations and remaining tasks. Do not stop at a plan or a UI mockup: build executable code, run tests and prepare a PR. No undocumented scraping and no fabricated sustainability measurements.
