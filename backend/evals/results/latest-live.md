# Rewear evaluation — live Gemini composer

- Cases passed: **14/14**
- Checks passed: **70/70**
- Owned-garment validity: every returned garment id is checked per case (target 100%).
- Looks needing no purchase: 23/26 (descriptive, not a target)

Checks are deterministic. Candidate `score` values are heuristic ranking signals, not calibrated probabilities, and are never shown to users as confidence.

| Case | Result | Failed checks | Latency |
|---|---|---|---|
| exact-camel-work | PASS | — | 11123 ms |
| same-silhouette-different-colour | PASS | — | 10517 ms |
| aesthetic-substitute-weekend | PASS | — | 20055 ms |
| category-substitute-dress | PASS | — | 15423 ms |
| multiple-substitutes-distinct | PASS | — | 19899 ms |
| missing-item-optional | PASS | — | 11944 ms |
| missing-key-piece | PASS | — | 11620 ms |
| formal-occasion-constraint | PASS | — | 14698 ms |
| shopping-disabled | PASS | — | 17163 ms |
| user-exclusion-and-keep | PASS | — | 18745 ms |
| ambiguous-not-an-outfit | PASS | — | 0 ms |
| hallucinated-ids | PASS | — | 19 ms |
| malformed-model-output | PASS | — | 17 ms |
| empty-wardrobe | PASS | — | 0 ms |

## Looks for human review

### exact-camel-work

_Exact garment matches: every key piece of the camel work look is owned._

**Classic Smart-Casual Tailoring** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Camel oversized blazer: The 'Camel oversized blazer' perfectly matches the inspiration's camel oversized blazer, preserving the key color, relaxed silhouette, and smart-casual formality.
- top-1 <- White crew-neck tee: The 'White crew-neck tee' is an exact match for the inspiration's white tee, maintaining the clean, minimal base layer.
- bottom-1 <- Black straight-leg trousers: The 'Black straight-leg trousers' directly correspond to the inspiration's black straight-leg trousers, ensuring the correct silhouette and color for the bottom half.
- shoes-1 <- Brown leather loafers: The 'Brown leather loafers' are an ideal match for the inspiration's brown loafers, completing the polished smart-casual footwear.
- accessory-1 <- Tan structured tote: The 'Tan structured tote' is a perfect replacement for the inspiration's tan tote bag, adding a structured and complementary accessory.

**Modern Sage & Black Office Look** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: The 'Sage tailored blazer' replaces the camel blazer, offering a similar tailored outerwear piece with a relaxed silhouette, but introduces a modern sage green color.
- top-1 <- White poplin shirt: The 'White poplin shirt' replaces the white tee, maintaining the crisp white base layer but elevating the formality slightly with a more structured shirt.
- bottom-1 <- Black straight-leg trousers: The 'Black straight-leg trousers' are retained from the inspiration, providing a classic, grounding bottom half that balances the top.
- shoes-1 <- Black leather ankle boots: The 'Black leather ankle boots' replace the brown loafers, shifting the footwear to a sleeker, more contemporary option while maintaining smart-casual formality and a darker tone.
- accessory-1 <- Tan structured tote: The 'Tan structured tote' remains, offering a consistent structured element and a warm neutral tone that complements the sage blazer.

### same-silhouette-different-colour

_Camel blazer removed: a blazer with the same structure in another colour should replace it._

**Sage and Black Tailored Ensemble** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: The sage tailored blazer replaces the camel blazer, maintaining the tailored, relaxed silhouette and smart-casual mood.
- top-1 <- White crew-neck tee: The white crew-neck tee perfectly matches the inspiration's base layer, providing a clean, minimal foundation.
- bottom-1 <- Black straight-leg trousers: The black straight-leg trousers are a direct match for the inspiration, maintaining the polished and tailored lower half.
- shoes-1 <- Brown leather loafers: The brown leather loafers match the inspiration's footwear, adding a classic and polished touch.
- accessory-1 <- Tan structured tote: The tan structured tote is a direct match, completing the look with a practical yet chic accessory.

**Monochrome & Modern Tailoring** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Black fitted blazer: The black fitted blazer replaces the camel blazer, shifting to a more structured silhouette while keeping the tailored outerwear role.
- top-1 <- White poplin shirt: A white poplin shirt replaces the white tee, elevating the base layer to a crisper, more formal option while maintaining the white color.
- bottom-1 <- Ecru wide-leg trousers: Ecru wide-leg trousers replace the black straight-leg trousers, offering a softer contrast and a more relaxed, modern silhouette.
- shoes-1 <- Black leather ankle boots: Black leather ankle boots replace the brown loafers, offering a sleeker, slightly more assertive footwear choice that complements the black blazer.
- accessory-1 <- Tan structured tote: The tan structured tote remains as a classic accessory, providing a warm neutral tone against the monochrome outfit.

### aesthetic-substitute-weekend

_No olive overshirt owned: another casual outer layer takes its role._

**Modern Utility Layers** — 4/4 pieces already in your closet · No new purchase needed

- outerwear-1 <- Light-wash denim jacket: The light-wash denim jacket replaces the olive utility overshirt, maintaining a similar boxy, relaxed silhouette and the casual, utility mood. The color shifts from olive to light blue.
- top-1 <- Cream cable-knit cardigan: The cream cable-knit cardigan stands in for the cream crew-neck knit sweater, perfectly matching the colour, cosy feel, and relaxed silhouette. It can be worn buttoned up as the main top.
- bottom-1 <- Mid-wash straight jeans: These mid-wash straight-leg jeans closely match the inspiration's light-wash straight-leg jeans, preserving the classic casual silhouette and feel.
- shoes-1 <- White leather sneakers: The white leather sneakers are a direct match for the inspiration's white low-top sneakers, maintaining the clean, casual foundation of the outfit.

**Earthy Tones & Relaxed Tailoring** — 4/4 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: The sage tailored blazer replaces the olive overshirt, bringing in a similar earthy green tone. While more tailored, its relaxed shoulders keep the overall mood from becoming too formal, adapting the utility layer to a slightly more polished aesthetic.
- top-1 <- Rust ribbed sweater: The rust ribbed sweater replaces the cream knit, introducing a warm, earthy alternative to the original's neutral tone while keeping the cosy, relaxed knit texture and silhouette.
- bottom-1 <- Black straight-leg trousers: The black straight-leg trousers replace the light-wash jeans, maintaining the clean straight silhouette but shifting the colour to a versatile black, offering a slightly more refined base.
- shoes-1 <- White leather sneakers: The white leather sneakers maintain the casual and comfortable footwear choice, providing a light contrast to the darker trousers.

**Soft Layers & Neutral Base** — 4/4 pieces already in your closet · No new purchase needed

- outerwear-1 <- Cream cable-knit cardigan: The cream cable-knit cardigan takes on the role of the outer layer, replacing the utility overshirt with a softer, cosier alternative. Worn open, it provides a relaxed, flowing silhouette similar to a light jacket.
- top-1 <- White poplin shirt: The white poplin shirt replaces the cream knit, offering a crisp, clean base layer that maintains a relaxed fit under the cardigan. It shifts the texture from knit to woven.
- bottom-1 <- Ecru wide-leg trousers: The ecru wide-leg trousers replace the straight-leg jeans, offering a different silhouette with a relaxed, flowing line and a soft neutral colour that complements the cream cardigan.
- shoes-1 <- Brown leather loafers: The brown leather loafers replace the white sneakers, elevating the footwear slightly while maintaining a comfortable and classic feel, fitting the softer, more refined neutral palette.

### category-substitute-dress

_Matching aesthetic with different categories: slip dress recreated by a top + skirt two-piece._

**Sleek Evening with a Tailored Edge** — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Black fitted blazer: The black fitted blazer replaces the cropped leather jacket, preserving the black color and structured element, but shifting the edgy biker style to a more polished, tailored aesthetic.
- dress-1 <- Black silk-look camisole: This black silk-look camisole acts as the top part of the slip dress, providing a sleek, dark foundation that pairs well with the skirt to create a column silhouette.
- dress-1 <- Champagne satin midi skirt: The champagne satin midi skirt replaces the lower half of the emerald slip dress, maintaining the fluid, bias-cut silhouette and luxurious evening feel, albeit in a lighter, neutral tone.
- shoes-1 <- Black leather ankle boots: These black leather ankle boots replace the strappy heels, maintaining the black color and sleekness suitable for evening, offering a slightly more grounded but equally chic finish.
- GAP accessory-1 (optional): No gold hoop earrings or similar evening-appropriate accessories are available in the closet.

**Modern Minimalist Evening Look** — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Sage tailored blazer: The sage tailored blazer replaces the black leather jacket, offering a different color to introduce a modern contrast while maintaining a structured outer layer over the dark base.
- dress-1 <- Black silk-look camisole: The black silk-look camisole forms the sleek top half of the base layer, echoing the luxurious feel of the slip dress and setting a dark, elegant tone.
- dress-1 <- Black straight-leg trousers: These black straight-leg trousers replace the fluidity of the slip dress with a tailored, modern column, maintaining a sleek, dark foundation suitable for an event.
- shoes-1 <- Black leather ankle boots: These black leather ankle boots provide a cohesive dark base with the trousers, mirroring the sleekness and formality of the inspiration's shoes, but in a boot style.
- GAP accessory-1 (optional): No gold hoop earrings or similar evening-appropriate accessories are available in the closet.

### multiple-substitutes-distinct

_Several reasonable substitutes: closest and creative looks must differ._

**Classic Tailored Minimalism** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Camel oversized blazer: The 'Camel oversized blazer' perfectly matches the inspiration's camel oversized single-breasted blazer, maintaining the key silhouette and color.
- top-1 <- White crew-neck tee: The 'White crew-neck tee' directly corresponds to the inspiration's white crew-neck t-shirt, preserving the simple base layer.
- bottom-1 <- Black straight-leg trousers: The 'Black straight-leg trousers' are an exact match for the inspiration's black straight-leg trousers, keeping the tailored and minimal bottom half.
- shoes-1 <- Brown leather loafers: The 'Brown leather loafers' are the exact item from the inspiration, providing the classic, polished footwear.
- accessory-1 <- Tan structured tote: The 'Tan structured tote' is a direct match for the inspiration's tan structured tote bag, completing the polished smart-casual aesthetic.

**Modern Sage & Black Office Chic** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: The 'Sage tailored blazer' replaces the camel blazer, offering a fresh color while maintaining the tailored, relaxed silhouette and smart-casual formality of the outer layer.
- top-1 <- White poplin shirt: The 'White poplin shirt' substitutes the white tee, elevating the formality slightly while keeping the clean white base and minimal aesthetic.
- bottom-1 <- Black straight-leg trousers: The 'Black straight-leg trousers' are retained for their perfect match to the inspiration's silhouette and color, providing a strong foundation.
- shoes-1 <- Black leather ankle boots: The 'Black leather ankle boots' replace the loafers, shifting to a sleek, slightly more assertive footwear choice that complements the black trousers and sage blazer.
- accessory-1 <- Tan structured tote: The 'Tan structured tote' is used again to provide a consistent, polished accessory that contrasts nicely with the sage and black palette.

**Relaxed Ecru & Navy Office Look** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Navy fine-knit sweater: The 'Navy fine-knit sweater' acts as a soft, unstructured outer layer, replacing the blazer while maintaining a smart-casual, minimal aesthetic in a different color.
- top-1 <- Navy Breton striped tee: The 'Navy Breton striped tee' replaces the plain white tee, adding a subtle pattern and classic touch while fitting the base layer role under the knit.
- bottom-1 <- Ecru wide-leg trousers: The 'Ecru wide-leg trousers' replace the black straight-leg trousers, offering a lighter color and a more relaxed, modern wide-leg silhouette.
- shoes-1 <- White leather sneakers: The 'White leather sneakers' replace the loafers, embracing a more relaxed smart-casual vibe, suitable for work given the tailored elements, as per styling principle sp-008.
- accessory-1 <- Tan structured tote: The 'Tan structured tote' adds a touch of polish and structure, grounding the otherwise softer and more relaxed elements of the outfit.

### missing-item-optional

_Missing wardrobe item: no hat owned; it must be an optional gap, never an invented garment._

**Classic Travel Layers** — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Camel oversized blazer: The camel oversized blazer replaces the beige trench, maintaining the warm neutral colour palette and smart-casual feel. While not a long trench, it serves as a polished outer layer.
- top-1 <- Navy fine-knit sweater: The navy fine-knit sweater is a direct match for the inspiration's slim navy knit, perfectly preserving its colour, silhouette, and role as a comfortable mid-layer.
- bottom-1 <- Ecru wide-leg trousers: The ecru wide-leg trousers are a perfect match, maintaining the relaxed yet polished wide-leg silhouette and the light, neutral colour of the inspiration.
- shoes-1 <- White leather sneakers: The white leather sneakers directly match the inspiration's white minimal sneakers, providing comfort and a clean, casual counterpoint to the smart elements.
- GAP accessory-1 (optional): No wide-brim hat is available in the owned garments to match the inspiration.

**Modern Navy & Black Travel Ensemble** — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Black fitted blazer: The black fitted blazer replaces the beige trench, shifting the outer layer to a darker, more formal tone but keeping the tailored, polished feel of a blazer.
- top-1 <- Navy fine-knit sweater: The navy fine-knit sweater directly replaces the inspiration's top, maintaining the slim silhouette and classic navy colour.
- bottom-1 <- Black straight-leg trousers: The black straight-leg trousers replace the ecru wide-leg trousers, offering a different colour and a more streamlined silhouette while maintaining a smart-casual base.
- shoes-1 <- Black leather ankle boots: The black leather ankle boots replace the white sneakers, providing a sleeker, more elevated footwear option that complements the black trousers and blazer.
- GAP accessory-1 (optional): No wide-brim hat is available in the owned garments to match the inspiration.

### missing-key-piece

_Genuine gap: closet without any outer layer must report an essential outerwear gap._

**Minimalist Workwear with a Missing Layer** — 3/5 inspiration pieces from your closet · 1 wardrobe gap

- top-1 <- White crew-neck tee: The white crew-neck tee directly replaces the inspiration's white tee, maintaining the simple base layer and crisp white colour.
- bottom-1 <- Black straight-leg trousers: These black straight-leg trousers are a perfect match for the inspiration's black straight-leg trousers, preserving the tailored, high-rise silhouette and black colour.
- shoes-1 <- Brown leather loafers: The brown leather loafers directly replace the inspiration's brown loafers, maintaining the polished smart-casual footwear choice and classic style.
- GAP outerwear-1 (essential): There is no camel oversized blazer or suitable tailored jacket in your owned garments to replicate the key layering piece of the inspiration. This piece defines the silhouette and formality.
- GAP accessory-1 (optional): No tan structured tote bag was available in your owned garments. While it adds to the polished look, the core outfit can function without it.

**Monochrome & Modern Tailoring** — 3/5 inspiration pieces from your closet · 1 wardrobe gap

- top-1 <- White poplin shirt: Instead of a t-shirt, a white poplin shirt offers a slightly more formal, crisp base layer while maintaining the white colour and minimal aesthetic.
- bottom-1 <- Ecru wide-leg trousers: Ecru wide-leg trousers replace the black straight-leg ones, shifting the palette to a lighter neutral and introducing a more relaxed, modern wide-leg silhouette while maintaining a tailored feel.
- shoes-1 <- Black leather ankle boots: Black ankle boots replace the brown loafers, offering a sleeker, more contemporary footwear option that complements the monochrome palette while maintaining smart-casual formality.
- GAP outerwear-1 (essential): No suitable blazer or tailored jacket is available to replicate the key outer layer. This piece is essential for the original inspiration's silhouette and formality.
- GAP accessory-1 (optional): No tan structured tote bag was available. The outfit works well without it, focusing on the clothing items.

### formal-occasion-constraint

_Formal occasion: no casual sneakers, denim jacket or jeans for an evening event._

**Edgy Green & Black Evening** — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Black fitted blazer: The black fitted blazer substitutes the cropped leather jacket, maintaining the dark, structured top layer and sleek feel, though it's a blazer rather than a biker jacket.
- dress-1 <- Forest green wrap midi dress: The forest green wrap midi dress replaces the emerald slip dress, preserving the elegant midi length and rich green hue, while offering a defined waist instead of a column silhouette.
- shoes-1 <- Black leather ankle boots: Black leather ankle boots replace the strappy heels, keeping the black color and sleekness, but offering a more grounded, edgy feel with a block heel instead of delicate straps.
- GAP accessory-1 (optional): No gold hoop earrings or similar statement earrings are available in your closet.

**Sleek Champagne & Black Separates** — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Black fitted blazer: The black fitted blazer provides the necessary dark, structured layer over the fluid separates, maintaining the sleek and slightly edgy contrast.
- dress-1 <- Black silk-look camisole: The black silk-look camisole serves as the top part of the 'dress' effect, offering a sleek, dark, and fluid upper half.
- dress-1 <- Champagne satin midi skirt: The champagne satin midi skirt forms the bottom half of the 'dress', capturing the bias-cut, fluid silhouette and luxurious sheen of the original slip dress.
- shoes-1 <- Black leather ankle boots: Black leather ankle boots ground the look, providing a sleek and modern alternative to strappy heels, maintaining the dark base.
- GAP accessory-1 (optional): No gold hoop earrings or similar statement earrings are available in your closet.

### shopping-disabled

_Shopping disabled: gaps carry no sourcing hints._

**Polished Travel Layers** — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Camel oversized blazer: The 'Camel oversized blazer' replaces the beige trench, offering a similar smart-casual formality and a warm neutral tone, maintaining a polished outer layer.
- top-1 <- Navy fine-knit sweater: The 'Navy fine-knit sweater' is a direct match for the inspiration's navy fine-knit, preserving the slim silhouette and classic color.
- bottom-1 <- Ecru wide-leg trousers: The 'Ecru wide-leg trousers' perfectly match the inspiration's ecru wide-leg trousers, maintaining the relaxed, fluid bottom silhouette and light neutral color.
- shoes-1 <- White leather sneakers: The 'White leather sneakers' are a direct match for the inspiration's white minimal sneakers, ensuring comfort and a clean, casual base.
- GAP accessory-1 (optional): No wide-brim hat is available in the owned garments to match the inspiration. The look remains complete and functional without it.

**Modern Navy & Cream Travel** — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Sage tailored blazer: The 'Sage tailored blazer' replaces the beige trench, introducing a fresh, modern color while retaining a structured yet relaxed outer layer suitable for smart-casual travel.
- top-1 <- White poplin shirt: The 'White poplin shirt' replaces the navy knit, offering a crisp, classic base layer that is equally polished and versatile for travel.
- bottom-1 <- Black straight-leg trousers: The 'Black straight-leg trousers' substitute for the ecru wide-leg, providing a sleek, tailored bottom that maintains a long line and smart-casual feel.
- shoes-1 <- Brown leather loafers: The 'Brown leather loafers' replace the white sneakers, elevating the formality slightly while keeping a comfortable, classic, and polished footwearchoice.
- extra <- Tan structured tote: The 'Tan structured tote' is added as a practical and stylish accessory, complementing the warm tones and polished feel of the outfit.
- GAP accessory-1 (optional): No wide-brim hat is available. The added tote bag provides a functional accessory for travel.

**Relaxed Weekend Layers** — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional

- outerwear-1 <- Light-wash denim jacket: The 'Light-wash denim jacket' replaces the trench, offering a more casual and relaxed outer layer while still providing warmth and a distinct silhouette.
- top-1 <- Navy Breton striped tee: The 'Navy Breton striped tee' replaces the fine-knit sweater, bringing a playful, classic print and a more casual feel while keeping the navy color family.
- bottom-1 <- Mid-wash straight jeans: The 'Mid-wash straight jeans' replace the ecru wide-leg trousers, providing a comfortable and universally casual bottom that maintains a relaxed, straight silhouette.
- shoes-1 <- White leather sneakers: The 'White leather sneakers' are a direct match for the inspiration's white minimal sneakers, perfectly suiting this more casual interpretation.
- GAP accessory-1 (optional): No wide-brim hat is available. The casual nature of this look also makes a hat less essential.

### user-exclusion-and-keep

_Preference adherence: excluded pieces never appear, kept pieces always do._

**Polished Workwear with a Neutral Palette** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Camel oversized blazer: The owned camel oversized blazer perfectly matches the inspiration's key outerwear, preserving the relaxed silhouette and warm neutral tone.
- top-1 <- White poplin shirt: A crisp white poplin shirt replaces the white tee, maintaining the bright, minimal base layer while elevating the formality slightly for a 'work' occasion.
- bottom-1 <- Black straight-leg trousers: These black straight-leg trousers are an exact match for the inspiration, ensuring the sleek, tailored lower half and classic color.
- shoes-1 <- Black leather ankle boots: Black leather ankle boots fulfill the 'keep' preference and provide a sleek, polished grounding for the outfit, aligning with the smart-casual formality.
- accessory-1 <- Tan structured tote: The tan structured tote perfectly mirrors the inspiration's accessory, adding a classic, functional element in a complementary neutral tone.

**Modern Tailoring with a Pop of Sage** — 5/5 pieces already in your closet · No new purchase needed

- outerwear-1 <- Sage tailored blazer: The sage tailored blazer offers a fresh color alternative to camel, maintaining the tailored yet relaxed silhouette and smart-casual feel of the inspiration's outerwear.
- top-1 <- Navy Breton striped tee: A navy Breton striped tee replaces the plain white tee, introducing a subtle pattern and darker base that still works as a minimalist underlayer.
- bottom-1 <- Ecru wide-leg trousers: Ecru wide-leg trousers provide a lighter, more relaxed alternative to black straight-leg trousers, shifting the palette while maintaining a tailored bottom.
- shoes-1 <- Black leather ankle boots: Black leather ankle boots ground the outfit with a sleek, practical choice, fulfilling the 'keep' requirement and adding a touch of modern edge.
- accessory-1 <- Tan structured tote: The tan structured tote complements the sage and ecru palette, adding a classic and functional element consistent with the inspiration's accessory role.

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
