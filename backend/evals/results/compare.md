# Rewear — baseline vs agentic stylist (live Gemini)

Baseline = single Gemini composition pass + deterministic validation.
Agentic = ADK workflow: stylist → validation → multimodal critic → bounded refinement (max_refinement_rounds=1).

## Summary

| Engine | Cases passed | Invalid owned ids | Looks returned | Looks with styling instructions | Critic interventions | Median latency | Max latency | Avg tokens* |
|---|---|---|---|---|---|---|---|---|
| single_pass | 16/16 | 0 | 31 | 31 | 0 | 13754 ms | 22172 ms | n/a |
| agentic | 15/16 | 0 | 18 | 18 | 14 | 29134 ms | 49018 ms | 20349 |

*Token totals are tracked for the agentic workflow's model calls (single-pass logs them per call).

## Per case

| Case | Engine | Objective checks | Looks | Latency | Rounds | Critic flags |
|---|---|---|---|---|---|---|
| real-denim-skirt | single_pass (gemini) | all pass | 2 | 13009 ms | 1 | 0 |
| real-denim-skirt | agentic (agentic) | all pass | 1 | 44205 ms | 2 | 2 |
| real-emerald-evening | single_pass (gemini) | all pass | 1 | 9490 ms | 1 | 0 |
| real-emerald-evening | agentic (agentic) | >=1 looks | 0 | 38394 ms | 2 | 1 |
| real-camel-work | single_pass (gemini) | all pass | 2 | 12486 ms | 1 | 0 |
| real-camel-work | agentic (agentic) | all pass | 1 | 18516 ms | 1 | 0 |
| real-satin-material-challenge | single_pass (gemini) | all pass | 2 | 12299 ms | 1 | 0 |
| real-satin-material-challenge | agentic (agentic) | all pass | 1 | 29134 ms | 2 | 1 |
| real-no-good-outfit | single_pass (gemini) | all pass | 0 | 6336 ms | 1 | 0 |
| real-no-good-outfit | agentic (agentic) | all pass | 0 | 6347 ms | 1 | 0 |
| exact-camel-work | single_pass (gemini) | all pass | 2 | 13214 ms | 1 | 0 |
| exact-camel-work | agentic (agentic) | all pass | 2 | 36777 ms | 2 | 1 |
| same-silhouette-different-colour | single_pass (gemini) | all pass | 3 | 13948 ms | 1 | 0 |
| same-silhouette-different-colour | agentic (agentic) | all pass | 3 | 49018 ms | 2 | 2 |
| aesthetic-substitute-weekend | single_pass (gemini) | all pass | 2 | 18261 ms | 1 | 0 |
| aesthetic-substitute-weekend | agentic (agentic) | all pass | 2 | 26954 ms | 1 | 0 |
| category-substitute-dress | single_pass (gemini) | all pass | 2 | 15861 ms | 1 | 0 |
| category-substitute-dress | agentic (agentic) | all pass | 1 | 16285 ms | 1 | 0 |
| multiple-substitutes-distinct | single_pass (gemini) | all pass | 3 | 22172 ms | 1 | 0 |
| multiple-substitutes-distinct | agentic (agentic) | all pass | 2 | 30517 ms | 2 | 1 |
| missing-item-optional | single_pass (gemini) | all pass | 3 | 15651 ms | 1 | 0 |
| missing-item-optional | agentic (agentic) | all pass | 1 | 15042 ms | 1 | 0 |
| missing-key-piece | single_pass (gemini) | all pass | 2 | 16930 ms | 1 | 0 |
| missing-key-piece | agentic (agentic) | all pass | 0 | 22975 ms | 2 | 2 |
| formal-occasion-constraint | single_pass (gemini) | all pass | 3 | 13754 ms | 1 | 0 |
| formal-occasion-constraint | agentic (agentic) | all pass | 2 | 24432 ms | 1 | 0 |
| shopping-disabled | single_pass (gemini) | all pass | 2 | 13323 ms | 1 | 0 |
| shopping-disabled | agentic (agentic) | all pass | 1 | 41843 ms | 2 | 2 |
| user-exclusion-and-keep | single_pass (gemini) | all pass | 2 | 17816 ms | 1 | 0 |
| user-exclusion-and-keep | agentic (agentic) | all pass | 1 | 42377 ms | 2 | 2 |
| ambiguous-not-an-outfit | single_pass (gemini) | all pass | 0 | 0 ms | 1 | 0 |
| ambiguous-not-an-outfit | agentic (gemini) | all pass | 0 | 0 ms | 1 | 0 |

## Side-by-side looks for human rating

Rate each engine's output 1–5 for coherence, inspiration fidelity and styling usefulness.

### real-denim-skirt

_The reported failure: white tucked button-down + high-waisted denim midi skirt + sneakers, styled from a real 7-piece wardrobe with no white shirt or denim skirt. A strong answer protects the defined waist and relaxed mood (e.g. the belted shirt-dress, or sweater + skirt with a tuck and casual shoes) instead of stacking dressy substitutes and an unneeded jacket._

**single_pass** — human rating: ___/5
- **Modern Midi Skirt & Sneakers** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Burgundy satin midi skirt → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - Coherence: This look maintains the inspiration's relaxed, chic, and modern aesthetic. The defined waist is achieved by tucking the sweater into the high-waisted midi skirt, and the midi length provides the elongated lower line. The color palette shifts to a deeper, more autumnal feel with burgundy and black, balanced by the white in the sneakers.
  - How to wear: Front-tuck the black sweater into the burgundy satin skirt to emphasize the defined waist. / Allow the satin skirt to flow naturally for movement.
  - Declared deviations: Color palette shift to darker tones (burgundy and black).; Material change from rigid denim to flowing satin.
- **High-Rise Denim & Sweater Combo** (creative) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Rust suede-like jacket → extra, Black crewneck sweater → White cotton button-down shirt, Black high-rise wide-leg jeans → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - Coherence: This look reinterprets the inspiration's proportions with high-rise wide-leg jeans, maintaining the defined waist and elongated lower line. The monochromatic black base of the sweater and jeans creates a sleek foundation, while the rust jacket adds warmth and texture. The white sneakers provide a modern, casual contrast.
  - How to wear: Tuck the black sweater fully into the high-rise jeans to emphasize the waist. / Wear the rust jacket open to showcase the high waist and add a textural contrast.
  - Declared deviations: Bottom garment type changed from skirt to wide-leg jeans.; Primary color palette is darker and more monochromatic (black).; Added an outer layer.

**agentic** — human rating: ___/5
- **Luxe Casual Midi** (creative) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Burgundy satin midi skirt → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - Coherence: This creative look pairs a luxurious satin midi skirt with a relaxed sweater and chunky sneakers, creating an elevated yet comfortable outfit. The defined waist and elongated midi line are preserved, while the mix of textures and the deep burgundy color add a sophisticated twist to the original casual inspiration.
  - How to wear: Half-tuck the front of the sweater into the skirt to maintain the defined waist. / Allow the satin skirt to flow freely for movement and elegance. / Ensure the sweater sleeves are pushed up or rolled to keep a relaxed, unstudied feel.
  - Declared deviations: Changed the bottom material from rigid denim to fluid satin, increasing formality.; Changed the color palette significantly to black and burgundy.; Used a knit sweater instead of a crisp button-down.
  - Critic: approved after 0 revision(s); notes: The 'light top against a mid-tone bottom' essential trait is lost due to the black sweater and dark burgundy skirt. While this is a declared deviation for a creative look, it's worth noting that the original color contrast is completely absent.; The black crewneck sweater, being a slightly shorter, relaxed fit, might require careful styling (half-tuck) to ensure the waist definition is as crisp as the inspiration, especially with the fluid satin skirt. If not tucked well, it could appear boxy.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

### real-emerald-evening

_Evening slip dress + cropped leather jacket + heels, from the real wardrobe (satin skirt, tweed and suede jackets, no heels)._

**single_pass** — human rating: ___/5
- **Edgy Evening Column with Tweed** (creative) — 2/4 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Cream embellished tweed jacket → Black cropped leather biker jacket, Burgundy satin midi skirt → Emerald satin bias-cut slip dress
  - Coherence: The black sweater and burgundy satin skirt create a rich, dark column. The cream tweed jacket adds a sharp, contrasting layer, maintaining the 'short structured over long fluid' proportion. The palette is deep and elegant with a touch of light contrast.
  - How to wear: Tuck the black sweater into the burgundy satin midi skirt to create a seamless, long column line. / Wear the cream tweed jacket open over the sweater and skirt to highlight the cropped silhouette and the fluid column beneath. / Accessorize with gold-toned jewelry if available to complement the jacket's embellishments and elevate the look.
  - Declared deviations: Replaced the single slip dress with a two-piece (sweater + skirt) to achieve the column silhouette.; Used a tweed jacket instead of leather, offering a different 'tough edge' with texture and embellishment.; Changed the color palette to burgundy, black, and cream, moving away from emerald and black.
  - Gaps: Black strappy heeled sandals (essential); Gold hoop earrings (optional)

**agentic** — human rating: ___/5
- No looks: The user's wardrobe lacks suitable formal footwear (heels or dressy flats) to create an 'evening glamour' look for an 'event' occasion. The only available shoes, 'r_platform_sneakers', are too casual and would fundamentally undermine the aesthetic and formality required by the inspiration. Without appropriate shoes, no coherent and occasion-appropriate outfit can be formed.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

### real-camel-work

_Camel blazer + tee + straight trousers + loafers for work, from the real wardrobe (no blazer, no tee, no loafers): expect honest gaps or declared deviations._

**single_pass** — human rating: ___/5
- **Cream Tweed & Wide-Leg Jeans** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Cream embellished tweed jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - Coherence: This look presents a modern smart-casual aesthetic with a focus on relaxed proportions. The cropped tweed jacket offers structure, balancing the volume of the wide-leg jeans. The black sweater and jeans create a cohesive dark base, while the white sneakers add a fresh, casual contrast.
  - How to wear: Wear the tweed jacket open to allow the black sweater to be visible. / Ensure the wide-leg jeans skim the top of the sneakers for a clean line.
  - Declared deviations: The blazer is cropped and tweed instead of oversized and camel.; The bottom is wide-leg jeans instead of straight-leg trousers.; Footwear is sneakers instead of loafers.; The base layer is a black sweater instead of a white tee.
  - Gaps: Tan structured tote bag (optional)
- **Rust & Black with a Touch of Satin** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Burgundy satin midi skirt → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - Coherence: This look plays with contrasting textures and formality, combining the casual rust overshirt and sneakers with an elegant satin skirt. The dark base of the black sweater and burgundy skirt creates depth, while the rust jacket adds warmth. The sneakers deliberately dress down the skirt, making it work-appropriate in a creative way.
  - How to wear: Wear the rust jacket open, letting its relaxed fit drape over the sweater and skirt. / Consider a half-tuck for the black sweater if it's long enough to define the waist with the skirt. / Allow the satin skirt to flow freely, emphasizing its movement.
  - Declared deviations: Outerwear is a casual overshirt jacket instead of a structured blazer.; Bottom is a satin midi skirt instead of tailored trousers.; Footwear is sneakers instead of loafers.; Base layer is a black sweater instead of a white tee.
  - Gaps: Tan structured tote bag (optional)

**agentic** — human rating: ___/5
- **Modern Neutrals** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - Coherence: The outfit balances the relaxed rust jacket and black sweater with the structured wide-leg jeans, creating a comfortable yet put-together silhouette. The monochromatic black base is broken by the warm jacket and bright sneakers, maintaining a modern neutral palette. The mix of suede-like texture, knit, denim, and leather keeps the look interesting while remaining understated and smart-casual.
  - How to wear: Wear the rust jacket open to maintain the relaxed, layered look. / Ensure the black sweater is not overly bulky to fit smoothly under the jacket. / Allow the wide-leg jeans to fall cleanly over the platform sneakers for an elongated line.
  - Declared deviations: The blazer is replaced by a more casual suede-like jacket.; The white tee is replaced by a black sweater, flipping the light/dark contrast of the base.; Tailored trousers are replaced by wide-leg jeans, shifting the material and exact leg line but keeping the overall silhouette.
  - Gaps: Tan structured tote bag (optional)
  - Critic: approved after 0 revision(s); notes: The combination of a suede-like overshirt, wide-leg denim jeans, and chunky platform sneakers significantly shifts the aesthetic from 'minimal, tailored, classic' and 'polished smart-casual' to a much more casual, streetwear-inspired look. The essential trait of 'polished but easy smart-casual' is lost.; The material combination of a matte suede-like jacket, knit sweater, denim jeans, and chunky leather sneakers creates a very casual and somewhat heavy texture profile that clashes with the polished suiting and smooth leather of the inspiration. The 'tailored' and 'polished' aspects are lost.; While the wide-leg jeans provide an elongated line, the combination of a relaxed, slightly shorter jacket (as seen in the garment image) with wide-leg jeans can create a less streamlined silhouette than the inspiration's hip-length blazer over straight trousers. The volume balance shifts from 'volume up top, slim straight bottom' to 'volume up top, volume on bottom'.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### real-satin-material-challenge

_Material challenge: satin slip skirt dressed down with a slouchy sweatshirt and sneakers. The burgundy satin skirt fits; the stylist must keep the dressed-down mood._

**single_pass** — human rating: ___/5
- **Modern High-Low Contrast** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - Coherence: This look maintains the core high-low contrast by pairing a relaxed, casual sweater with a sleek satin midi skirt and chunky sneakers. The palette is grounded in neutrals (black, white) with a rich burgundy accent, creating a sophisticated yet relaxed feel.
  - How to wear: Front-tuck the black sweater to define the waist and maintain the proportion of the inspiration. / Wear the skirt at your natural waist.
  - Declared deviations: Color palette shifted from soft neutrals to a darker neutral with a jewel-toned accent.
- **Modern Casual Long Line** (creative) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Black high-rise wide-leg jeans → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - Coherence: This look offers a creative interpretation of the inspiration's proportions, using high-rise wide-leg jeans to achieve a similar long, fluid lower line. The all-black base with white/black sneakers creates a sleek, modern, and monochromatic casual outfit.
  - How to wear: Ensure the black sweater is front-tucked into the high-rise jeans to emphasize the waist and create the desired long lower line. / Wear the jeans to skim the top of the sneakers for a clean, elongated look.
  - Declared deviations: Replaced the satin midi skirt with high-rise wide-leg jeans, changing the material and specific silhouette but keeping the long-line proportion.; The high-low material contrast is shifted from satin/fleece to denim/sweater knit.

**agentic** — human rating: ___/5
- **Sleek & Sporty Contrast** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - Coherence: This outfit achieves a high-low aesthetic by pairing the luxurious, fluid satin skirt with a relaxed knit sweater and chunky sneakers. The proportions are balanced with an oversized top that is visually cinched at the waist, contrasting with the flowing midi skirt. The neutral black and burgundy palette provides a soft contrast, allowing the textures to stand out.
  - How to wear: Front-tuck or half-tuck the black sweater to define the waist. / Push up the sweater sleeves slightly for a more relaxed feel.
  - Declared deviations: Sweater is black knit instead of heather grey fleece.; Skirt is burgundy A-line satin instead of champagne bias-cut satin.
  - Critic: approved after 0 revision(s); notes: The black sweater is a matte knit rather than a fleece sweatshirt, which slightly reduces the 'sporty' aspect of the high-low contrast and the material interplay.; The burgundy skirt is A-line, not bias-cut, which slightly alters the fluid drape compared to the inspiration's slip skirt.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

### real-no-good-outfit

_No good outfit exists: black-tie tuxedo look from a casual 7-piece wardrobe. A good system admits the gap instead of forcing a match._

**single_pass** — human rating: ___/5
- No looks: The inspiration is a very specific and strict black-tie tuxedo outfit. Your current wardrobe consists primarily of casual or smart-casual items and lacks any formal garments such as tuxedo jackets, dress shirts, formal trousers, or formal shoes. Given the 'close fidelity' preference, it is impossible to create a look that even remotely matches the inspiration's formality, silhouette, or colour palette using only the owned garments. There are no suitable replacements for any of the key pieces (tuxedo jacket, dress shirt, tuxedo trousers, patent oxfords).

**agentic** — human rating: ___/5
- No looks: The user's wardrobe lacks any garments suitable for a 'strict black tie' formal occasion. The inspiration requires formal tailored suiting in black and a crisp white dress shirt, none of which are present. All owned garments are casual or smart-casual, making it impossible to preserve the essential traits of 'matching black tailoring', 'crisp white shirt', and 'strict formality'.
- Workflow: Stylist proposed 0 look(s); 0 passed validation

### exact-camel-work

_Exact garment matches: every key piece of the camel work look is owned._

**single_pass** — human rating: ___/5
- **Classic Camel & Black Tailoring** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look achieves high coherence by directly replicating the inspiration's minimal, tailored aesthetic, colour palette, and balanced proportions. The camel, white, and black create a sophisticated neutral base, accented by the brown leather.
  - How to wear: Wear the blazer open over the tee. / Loosely front-tuck the white tee into the trousers for a relaxed yet polished feel.
- **Modern Sage & Ecru Workwear** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Ecru wide-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look creates a fresh, modern smart-casual ensemble. The sage green blazer and ecru trousers form a soft, sophisticated neutral palette. The crisp white shirt and sleek black boots add definition, while the tan tote ties the warm tones together. The wider leg of the trousers, balanced by the tailored blazer, maintains a contemporary proportion.
  - How to wear: Wear the sage blazer open. / Tuck the white poplin shirt neatly into the ecru trousers to define the waist and emphasize the wide leg. / Ensure the trousers are long enough to cover the top of the ankle boots for an elongated line.
  - Declared deviations: Color palette shifted from warm camel/black to cooler sage/ecru with black accents.; Bottom silhouette changed from straight-leg to wide-leg.; Base layer is a shirt instead of a tee.

**agentic** — human rating: ___/5
- **Classic Tailored Ease** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This outfit is a direct recreation of the inspiration, featuring an oversized camel blazer over a white tee and black straight trousers. The palette is a cohesive neutral mix of camel, white, black, and brown, creating medium contrast. The blend of matte suiting, soft jersey, and smooth leather textures, along with the smart-casual formality, is perfectly aligned.
  - How to wear: Wear the camel blazer open to maintain the relaxed, undefined waist. / Loosely front-tuck the white tee into the trousers to keep a clean line without full tucking. / Ensure trousers fall to a full length or slightly break over the loafers for an elongated leg line.
  - Declared deviations: The owned black trousers are noted as slightly slimmer than the inspiration, but still maintain a straight-leg silhouette.
  - Critic: approved after 0 revision(s); notes: The declared deviation notes the owned black trousers are slightly slimmer than the inspiration. While this is acknowledged, it slightly alters the intended volume balance, making the leg line a bit less relaxed than the inspiration's broader straight leg.
- **Modern Earth Tones** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This outfit maintains the inspiration's relaxed tailored silhouette with an open blazer over a simple base. The palette shifts slightly with sage, but remains minimal and neutral. The straight leg line is preserved, and the textures combine matte suiting, soft jersey, and smooth leather for a polished yet comfortable smart-casual look.
  - How to wear: Wear the sage blazer open to maintain the relaxed, undefined waist. / Loosely front-tuck the white tee into the trousers to keep a clean line without adding bulk. / Ensure the black ankle boots meet the trousers seamlessly to preserve the elongated leg line.
  - Declared deviations: Blazer color is sage green instead of camel, introducing a cooler, modern neutral.; Shoes are black ankle boots instead of brown loafers, offering a sleeker, slightly more contemporary feel.
  - Critic: approved after 1 revision(s); notes: While the sage blazer is a good creative interpretation, the 'oversized' nature of the inspiration's blazer is slightly less pronounced in the 'sage tailored blazer' which appears more fitted, potentially altering the relaxed volume balance slightly. However, it still reads as a relaxed fit.; The black boots, while sleek, introduce a slightly harder contrast with the sage and white than the softer brown loafers would have with camel. This is a stylistic choice that leans more modern, but slightly deviates from the 'medium contrast' of the original palette.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### same-silhouette-different-colour

_Camel blazer removed: a blazer with the same structure in another colour should replace it._

**single_pass** — human rating: ___/5
- **Modern Sage & Black Tailoring** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look maintains the inspiration's core structure: a relaxed blazer over a simple tee, paired with straight trousers and classic loafers. The palette shifts from camel to sage green, but keeps the neutral, minimal feel with black and white, and brown accents.
  - How to wear: Wear the blazer open to maintain the relaxed feel. / Loosely front-tuck the white tee into the trousers to define the waist subtly.
  - Declared deviations: Sage green blazer instead of camel.
- **Monochrome & Modern Tailoring** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Black fitted blazer → Camel oversized single-breasted blazer, Black silk-look camisole → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look creates a sleek, monochromatic base with a black blazer, cami, and trousers, extended by black ankle boots. The tan tote adds a warm, contrasting neutral. The silhouette is more fitted than the inspiration but still maintains a tailored, polished smart-casual vibe.
  - How to wear: Wear the blazer open to maintain ease and show the camisole. / Ensure the black ankle boots create a continuous line with the trousers for elongation.
  - Declared deviations: More fitted blazer and camisole replace the oversized blazer and tee.; Monochromatic black base instead of white and black contrast.; Ankle boots instead of loafers.
- **Relaxed Ecru & Navy for Work** (alternative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Navy fine-knit sweater → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Ecru wide-leg trousers → Black straight-leg trousers, White leather sneakers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look offers a softer, more relaxed take on smart-casual. The navy knit over a white shirt provides a polished top half, balanced by the flowing ecru wide-leg trousers. White sneakers keep it fresh and comfortable, while the tan tote adds structure.
  - How to wear: Layer the navy knit over the white shirt, allowing the shirt collar to peek out for a polished touch. / Ensure the trousers skim the top of the sneakers for an intentional, elongated look.
  - Declared deviations: A fine-knit sweater replaces the blazer, shifting from structured tailoring to soft layering.; Wide-leg trousers replace straight-leg, altering the lower body silhouette.; White sneakers replace loafers for a more casual footwear choice.

**agentic** — human rating: ___/5
- **Sage & Sleek** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: The sage blazer provides a relaxed, tailored top layer, balanced by the straight black trousers for an elongated leg line. The white tee offers a clean, minimal base. Brown loafers and a tan tote complete a cohesive smart-casual look with a neutral, slightly accented palette and polished textures.
  - How to wear: Wear the sage blazer open to maintain the relaxed top layer and highlight the clean base. / Half-tuck the white tee at the front to subtly define the waist, in line with the inspiration's styling.
  - Declared deviations: Blazer color is sage green instead of camel, introducing a cool-toned accent to the neutral palette.
  - Critic: approved after 0 revision(s); notes: The sage blazer, while a good substitute for the 'relaxed tailored top layer', introduces a cool-toned accent that slightly shifts the overall palette from the inspiration's warm camel. This is a declared deviation and well-managed.
- **Sage & Black Contrast** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look creates a modern, smart-casual aesthetic by combining a relaxed sage blazer with a clean white tee and sleek black trousers. The black ankle boots extend the leg line and add polish, while the tan tote introduces a warm, structured element, ensuring a balanced and contemporary feel.
  - How to wear: Wear the sage blazer open to maintain the relaxed top layer and highlight the clean white tee. / Half-tuck the white tee at the front to subtly define the waist, in line with the inspiration's styling. / Ensure the black ankle boots meet the trousers to maintain a seamless, elongated leg line.
  - Declared deviations: Blazer color is sage green instead of camel, altering the specific neutral palette but maintaining the relaxed tailored feel.; Footwear is black ankle boots instead of brown loafers, offering a sleeker, slightly edgier take on polished smart-casual.
  - Critic: approved after 1 revision(s); notes: The shift from a warm camel blazer to a cool sage green blazer, combined with black boots, creates a cooler overall palette than the inspiration's warm camel and brown accents. While declared, it does alter the mood slightly.; The black ankle boots, while sleek and polished, introduce a slightly edgier and more formal feel compared to the classic, softer look of penny loafers. This is a declared deviation and works well within the 'creative' strategy.
- **Tailored Casual with Sneakers** (alternative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, White leather sneakers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This alternative look combines the relaxed tailoring of the sage blazer and black straight trousers with the ease of a white tee and sneakers. The clean lines and minimal palette create a cohesive, modern smart-casual outfit that is comfortable yet polished, with the tan tote adding a refined touch.
  - How to wear: Wear the sage blazer open to emphasize the relaxed silhouette and layered look. / Half-tuck the white tee into the trousers to maintain a subtle waist definition. / Ensure the black trousers are a good length to hit just above the sneakers for a clean line.
  - Declared deviations: Blazer color is sage green instead of camel, introducing a cooler tone to the palette.; Footwear is white leather sneakers instead of brown loafers, shifting the formality slightly more casual while remaining polished.
  - Critic: approved after 1 revision(s); notes: The sage green blazer shifts the primary accent color from warm camel to a cooler tone, altering the overall palette's warmth, though it remains minimal and neutral.; The white sneakers, while a good alternative, do push the formality slightly more casual than the loafers in the inspiration, though this is a declared and acceptable deviation for an 'alternative' strategy.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 1 of 3; sending feedback to the stylist → Stylist proposed 2 look(s); 2 passed validation → Critic approved 2 of 2

### aesthetic-substitute-weekend

_No olive overshirt owned: another casual outer layer takes its role._

**single_pass** — human rating: ___/5
- **Modern Utility Layers** (closest) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Light-wash denim jacket → Olive cotton utility overshirt, Cream cable-knit cardigan → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - Coherence: The look maintains the inspiration's relaxed, layered silhouette with a boxy top half and straight leg. The palette shifts slightly to blue denim and cream, creating a fresh, harmonious casual feel. Textures are balanced between the sturdy denim and soft knit.
  - How to wear: Wear the denim jacket open over the cardigan. / Button up the cream cardigan to create a sweater-like effect. / Ensure the straight-leg jeans have a clean break at the ankle or a small cuff to highlight the sneakers.
  - Declared deviations: The outerwear is a denim jacket instead of a utility overshirt, slightly altering the specific 'utility' feel but keeping the casual jacket role.
- **Earthy & Relaxed Layers** (creative) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Olive cotton utility overshirt, Rust ribbed sweater → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - Coherence: This look creates a warm, earthy palette with the sage green blazer and rust sweater, grounded by classic denim and crisp white sneakers. The overall silhouette remains relaxed and layered, balancing the slightly more tailored blazer with casual elements.
  - How to wear: Wear the sage blazer open and push up the sleeves for a relaxed feel. / Allow the rust sweater to fall naturally for an un-tucked, relaxed look. / Keep the jeans full-length or with a subtle cuff to meet the sneakers.
  - Declared deviations: The outerwear is a blazer, introducing a touch more polish than the utility overshirt, but kept casual by the knit and jeans.; The internal knit is rust instead of cream, creating a warmer colour story.

**agentic** — human rating: ___/5
- **Earthy Weekend Layers** (closest) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Olive cotton utility overshirt, Cream cable-knit cardigan → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - Coherence: The outfit achieves a relaxed, earthy aesthetic through the soft sage green blazer and cream knit, complemented by classic mid-wash straight jeans. The proportions remain balanced with a softly voluminous top half over a clean straight leg, all tied together with casual white sneakers.
  - How to wear: Wear the sage blazer open to mimic the overshirt's relaxed drape. / Ensure the cream cardigan is visible as a distinct layer under the blazer. / Let the layers fall naturally to maintain an undefined waist.
  - Declared deviations: Blazer replaces utility overshirt, bringing a slightly more refined casual feel.; Mid-wash jeans instead of light-wash.
  - Critic: approved after 0 revision(s); notes: The sage tailored blazer, despite its color, fundamentally changes the 'utility' and 'relaxed' aesthetic of the overshirt. A blazer, even a relaxed one, carries a more formal connotation than a utility overshirt, shifting the overall mood from 'effortless weekend ease' to 'smart casual'.; The combination of a tailored blazer with a chunky cable-knit cardigan creates a bulkier and potentially awkward silhouette, especially when worn open. The blazer's lapels and structured shoulders clash with the relaxed, chunky texture of the cardigan, making the layering less seamless and effortless than the inspiration.; While the intention is to maintain soft volume, the tailored nature of the blazer, even with relaxed shoulders, will likely create a more structured and less 'boxy' or 'fluid' top half compared to the inspiration's utility overshirt. This subtly alters the relaxed volume balance.
- **Warm Tones & Denim** (creative) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Light-wash denim jacket → Olive cotton utility overshirt, Rust ribbed sweater → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - Coherence: This look creatively shifts the palette to warmer, richer tones with a rust knit under a light-wash denim jacket, maintaining the relaxed layered feel. The classic straight-leg jeans and white sneakers ground the outfit in casual ease, ensuring the proportions remain balanced with a softer volume on top and a clean line below.
  - How to wear: Wear the denim jacket unbuttoned to keep the layered effect and relaxed silhouette. / Allow the rust sweater to peek out from under the jacket for color contrast. / Ensure the sweater falls loosely to maintain the undefined waist.
  - Declared deviations: Palette shifts from olive/cream to light blue/rust, introducing more contrast.; Denim jacket replaces cotton utility overshirt, changing texture.; Rust knit replaces cream knit.
  - Critic: approved after 0 revision(s); notes: The palette shifts from the inspiration's earthy olive/cream to a warmer light blue/rust combination, which is a declared deviation. While coherent, it moves away from the specific 'earthy, soft palette' of the DNA.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 2 of 2

### category-substitute-dress

_Matching aesthetic with different categories: slip dress recreated by a top + skirt two-piece._

**single_pass** — human rating: ___/5
- **Sleek Satin & Structured Blazer** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - Coherence: This look creates a sophisticated evening ensemble by pairing the fluid champagne satin skirt and black camisole (mimicking a slip dress) with a structured black blazer. The black boots maintain the sleek, slightly edgy feel, and the overall palette is elegant and cohesive.
  - How to wear: Ensure the black camisole is tucked smoothly into the champagne satin skirt to create a seamless column effect. / Wear the black blazer open to maintain the layering and highlight the silhouette of the top and skirt.
  - Declared deviations: The base is a two-piece (cami + skirt) instead of a single dress, but achieves a similar column silhouette.; A fitted blazer replaces a cropped biker jacket, offering a more polished rather than overtly edgy feel.; Ankle boots replace strappy heels, providing a more grounded and modern take on evening footwear.
  - Gaps: Gold hoop earrings (optional)
- **Modern Minimalist Edge** (alternative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Black cropped leather biker jacket, Black silk-look camisole → extra, Black straight-leg trousers → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - Coherence: This look offers a modern, minimalist take on the inspiration. The monochromatic black base (cami + trousers) provides a sleek column, while the camel oversized blazer adds a chic, contrasting structured layer. The black boots maintain a cohesive, polished feel.
  - How to wear: Tuck the black camisole into the black trousers for a seamless, elongated silhouette. / Wear the camel blazer open to showcase the monochromatic base and maintain a relaxed yet polished vibe.
  - Declared deviations: The base is a monochrome black camisole and trousers, creating a different type of 'long line' than a fluid dress.; An oversized camel blazer replaces a cropped black biker jacket, shifting the palette and proportion of the outer layer to a more relaxed yet still structured feel.; The overall mood is more minimalist and less overtly 'edgy' than the inspiration.
  - Gaps: Gold hoop earrings (optional)

**agentic** — human rating: ___/5
- **Sleek Noir Evening** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - Coherence: This outfit creates a cohesive evening look by combining a black satin camisole and champagne satin midi skirt to form a fluid column. The black fitted blazer adds a structured, dark layer for contrast, while black ankle boots maintain a sleek and polished feel. The palette is sophisticated and the textures play between soft satin and crisp suiting.
  - How to wear: Ensure the black camisole is tucked smoothly into the champagne skirt to create a seamless, long column line. / Wear the black blazer open to maintain the layered look and reveal the fluid base. / Push up the blazer sleeves slightly to enhance the 'short structured layer' feel and add a relaxed touch.
  - Declared deviations: The base is a two-piece (cami and skirt) instead of a dress, and the color is champagne/black instead of emerald.; The 'tough edge' comes from a structured blazer instead of a leather biker jacket, making it slightly less edgy and more polished.; Ankle boots replace strappy heels, shifting the shoe style towards a more contemporary, sleek look.
  - Gaps: Gold hoop earrings (optional)
  - Critic: approved after 0 revision(s); notes: The 'tough edge' essential trait from the leather biker jacket is lost. The black fitted blazer, while structured, leans more towards classic elegance than edgy, which significantly alters the core aesthetic of the inspiration.; The black camisole and champagne skirt, while creating a column, introduce a strong color block at the waist that breaks the 'long fluid column' more distinctly than a single slip dress would. The inspiration's column was unbroken by color.; The black ankle boots, while sleek, are a more casual and heavier choice than strappy heels for an 'evening glamour' aesthetic, slightly pulling the look away from the inspiration's delicate elegance.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### multiple-substitutes-distinct

_Several reasonable substitutes: closest and creative looks must differ._

**single_pass** — human rating: ___/5
- **Classic Tailored Neutrals** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look maintains the inspiration's core palette of camel, white, and black with brown accents, creating a cohesive and timeless smart-casual ensemble. The oversized blazer balances the straight trousers for a modern, relaxed yet polished silhouette.
  - How to wear: Wear the blazer open to maintain the relaxed feel. / Loosely front-tuck the white tee to define the waist subtly without disrupting the overall relaxed silhouette.
- **Modern Sage & Black Contrast** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look creates a sophisticated palette with sage green, crisp white, and black, offering a modern twist on the original. The slightly more structured white shirt and sleek ankle boots elevate the formality a touch while retaining the relaxed blazer proportion.
  - How to wear: Wear the blazer open to showcase the clean lines of the shirt. / Consider a partial tuck of the white shirt to maintain a relaxed yet put-together look.
  - Declared deviations: Changed blazer color from camel to sage green for a modern feel.; Substituted the casual tee for a crisper white shirt.; Replaced brown loafers with black ankle boots for a sleeker, more cohesive leg line.
- **Relaxed Ecru & Navy Palette** (alternative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, Navy fine-knit sweater → White crew-neck t-shirt, Ecru wide-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look explores a softer, warmer neutral palette with camel, navy, and ecru. The wide-leg trousers create a different proportion than the inspiration, leaning into a more relaxed yet still tailored silhouette, balanced by the oversized blazer.
  - How to wear: Wear the blazer open to highlight the vertical line of the outfit. / Ensure the wide-leg trousers skim the top of the loafers for an elongated effect.
  - Declared deviations: Changed the base layer from a white tee to a navy fine-knit sweater.; Swapped black straight-leg trousers for ecru wide-leg trousers, altering the bottom silhouette and color.; Introduces a softer, warmer overall palette.

**agentic** — human rating: ___/5
- **Classic Camel & Black Tailoring** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This outfit maintains the inspiration's core aesthetic by combining a relaxed camel blazer with a white tee and black trousers, creating a balanced silhouette. The neutral palette is preserved, with warm camel and brown accents against crisp white and black, ensuring a polished smart-casual look suitable for work.
  - How to wear: Wear the camel blazer open to maintain the relaxed silhouette and show the base layer. / Loosely front-tuck the white tee to hint at the waist without being overtly defined. / Ensure trousers fall straight to maintain the elongated leg line.
  - Declared deviations: The black trousers are slightly slimmer than the original, making the overall silhouette a bit more streamlined.
  - Critic: approved after 0 revision(s); notes: The declared deviation notes the black trousers are slightly slimmer than the original. While this is a minor difference, it slightly reduces the 'straight' and 'full-length' volume of the inspiration's trousers, making the leg line a touch more streamlined than the relaxed original.
- **Modern Sage & Ecru Workwear** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Ecru wide-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This creative interpretation updates the palette with soft sage and ecru, offering a lighter, contemporary feel while retaining the smart-casual tailoring. The wide-leg trousers balance the relaxed blazer, creating an intentional, flowing silhouette, while the white tee and brown loafers maintain polish and ease.
  - How to wear: Wear the sage blazer open to showcase the clean base and maintain a relaxed vibe. / Loosely front-tuck the white tee to define the waist against the wider trousers. / Ensure the ecru trousers fall to a full length to maintain the elongated leg line.
  - Declared deviations: The palette shifts from warm camel/black to cooler sage/ecru.; The trousers are wide-leg instead of straight, altering the lower body volume.
  - Critic: approved after 0 revision(s); notes: While the wide-leg trousers are an intentional creative choice, the inspiration's volume balance was 'volume up top (oversized blazer) balanced by a slim straight trouser'. This look shifts to volume on both top and bottom, which is a valid proportion but a significant departure from the inspiration's specific balance.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 2 of 3; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

### missing-item-optional

_Missing wardrobe item: no hat owned; it must be an optional gap, never an invented garment._

**single_pass** — human rating: ___/5
- **Polished Travel Layers** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - Coherence: This look maintains the inspiration's core elements: a neutral outer layer, a navy knit, ecru wide-leg bottoms, and white sneakers. The overall palette is harmonious and the proportions balance the oversized blazer with the fluid trousers.
  - How to wear: Wear the camel blazer open to maintain a long, vertical line. / Ensure the navy knit is tucked or neatly layered to create a smooth transition to the high-rise trousers.
  - Declared deviations: The outer layer is an oversized blazer instead of a trench coat.
  - Gaps: Wide-brim straw-coloured hat (optional)
- **Modern Navy & Cream Ensemble** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Navy fine-knit sweater → Beige belted double-breasted trench coat, White crew-neck tee → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, Brown leather loafers → White minimal sneakers
  - Coherence: This look creates a fresh palette of navy, white, ecru, and brown. The proportions are balanced with the slim knit over a t-shirt and fluid wide-leg trousers. The overall feel is smart-casual, leaning into a slightly more preppy or minimalist aesthetic.
  - How to wear: Layer the navy knit over the white tee, allowing a small hint of white to show at the neckline for contrast. / Ensure the trousers skim the top of the loafers for a clean line.
  - Declared deviations: No long outer layer; the navy knit functions as the main top layer.; The shoes are loafers, adding a different kind of polish than sneakers.; The color palette shifts to incorporate brown and more prominent white.
  - Gaps: Wide-brim straw-coloured hat (optional)
- **Monochromatic Chic with a Pop** (alternative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Beige belted double-breasted trench coat, Black silk-look camisole → Navy fine-knit crew-neck sweater, Black straight-leg trousers → Ecru high-rise wide-leg trousers, Black leather ankle boots → White minimal sneakers, Tan structured tote → extra
  - Coherence: This look creates a chic, monochromatic black column with a structured blazer, offering a sophisticated alternative. The tan tote provides a warm, contrasting accent, while the ankle boots maintain comfort and polish. The proportions are sleek and streamlined.
  - How to wear: Wear the black camisole tucked into the black trousers for a seamless, elongated look. / Carry the tan tote to break up the monochromatic black and add a sophisticated touch.
  - Declared deviations: Palette shifts to primarily black with a tan accent, rather than beige/navy/ecru.; Silhouette is more streamlined (straight-leg trousers) rather than wide-leg.; Outer layer is a fitted blazer, not a long trench.; Shoes are ankle boots, not sneakers.
  - Gaps: Wide-brim straw-coloured hat (optional)

**agentic** — human rating: ___/5
- **Polished Travel Layers** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - Coherence: This outfit maintains the inspiration's smart-casual aesthetic by pairing a tailored camel blazer with a fine navy knit and fluid ecru wide-leg trousers. The neutral palette is preserved, and the combination of structured and flowing pieces creates a balanced silhouette, anchored by comfortable white sneakers.
  - How to wear: Wear the camel blazer unbuttoned to maintain a long, vertical line and showcase the knit beneath. / Ensure the navy knit is tucked neatly into the high-rise ecru trousers to define the waistline. / Allow the wide-leg trousers to drape fluidly, reaching just above the sneakers.
  - Declared deviations: The outer layer is a blazer, not a long trench coat, resulting in a shorter vertical line and no belted waist for the outerwear.; The wide-brim hat is omitted due to unavailability.
  - Gaps: Wide-brim straw-coloured hat (optional)
  - Critic: approved after 0 revision(s); notes: The camel oversized blazer, while a good neutral, fundamentally alters the silhouette and the 'long vertical line' essential trait of the inspiration. A blazer, even an oversized one, does not provide the same long, flowing line or the belted waist definition of a trench coat.; The inspiration relies on the long, belted trench to create a specific vertical line and waist definition. The blazer, being shorter and unbelted, breaks this line higher, changing the overall proportion and volume balance from the inspiration's 'long outer layer and wide trousers framing a fitted knit'.; The styling instruction to 'tuck neatly' the knit into the trousers is good for waist definition, but the overall effect with the shorter blazer loses some of the relaxed, layered elegance of the trench, making the outfit feel slightly less cohesive as a 'polished travel layer' ensemble.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### missing-key-piece

_Genuine gap: closet without any outer layer must report an essential outerwear gap._

**single_pass** — human rating: ___/5
- **Minimalist Workwear Base** (closest) — 3/5 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers
  - Coherence: This look establishes the core minimalist and smart-casual foundation of the inspiration, with a classic black and white palette accented by warm brown shoes. The straight-leg trousers provide a clean, elongated line.
  - How to wear: Wear the white tee untucked or with a very subtle front tuck for a relaxed feel. / Ensure trousers are the correct length to skim the top of the loafers.
  - Declared deviations: Absence of the key tailored blazer, which significantly alters the overall silhouette and layering.
  - Gaps: Camel oversized single-breasted blazer (essential); Tan structured tote bag (optional)
- **Monochromatic Base with Classic Stripes** (creative) — 3/5 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Navy Breton striped tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers
  - Coherence: This look uses a darker, more cohesive palette of navy and black, creating an elongated and sophisticated line. The Breton stripes add visual interest while keeping the overall feel classic and minimal. The sleek boots enhance the polished aesthetic.
  - How to wear: Allow the Breton tee to fall loosely over the trousers or perform a very subtle front tuck. / Ensure trousers fall neatly over the ankle boots for a continuous line.
  - Declared deviations: Absence of the key tailored blazer.; Introduction of a striped top instead of solid white, and black boots instead of brown loafers, shifting the palette to a cooler, more monochromatic feel.
  - Gaps: Camel oversized single-breasted blazer (essential); Tan structured tote bag (optional)

**agentic** — human rating: ___/5
- No looks: The wardrobe lacks a suitable 'relaxed tailored top layer' (blazer or similar structured outerwear) which is an essential trait and key piece of the inspiration's silhouette and identity. Without this core garment, no coherent interpretation of the outfit can be formed.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 0 of 2; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

### formal-occasion-constraint

_Formal occasion: no casual sneakers, denim jacket or jeans for an evening event._

**single_pass** — human rating: ___/5
- **Green Dress & Blazer Evening** (closest) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Forest green wrap midi dress → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - Coherence: This look maintains the core color palette of deep green and black. The fluid line of the wrap dress is contrasted by the structured blazer, creating a polished silhouette suitable for an event. The sleek boots ground the outfit with a modern edge.
  - How to wear: Wear the blazer open over the dress to maintain the long line of the dress and the layering effect. / Ensure the dress is well-steamed for a fluid drape.
  - Declared deviations: The blazer is fitted rather than cropped, altering the exact proportion of the top layer, but still provides structure and contrast.; Ankle boots replace strappy heels, shifting the shoe style to a slightly more grounded, yet still sleek, option.
  - Gaps: Gold hoop earrings (optional)
- **Satin & Silk Two-Piece with Blazer** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - Coherence: This look creates a cohesive column silhouette using a black camisole and champagne satin skirt, topped with a black blazer. The material combination of silk-look and satin provides the necessary sheen, while the black blazer and boots maintain the edgy contrast.
  - How to wear: Tuck the camisole into the skirt to create a seamless, column-like effect. / Wear the blazer open to showcase the fluid lines of the top and skirt. / Consider adding a belt at the waist to define the silhouette if desired.
  - Declared deviations: The 'dress' is created from a two-piece set, changing the color from green to black and champagne.; The blazer is fitted rather than cropped, altering the exact proportion of the top layer, but still provides structure and contrast.; Ankle boots replace strappy heels, shifting the shoe style to a slightly more grounded, yet still sleek, option.
  - Gaps: Gold hoop earrings (optional)
- **Modern Evening with Sage & Black** (alternative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Sage tailored blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Black straight-leg trousers → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - Coherence: This look creates a modern, sophisticated evening outfit by pairing a sleek black camisole and trousers for a continuous column, then adding a contrasting sage blazer. The palette is muted but elegant, suitable for an event.
  - How to wear: Ensure the camisole is neatly tucked into the trousers for a seamless look. / Wear the blazer open to highlight the sleek black base and create vertical lines. / Roll up blazer sleeves slightly for a more relaxed, modern feel.
  - Declared deviations: The 'dress' is replaced by a black camisole and black trousers, creating a different silhouette and color for the base.; The outerwear is a sage blazer, changing the color from black and the material from leather.; Ankle boots replace strappy heels, shifting the shoe style to a slightly more grounded, yet still sleek, option.
  - Gaps: Gold hoop earrings (optional)

**agentic** — human rating: ___/5
- **Sleek Green & Black Evening** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Forest green wrap midi dress → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - Coherence: This outfit blends the fluid elegance of the wrap dress with the structured formality of the blazer and sleekness of the boots. The forest green and black create a high-contrast palette, while the different textures (jersey, suiting, leather) add depth. The wrap dress's defined waist is subtly highlighted by the blazer's fit.
  - How to wear: Wear the blazer open to maintain the long line of the dress and the layering effect. / Ensure the wrap dress is tied to create a defined waist.
  - Declared deviations: The dress is a jersey wrap dress with a defined waist, not a satin slip dress, shifting the material and silhouette slightly.; A fitted blazer replaces the cropped biker jacket, giving a more formal rather than edgy feel to the 'tough' element.; Ankle boots replace strappy heels, providing a more grounded, sleek look.
  - Gaps: Gold hoop earrings (optional)
  - Critic: approved after 0 revision(s); notes: The essential trait of 'sheen against a tough edge' is lost. The jersey wrap dress lacks the lustrous sheen of satin, and the suiting blazer, while structured, doesn't provide the 'tough edge' of a leather biker jacket. This significantly alters the aesthetic from edgy glamour to more classic smart-casual.; The wrap dress creates a defined waist and an A-line silhouette, which deviates from the 'long fluid column' and 'soft waist definition' of the slip dress. The blazer, while fitted, doesn't fully restore the column effect or the specific volume balance of a cropped jacket over a straight slip.; The combination of a jersey wrap dress, a suiting blazer, and sleek ankle boots leans more towards a business-casual or polished daytime look rather than the sleek evening glamour intended by the inspiration. The materials, while individually fine, don't elevate each other to the desired evening aesthetic.
- **Modern Minimalist Evening** (alternative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - Coherence: This look creates a modern evening ensemble by pairing a lustrous champagne satin skirt with a black silk-look camisole, forming a seamless fluid column. The black fitted blazer introduces structure and a contrasting texture, while black ankle boots complete the sleek, slightly edgy aesthetic. The palette is sophisticated, with the champagne providing a soft glow against the stark black.
  - How to wear: Tuck the black camisole neatly into the champagne satin skirt to create a continuous, fluid line. / Wear the blazer open to showcase the fluid separates and maintain the layering contrast. / Ensure the skirt sits high on the waist to elongate the body and maintain the column silhouette.
  - Declared deviations: Uses a satin skirt and camisole combo instead of a single slip dress, changing the color from emerald to champagne and black.; A fitted blazer replaces the cropped biker jacket, offering a more classic 'tough edge' rather than overtly biker.; Ankle boots replace strappy heels, providing a sleek, grounded finish.
  - Gaps: Gold hoop earrings (optional)
  - Critic: approved after 0 revision(s); notes: The 'tough edge' is interpreted through a classic blazer rather than a biker jacket, making it more polished than overtly edgy. This is a declared deviation and a reasonable creative interpretation given the wardrobe.; The champagne color of the skirt, while lustrous, is a significant departure from the emerald green of the inspiration. However, it still creates a sophisticated evening palette.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 2 of 2

### shopping-disabled

_Shopping disabled: gaps carry no sourcing hints._

**single_pass** — human rating: ___/5
- **Polished Travel Layers with Camel Blazer** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - Coherence: This look maintains a cohesive smart-casual palette of camel, navy, and ecru. The oversized blazer provides a relaxed yet polished structure over the slim knit and fluid wide-leg trousers, creating a comfortable and put-together travel ensemble.
  - How to wear: Wear the navy fine-knit sweater tucked into the ecru wide-leg trousers to maintain the high-rise proportion. / Keep the camel oversized blazer open to showcase the layers and maintain a relaxed feel.
  - Declared deviations: The outerwear is an oversized blazer instead of a long belted trench, which alters the vertical line and waist definition. However, the overall polished and relaxed mood is preserved.
  - Gaps: Wide-brim straw-coloured hat (optional)
- **Sage and Ecru Layers with a Modern Twist** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Sage tailored blazer → Beige belted double-breasted trench coat, White poplin shirt → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, Brown leather loafers → White minimal sneakers
  - Coherence: This look presents a fresh, modern smart-casual palette with sage, white, and ecru, grounded by classic brown loafers. The tailored blazer over the crisp shirt and fluid trousers creates a sophisticated yet comfortable ensemble, perfect for travel with a slightly elevated feel.
  - How to wear: Button the white poplin shirt and tuck it neatly into the ecru trousers for a clean silhouette. / Wear the sage blazer open to maintain a relaxed, modern feel. / Roll up the sleeves of the blazer slightly to add a casual touch.
  - Declared deviations: A different color palette (sage and white instead of beige and navy).; Smarter footwear (loafers instead of sneakers).; No long vertical line from the outerwear.
  - Gaps: Wide-brim straw-coloured hat (optional)

**agentic** — human rating: ___/5
- **Polished Neutral Layers** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - Coherence: The outfit creates a smart-casual, relaxed yet put-together look. The camel blazer offers a structured outer layer that works with the fluid wide-leg trousers, anchored by the classic navy knit. The overall palette is soft and neutral, making it versatile for travel.
  - How to wear: Wear the blazer open to maintain a relaxed feel and allow the knit to show. / Ensure the knit is neatly tucked or hits at the waistband of the trousers for a clean line.
  - Declared deviations: The outer layer is a blazer instead of a long trench, which shortens the vertical line and changes the overall volume balance slightly.; The belted waist definition of the trench is absent.
  - Gaps: Wide-brim straw-coloured hat (optional)
  - Critic: approved after 0 revision(s); notes: The camel oversized blazer, while a good color match, fundamentally changes the silhouette and proportion by replacing the long belted trench. It loses the 'long vertical line' and 'belted waist definition' which are essential traits of the inspiration.; The oversized blazer, while stylish, creates a different volume balance than the inspiration's long, belted trench. The shorter length and lack of waist definition from the blazer disrupt the intended long vertical line and the framing of the fitted knit and wide trousers.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

### user-exclusion-and-keep

_Preference adherence: excluded pieces never appear, kept pieces always do._

**single_pass** — human rating: ___/5
- **Classic Camel & Black with a Crisp Shirt** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: The outfit maintains the inspiration's smart-casual tailored aesthetic with a classic camel, white, and black palette. The relaxed blazer balances the straight trousers, while the white shirt offers a clean contrast. Black boots provide a cohesive, polished finish.
  - How to wear: Wear the blazer open to maintain the relaxed feel. / Loosely front-tuck the white shirt into the trousers. / Ensure trousers fall neatly over the ankle boots.
  - Declared deviations: Swapped brown loafers for black ankle boots as per user preference.; Replaced a t-shirt with a button-down shirt for a slightly more formal work-appropriate base.
- **Modern Sage & Navy with Tailored Edge** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, Navy fine-knit sweater → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look offers a fresh palette with sage green, navy, and black, maintaining the tailored smart-casual feel. The slightly more structured blazer and fine-knit sweater create a refined silhouette, balanced by the straight trousers and sleek boots. The tan tote adds a touch of warmth.
  - How to wear: Wear the blazer open to showcase the tonal base. / Ensure the navy knit is neatly tucked or falls smoothly over the waistband. / Allow trousers to break cleanly over the ankle boots.
  - Declared deviations: Introduces a new color palette with sage and navy.; Uses a fine-knit sweater for the base layer instead of a t-shirt.

**agentic** — human rating: ___/5
- **Modern Sage & Navy Smart-Casual** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, Navy fine-knit sweater → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - Coherence: This look creatively reinterprets the inspiration by introducing a contemporary color palette of sage green and navy, while preserving the core silhouette. The relaxed sage blazer over a fine navy knit creates a sophisticated top half, balanced by the classic black straight trousers. Black ankle boots provide a sleek, modern finish, maintaining the polished smart-casual formality, while the tan tote offers a warm, structured accent.
  - How to wear: Wear the sage blazer open to keep the relaxed, flowing lines. / Ensure the navy knit is neatly tucked or falls smoothly over the waistband of the trousers. / Allow the trousers to fall over the ankle boots for a clean, elongated leg line.
  - Declared deviations: The palette shifts from warm neutrals to cooler tones (sage, navy, black).; The base layer is a fine-knit sweater instead of a t-shirt, adding a slightly more refined texture.; Footwear is sleek ankle boots instead of loafers, creating a more contemporary edge.
  - Critic: approved after 0 revision(s); notes: The sage blazer is described as 'tailored, relaxed shoulders' while the inspiration's blazer is 'oversized, relaxed'. The image of the sage blazer appears slightly more fitted than the inspiration's, which could subtly alter the relaxed volume balance if not styled carefully.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

### ambiguous-not-an-outfit

_Ambiguous/non-outfit photo: no looks, honest reason._

**single_pass** — human rating: ___/5
- No looks: We couldn't find a wearable outfit in this image. Try a clearer full-outfit photo.

**agentic** — human rating: ___/5
- No looks: We couldn't find a wearable outfit in this image. Try a clearer full-outfit photo.
