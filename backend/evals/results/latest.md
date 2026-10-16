# Rewear evaluation — offline (rule-based composer + injected model outputs)

- Cases passed: **14/14**
- Checks passed: **70/70**
- Owned-garment validity: every returned garment id is checked per case (target 100%).
- Looks needing no purchase: 20/23 (descriptive, not a target)

Checks are deterministic. Candidate `score` values are heuristic ranking signals, not calibrated probabilities, and are never shown to users as confidence.

| Case | Result | Failed checks | Latency |
|---|---|---|---|
| exact-camel-work | PASS | — | 16 ms |
| same-silhouette-different-colour | PASS | — | 10 ms |
| aesthetic-substitute-weekend | PASS | — | 9 ms |
| category-substitute-dress | PASS | — | 5 ms |
| multiple-substitutes-distinct | PASS | — | 11 ms |
| missing-item-optional | PASS | — | 10 ms |
| missing-key-piece | PASS | — | 5 ms |
| formal-occasion-constraint | PASS | — | 6 ms |
| shopping-disabled | PASS | — | 10 ms |
| user-exclusion-and-keep | PASS | — | 10 ms |
| ambiguous-not-an-outfit | PASS | — | 0 ms |
| hallucinated-ids | PASS | — | 9 ms |
| malformed-model-output | PASS | — | 11 ms |
| empty-wardrobe | PASS | — | 0 ms |

## Looks for human review

### exact-camel-work

_Exact garment matches: every key piece of the camel work look is owned._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Camel oversized blazer: Your camel oversized blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); similar silhouette (oversized, relaxed single-breasted).
- top-1 <- White crew-neck tee: Your white crew-neck tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Black straight-leg trousers: Your black straight-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); similar silhouette (straight-leg, high-rise).
- shoes-1 <- Brown leather loafers: Your brown leather loafers can stand in for the brown leather penny loafers — same garment type (flats); similar silhouette (classic penny loafer).
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

**Creative remix** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: Your sage tailored blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); similar silhouette (tailored, relaxed shoulders).
- top-1 <- Navy Breton striped tee: Your navy breton striped tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Ecru wide-leg trousers: Your ecru wide-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); matching formality (smart casual).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the brown leather penny loafers — matching formality (smart casual); shared style: classic.
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

### same-silhouette-different-colour

_Camel blazer removed: a blazer with the same structure in another colour should replace it._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: Your sage tailored blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); similar silhouette (tailored, relaxed shoulders).
- top-1 <- White crew-neck tee: Your white crew-neck tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Black straight-leg trousers: Your black straight-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); similar silhouette (straight-leg, high-rise).
- shoes-1 <- Brown leather loafers: Your brown leather loafers can stand in for the brown leather penny loafers — same garment type (flats); similar silhouette (classic penny loafer).
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

**Creative remix** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Black fitted blazer: Your black fitted blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); shared style: tailored.
- top-1 <- Navy Breton striped tee: Your navy breton striped tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Ecru wide-leg trousers: Your ecru wide-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); matching formality (smart casual).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the brown leather penny loafers — matching formality (smart casual); shared style: classic.
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

### aesthetic-substitute-weekend

_No olive overshirt owned: another casual outer layer takes its role._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 4/4 pieces already in your closet · No new purchase needed

- outerwear-1 <- Light-wash denim jacket: Your light-wash denim jacket can stand in for the olive cotton utility overshirt — same garment type (jacket); similar silhouette (boxy, cropped).
- top-1 <- Cream cable-knit cardigan: Your cream cable-knit cardigan can stand in for the cream crew-neck knit sweater — same garment type (knit); similar silhouette (relaxed, button-front).
- bottom-1 <- Mid-wash straight jeans: Your mid-wash straight jeans can stand in for the light-wash straight-leg jeans — same garment type (jeans); similar silhouette (straight-leg, high-rise).
- shoes-1 <- White leather sneakers: Your white leather sneakers can stand in for the white low-top sneakers — same garment type (sneakers); same colour family (white).

**Creative remix** — 4/4 pieces already in your closet · No new purchase needed

- outerwear-1 <- Cream cable-knit cardigan: Your cream cable-knit cardigan can stand in for the olive cotton utility overshirt — similar silhouette (relaxed, button-front); matching formality (casual).
- top-1 <- Rust ribbed sweater: Your rust ribbed sweater can stand in for the cream crew-neck knit sweater — same garment type (knit); similar silhouette (relaxed, crew neck).
- bottom-1 <- Black straight-leg trousers: Your black straight-leg trousers can stand in for the light-wash straight-leg jeans — similar silhouette (straight-leg, high-rise); shared style: classic.
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the white low-top sneakers — suits everyday.

### category-substitute-dress

_Matching aesthetic with different categories: slip dress recreated by a top + skirt two-piece._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Black fitted blazer: Your black fitted blazer can stand in for the black cropped leather biker jacket — same colour family (black); suits event.
- dress-1 <- Black silk-look camisole: Your black silk-look camisole can stand in for the emerald satin bias-cut slip dress — shared style: evening, sleek; suits event.
- dress-1 <- Champagne satin midi skirt: Your champagne satin midi skirt can stand in for the emerald satin bias-cut slip dress — similar silhouette (bias-cut midi, fluid); shared style: evening, sleek.
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the black strappy heeled sandals — same colour family (black); shared style: evening, sleek.
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Gold hoop earrings.

**Creative remix** — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Camel oversized blazer: Your camel oversized blazer can stand in for the black cropped leather biker jacket — matching formality (smart casual); suits event.
- dress-1 <- Black silk-look camisole: Your black silk-look camisole can stand in for the emerald satin bias-cut slip dress — shared style: evening, sleek; suits event.
- dress-1 <- Champagne satin midi skirt: Your champagne satin midi skirt can stand in for the emerald satin bias-cut slip dress — similar silhouette (bias-cut midi, fluid); shared style: evening, sleek.
- shoes-1 <- Brown leather loafers: Your brown leather loafers can stand in for the black strappy heeled sandals — it fills the same role in the outfit.
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Gold hoop earrings.

### multiple-substitutes-distinct

_Several reasonable substitutes: closest and creative looks must differ._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Camel oversized blazer: Your camel oversized blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); similar silhouette (oversized, relaxed single-breasted).
- top-1 <- White crew-neck tee: Your white crew-neck tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Black straight-leg trousers: Your black straight-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); similar silhouette (straight-leg, high-rise).
- shoes-1 <- Brown leather loafers: Your brown leather loafers can stand in for the brown leather penny loafers — same garment type (flats); similar silhouette (classic penny loafer).
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

**Creative remix** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: Your sage tailored blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); similar silhouette (tailored, relaxed shoulders).
- top-1 <- Navy Breton striped tee: Your navy breton striped tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Ecru wide-leg trousers: Your ecru wide-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); matching formality (smart casual).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the brown leather penny loafers — matching formality (smart casual); shared style: classic.
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

### missing-item-optional

_Missing wardrobe item: no hat owned; it must be an optional gap, never an invented garment._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Camel oversized blazer: Your camel oversized blazer can stand in for the beige belted double-breasted trench coat — same colour family (beige); matching formality (smart casual).
- top-1 <- Navy fine-knit sweater: Your navy fine-knit sweater can stand in for the navy fine-knit crew-neck sweater — same garment type (knit); similar silhouette (slim, crew neck).
- bottom-1 <- Ecru wide-leg trousers: Your ecru wide-leg trousers can stand in for the ecru high-rise wide-leg trousers — same garment type (trousers); similar silhouette (high-rise wide-leg).
- shoes-1 <- White leather sneakers: Your white leather sneakers can stand in for the white minimal sneakers — same garment type (sneakers); same colour family (white).
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Wide-brim straw-coloured hat.

**Creative remix** — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Black fitted blazer: Your black fitted blazer can stand in for the beige belted double-breasted trench coat — shared style: classic.
- top-1 <- Black silk-look camisole: Your black silk-look camisole can stand in for the navy fine-knit crew-neck sweater — similar silhouette (slim, bias-cut); matching formality (smart casual).
- bottom-1 <- Black straight-leg trousers: Your black straight-leg trousers can stand in for the ecru high-rise wide-leg trousers — same garment type (trousers); matching formality (smart casual).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the white minimal sneakers — suits travel.
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Wide-brim straw-coloured hat.

### missing-key-piece

_Genuine gap: closet without any outer layer must report an essential outerwear gap._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 3/5 inspiration pieces from your closet · 1 wardrobe gap

- top-1 <- White crew-neck tee: Your white crew-neck tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Black straight-leg trousers: Your black straight-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); similar silhouette (straight-leg, high-rise).
- shoes-1 <- Brown leather loafers: Your brown leather loafers can stand in for the brown leather penny loafers — same garment type (flats); similar silhouette (classic penny loafer).
- GAP outerwear-1 (essential): Nothing in your closet fills the role of the Camel oversized single-breasted blazer.
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Tan structured tote bag.

**Creative remix** — 3/5 inspiration pieces from your closet · 1 wardrobe gap

- top-1 <- Navy Breton striped tee: Your navy breton striped tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Ecru wide-leg trousers: Your ecru wide-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); matching formality (smart casual).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the brown leather penny loafers — matching formality (smart casual); shared style: classic.
- GAP outerwear-1 (essential): Nothing in your closet fills the role of the Camel oversized single-breasted blazer.
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Tan structured tote bag.

### formal-occasion-constraint

_Formal occasion: no casual sneakers, denim jacket or jeans for an evening event._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Black fitted blazer: Your black fitted blazer can stand in for the black cropped leather biker jacket — same colour family (black); suits event.
- dress-1 <- Forest green wrap midi dress: Your forest green wrap midi dress can stand in for the emerald satin bias-cut slip dress — same garment type (dress); similar silhouette (wrap, midi, defined waist).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the black strappy heeled sandals — same colour family (black); shared style: evening, sleek.
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Gold hoop earrings.

**Creative remix** — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Camel oversized blazer: Your camel oversized blazer can stand in for the black cropped leather biker jacket — matching formality (smart casual); suits event.
- dress-1 <- Black silk-look camisole: Your black silk-look camisole can stand in for the emerald satin bias-cut slip dress — shared style: evening, sleek; suits event.
- dress-1 <- Champagne satin midi skirt: Your champagne satin midi skirt can stand in for the emerald satin bias-cut slip dress — similar silhouette (bias-cut midi, fluid); shared style: evening, sleek.
- shoes-1 <- Brown leather loafers: Your brown leather loafers can stand in for the black strappy heeled sandals — it fills the same role in the outfit.
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Gold hoop earrings.

### shopping-disabled

_Shopping disabled: gaps carry no sourcing hints._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Camel oversized blazer: Your camel oversized blazer can stand in for the beige belted double-breasted trench coat — same colour family (beige); matching formality (smart casual).
- top-1 <- Navy fine-knit sweater: Your navy fine-knit sweater can stand in for the navy fine-knit crew-neck sweater — same garment type (knit); similar silhouette (slim, crew neck).
- bottom-1 <- Ecru wide-leg trousers: Your ecru wide-leg trousers can stand in for the ecru high-rise wide-leg trousers — same garment type (trousers); similar silhouette (high-rise wide-leg).
- shoes-1 <- White leather sneakers: Your white leather sneakers can stand in for the white minimal sneakers — same garment type (sneakers); same colour family (white).
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Wide-brim straw-coloured hat.

**Creative remix** — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Black fitted blazer: Your black fitted blazer can stand in for the beige belted double-breasted trench coat — shared style: classic.
- top-1 <- Black silk-look camisole: Your black silk-look camisole can stand in for the navy fine-knit crew-neck sweater — similar silhouette (slim, bias-cut); matching formality (smart casual).
- bottom-1 <- Black straight-leg trousers: Your black straight-leg trousers can stand in for the ecru high-rise wide-leg trousers — same garment type (trousers); matching formality (smart casual).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the white minimal sneakers — suits travel.
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Wide-brim straw-coloured hat.

### user-exclusion-and-keep

_Preference adherence: excluded pieces never appear, kept pieces always do._

> Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's rule-based matcher. Explanations are templated.

**Closest recreation** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Camel oversized blazer: Your camel oversized blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); similar silhouette (oversized, relaxed single-breasted).
- top-1 <- Navy Breton striped tee: Your navy breton striped tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Black straight-leg trousers: Your black straight-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); similar silhouette (straight-leg, high-rise).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the brown leather penny loafers — matching formality (smart casual); shared style: classic.
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

**Creative remix** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: Your sage tailored blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); similar silhouette (tailored, relaxed shoulders).
- top-1 <- Black silk-look camisole: Your black silk-look camisole can stand in for the white crew-neck t-shirt — shared style: minimal; suits work.
- bottom-1 <- Ecru wide-leg trousers: Your ecru wide-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); matching formality (smart casual).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the brown leather penny loafers — matching formality (smart casual); shared style: classic.
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

### ambiguous-not-an-outfit

_Ambiguous/non-outfit photo: no looks, honest reason._

No looks: We couldn't find a wearable outfit in this image. Try a clearer full-outfit photo.

### hallucinated-ids

_Model invents garment ids: they are removed and the slot becomes a gap._

**Invented** — 2/5 inspiration pieces from your closet · 2 wardrobe gaps

- outerwear-1 <- Camel oversized blazer: ok
- shoes-1 <- Brown leather loafers: ok
- GAP top-1 (essential): Nothing in your closet fills the role of the White crew-neck t-shirt.
- GAP bottom-1 (essential): Nothing in your closet fills the role of the Black straight-leg trousers.
- GAP accessory-1 (optional): Nothing in your closet fills the role of the Tan structured tote bag.

### malformed-model-output

_Model output unusable: labelled rule-based fallback, never a fabricated AI answer._

> Our AI stylist was unavailable (The AI returned an unusable answer), so these looks come from Rewear's rule-based matcher. Try again for AI-written styling.

**Closest recreation** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Camel oversized blazer: Your camel oversized blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); similar silhouette (oversized, relaxed single-breasted).
- top-1 <- White crew-neck tee: Your white crew-neck tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Black straight-leg trousers: Your black straight-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); similar silhouette (straight-leg, high-rise).
- shoes-1 <- Brown leather loafers: Your brown leather loafers can stand in for the brown leather penny loafers — same garment type (flats); similar silhouette (classic penny loafer).
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

**Creative remix** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: Your sage tailored blazer can stand in for the camel oversized single-breasted blazer — same garment type (blazer); similar silhouette (tailored, relaxed shoulders).
- top-1 <- Navy Breton striped tee: Your navy breton striped tee can stand in for the white crew-neck t-shirt — same garment type (tee); similar silhouette (straight, regular fit).
- bottom-1 <- Ecru wide-leg trousers: Your ecru wide-leg trousers can stand in for the black straight-leg trousers — same garment type (trousers); matching formality (smart casual).
- shoes-1 <- Black leather ankle boots: Your black leather ankle boots can stand in for the brown leather penny loafers — matching formality (smart casual); shared style: classic.
- accessory-1 <- Tan structured tote: Your tan structured tote can stand in for the tan structured tote bag — same garment type (bag); similar silhouette (structured, rectangular).

### empty-wardrobe

_No wardrobe: request is rejected with a clear error instead of invented looks._

(no generation — expected error)
