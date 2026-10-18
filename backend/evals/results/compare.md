# Rewear — engine comparison (live Gemini)

Variants: `single_pass` {'styling_engine': 'single_pass'}, `agentic` {'styling_engine': 'agentic'}

## Summary

| Variant | Objective checks | Invalid owned ids | Looks returned | With styling instructions | Critic rejections | No-look runs (legit / suspect) | Median total | Max total |
|---|---|---|---|---|---|---|---|---|
| single_pass | 16/16 | 0 | 25 | 25 | 0 | 2 / 1 | 11.6 s | 22.2 s |
| agentic | 15/16 | 0 | 15 | 15 | 20 | 3 / 1 | 34.8 s | 72.4 s |

### Median per-stage latency (ms) and cost counters

| Variant | retrieval_ms | knowledge_ms | composer_ms | stylist_ms | critic_image_prep_ms | critic_ms | revision_ms | total_ms | passes | stylist_calls | critic_calls | critic_images | critic_image_tokens | stylist_tokens | critic_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| single_pass | 22 | 0 | 11540 | – | – | – | – | 11584 | – | – | – | – | – | – | – |
| agentic | 26 | 0 | 11685 | 20548 | 53 | 11552 | 14853 | 34807 | 2 | 2 | 2 | 12 | 3096 | 16866 | 13966 |

`revision_ms` = model time in passes after the first; `critic_ms` excludes image preparation (`critic_image_prep_ms`). Values are medians per request.

## Looks per case (human rating fields are intentionally blank)

### real-denim-skirt

_The reported failure: white tucked button-down + high-waisted denim midi skirt + sneakers, styled from a real 7-piece wardrobe with no white shirt or denim skirt. A strong answer protects the defined waist and relaxed mood (e.g. the belted shirt-dress, or sweater + skirt with a tuck and casual shoes) instead of stacking dressy substitutes and an unneeded jacket._

**single_pass** · 14.5 s · all objective checks pass · human rating: ___/5
- **Modern Midi Skirt & Sweater Look** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Burgundy satin midi skirt → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Fully tuck the black sweater into the high-waisted satin skirt to define the waist. / Consider a half-tuck for a more relaxed vibe if preferred.
  - Declared deviations: The top is a soft sweater instead of a crisp shirt, changing the textural contrast.; The skirt is satin and burgundy, differing from the denim and mid-blue of the inspiration, but maintains the midi-skirt silhouette.
- **Relaxed Denim & Shirt Dress Remix** (creative) — 2/2 pieces already in your closet · No new purchase needed
  - Pieces: Tan belted shirt dress → White cotton button-down shirt + High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Wear the tan belted shirt dress open over the black wide-leg jeans, using the belt to cinch the waist of the dress. / Alternatively, wear the shirt dress partially buttoned and belted, allowing the jeans to peek out for a layered effect. / Roll up the sleeves of the shirt dress for a more relaxed look.
  - Declared deviations: The shirt dress is layered over jeans, creating a different layering dynamic than the simple tucked shirt and skirt.; The bottom is wide-leg jeans instead of a midi skirt, changing the specific silhouette but maintaining the elongated lower line and casual mood.

**agentic** · 29.0 s · all objective checks pass · human rating: ___/5
- **Modern Denim & Knit** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Black high-rise wide-leg jeans → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Half-tuck the front of the black sweater into the jeans to define your waist. / Ensure the jeans fall long over your sneakers to maintain the elongated lower line.
  - Declared deviations: Flipped color contrast (dark top/bottom, light shoes instead of light top, mid-tone bottom, light shoes).; Wide-leg jeans instead of a midi skirt.; Soft knit top instead of crisp cotton shirt.
  - Gemini critic: approved after 0 revision(s); notes: The black crewneck sweater, with its slightly cropped and boxy silhouette, does not lend itself well to a half-tuck into high-waisted wide-leg jeans. This styling choice will likely create an awkward bulk at the waist and disrupt the desired smooth, defined waistline.; The inspiration features a crisp, structured cotton shirt, while this look uses a soft, relaxed knit sweater. This significantly changes the material interplay and the 'crisp' aspect of the 'relaxed but put-together' aesthetic.; The flipped color palette (dark top/bottom) combined with the soft knit and matte denim lacks the crisp contrast and material interplay of the inspiration's white cotton and rigid mid-blue denim. While declared, it's a significant shift in visual texture and lightness.
- **Effortless Tan Shirtdress** (creative) — 2/2 pieces already in your closet · No new purchase needed
  - Pieces: Tan belted shirt dress → White cotton button-down shirt + High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Cinch the belt of the shirtdress at your natural waist to create a defined silhouette. / Roll up the sleeves of the shirtdress to add a relaxed, effortless touch, mirroring the inspiration's styling.
  - Declared deviations: Monochromatic tan palette instead of white and mid-blue contrast.; A single dress replacing a top and skirt.; No front slit on the dress.
  - Gemini critic: approved after 0 revision(s); notes: The monochromatic tan palette lacks the crisp white and mid-blue contrast of the inspiration, resulting in a softer, less graphic look. While a declared deviation, it does alter the visual impact.; The absence of a front slit on the dress removes the element of movement and subtle edge present in the inspiration's skirt.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 2 of 3; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

### real-emerald-evening

_Evening slip dress + cropped leather jacket + heels, from the real wardrobe (satin skirt, tweed and suede jackets, no heels)._

**single_pass** · 9.6 s · all objective checks pass · human rating: ___/5
- **Satin & Tweed Evening Edge** (closest) — 2/4 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Cream embellished tweed jacket → Black cropped leather biker jacket, Burgundy satin midi skirt → Emerald satin bias-cut slip dress
  - How to wear: Pair the burgundy satin skirt with a fitted black or dark burgundy camisole or fine-knit top to mimic a slip dress. / Wear the cream tweed jacket open over the top to highlight the fluid column underneath.
  - Declared deviations: Color palette shifted from emerald/black to burgundy/cream/gold.; Material contrast is satin/tweed instead of satin/leather, creating a softer edge.; Two pieces (skirt + implied top) replace a single dress.
  - Gaps: Black strappy heeled sandals (essential); Gold hoop earrings (optional)

**agentic** · 44.0 s · all objective checks pass · human rating: ___/5
- **Modern Evening Edge** (creative) — 2/4 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Cream embellished tweed jacket → Black cropped leather biker jacket, Burgundy satin midi skirt → Emerald satin bias-cut slip dress
  - How to wear: Tuck the black sweater neatly into the burgundy satin skirt to create a seamless column effect. / Wear the cream tweed jacket open to highlight the base layer and maintain the cropped silhouette.
  - Declared deviations: Color palette shifted from emerald/black to burgundy/black/cream.; Material contrast is satin/tweed instead of satin/leather.
  - Gaps: Black strappy heeled sandals (essential); Gold hoop earrings (optional)

### real-camel-work

_Camel blazer + tee + straight trousers + loafers for work, from the real wardrobe (no blazer, no tee, no loafers): expect honest gaps or declared deviations._

**single_pass** · 12.9 s · all objective checks pass · human rating: ___/5
- **Cream Tweed & Black Denim** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Cream embellished tweed jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - How to wear: Wear the black sweater untucked or with a slight front tuck to maintain a relaxed feel. / Ensure the tweed jacket is worn open to showcase the base layer and maintain the layering style.
  - Declared deviations: More casual overall due to jeans and sneakers.; The outerwear is a cropped tweed jacket rather than an oversized blazer.
  - Gaps: Tan structured tote bag (optional)
- **Modern Shirtdress with Casual Layers** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Tan belted shirt dress → Black straight-leg trousers + White crew-neck t-shirt, White and black platform sneakers → Brown leather penny loafers
  - How to wear: Wear the shirtdress unbelted for a more relaxed silhouette, or loosely belted to define the waist. / Keep the rust jacket open to maintain the layered effect and showcase the shirtdress. / Consider rolling up the sleeves of the jacket for an effortless feel.
  - Declared deviations: Uses a dress as the core instead of separate top and bottom.; More earthy and less strictly neutral palette.; Slightly more casual overall due to the suede jacket and sneakers.
  - Gaps: Tan structured tote bag (optional)

**agentic** · 50.9 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): Look 0 is rejected due to critical deviations from essential DNA traits and a lack of overall coherence, while Look 1 is a creative reinterpretation that needs minor revisions to better align with the inspiration's proportions and tailored feel. What didn't work: Polished Neutral Contrast: [critical] fidelity: The essential trait of a 'straight, elongated leg line' is lost. The inspiration uses straight-leg trousers, while this look uses a fluid A-line satin midi skirt. This changes the silhouette, movement, and overall aesthetic significantly. Fix: Replace the 'Burgundy satin midi skirt' with 'Black high-rise wide-leg jeans' to achieve a more elongated and straight-leg line, albeit with a different material and formality.; Relaxed Shirtdress Layers: [major] fidelity: The essential trait of a 'straight, elongated leg line' is reinterpreted as a dress, which fundamentally changes the two-piece structure of the inspiration. While the shirtdress provides an elongated line, it's not a 'leg line' in the same sense as trousers. Fix: To achieve a more direct 'leg line' interpretation, the 'Black high-rise wide-leg jeans' could be paired with a top and the 'Rust suede-like jacket'. However, this would be a different outfit strategy.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 0 of 2; sending feedback to the stylist → Stylist proposed 2 look(s); 2 passed validation → Critic approved 0 of 2

### real-satin-material-challenge

_Material challenge: satin slip skirt dressed down with a slouchy sweatshirt and sneakers. The burgundy satin skirt fits; the stylist must keep the dressed-down mood._

**single_pass** · 7.2 s · all objective checks pass · human rating: ___/5
- **Burgundy Satin & Black Knit Contrast** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - How to wear: Front-tuck the black sweater to define the waist and showcase the skirt. / Wear the burgundy satin skirt at your natural waist for optimal proportion.
  - Declared deviations: Darker, richer color palette (black and burgundy vs. heather grey and champagne); Knit sweater instead of fleece sweatshirt

**agentic** · 24.9 s · all objective checks pass · human rating: ___/5
- **Burgundy Satin & Black Knit Chill** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - How to wear: Half-tuck the front of the black sweater into the skirt to define your waist, mimicking the inspiration's proportions. / Wear the sweater slightly pulled out to maintain its relaxed volume over the skirt.
  - Declared deviations: Top is black knit instead of heather grey fleece.; Skirt is burgundy A-line instead of champagne bias-cut.
  - Gemini critic: approved after 0 revision(s); notes: The black crewneck sweater, while relaxed, is a knit and not an oversized fleece sweatshirt, which slightly reduces the 'sporty' aspect of the high-low contrast.; The burgundy satin midi skirt appears to be more A-line than bias-cut, which slightly alters the fluid drape compared to the inspiration.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 1 of 3; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

### real-no-good-outfit

_No good outfit exists: black-tie tuxedo look from a casual 7-piece wardrobe. A good system admits the gap instead of forcing a match._

**single_pass** · 4.1 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): The inspiration is a very specific and strict black-tie tuxedo outfit. Unfortunately, all available owned garments are either casual or smart-casual, and none match the high formality, tailored silhouette, or specific garment types (tuxedo jacket, dress shirt, tuxedo trousers, patent oxfords) required to recreate even a 'creative' interpretation of this look. There are no suitable formal items in the closet.

**agentic** · 7.3 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): The user's wardrobe lacks any formal wear, particularly the black tailored pieces and crisp white shirt essential for a black-tie look. All available garments are casual to smart-casual, making it impossible to recreate the strict formality and specific aesthetic of the inspiration outfit.
- Workflow: Stylist proposed 0 look(s); 0 passed validation

### exact-camel-work

_Exact garment matches: every key piece of the camel work look is owned._

**single_pass** · 15.3 s · all objective checks pass · human rating: ___/5
- **Classic Smart-Casual Tailoring** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the camel blazer open over the white tee. / Loosely front-tuck the white tee into the black trousers. / Pair with brown loafers for a classic finish.
- **Modern Sage & Ecru Smart-Casual** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Ecru wide-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the sage blazer open over the white shirt. / Partially tuck the white shirt into the ecru wide-leg trousers to define the waist. / Ensure the trousers skim the top of the ankle boots for a clean line.
  - Declared deviations: Changed primary colour palette from camel/black to sage/ecru.; Introduced a wide-leg silhouette for the trousers.
- **Relaxed Monochrome with a Pop** (alternative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Black fitted blazer → Camel oversized single-breasted blazer, Black silk-look camisole → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, White leather sneakers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the black blazer open over the black camisole. / Ensure the black camisole is neatly tucked into the black trousers to maintain a sleek line. / Pair with white sneakers for a fresh, modern contrast.
  - Declared deviations: Shifted to a monochrome black base with white and tan accents.; Introduced sneakers for a more relaxed, modern footwear choice.; Used a fitted blazer instead of an oversized one.

**agentic** · 32.2 s · all objective checks pass · human rating: ___/5
- **Classic Tailored Neutrals** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the camel blazer open to maintain the relaxed, undefined waistline. / Loosely front-tuck the white tee into the trousers to keep the clean base while allowing for ease. / Ensure the trousers fall to a full length or slightly break over the loafers to maintain the elongated leg line.
  - Gemini critic: approved after 0 revision(s)
- **Contemporary Sage & Black** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the sage blazer open to keep the relaxed, flowing line of the top layer. / Loosely front-tuck the white tee into the trousers to maintain a clean base without looking overly formal. / Ensure the black trousers fall cleanly over the loafers for a streamlined and elongated leg line.
  - Declared deviations: The blazer's color is sage green instead of camel, introducing a soft, contemporary hue.; The palette shifts from warm camel/white/black to a cooler sage/white/black, with brown accents.
  - Gemini critic: approved after 1 revision(s)
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### same-silhouette-different-colour

_Camel blazer removed: a blazer with the same structure in another colour should replace it._

**single_pass** · 10.6 s · all objective checks pass · human rating: ___/5
- **Modern Minimalist in Sage** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open to maintain the relaxed feel. / Loosely front-tuck the white tee into the trousers.
  - Declared deviations: Blazer color changed from camel to sage.
- **Monochromatic Black & White with a Pop of Sage** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Button the white shirt for a crisp look, or leave it slightly unbuttoned for a more relaxed vibe. / Allow the black boots to create a seamless line with the black trousers.
  - Declared deviations: Base layer changed from tee to shirt.; Footwear changed from brown loafers to black ankle boots.

**agentic** · 40.8 s · all objective checks pass · human rating: ___/5
- **Modern Tailored Neutrals** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the sage blazer open to maintain the relaxed top layer and undefined waist. / Loosely front-tuck the white tee into the trousers to keep a clean line while preserving the casual ease. / Ensure the black trousers fall with a straight, unbroken line to create an elongated silhouette.
  - Declared deviations: The blazer color is sage green instead of camel, shifting the warm neutral to a cool neutral.; The black trousers are a slightly slimmer fit than the inspiration.
  - Gemini critic: approved after 0 revision(s); notes: The blazer's color shifts the palette from warm camel to a cool sage, which is a declared deviation but still alters the original color mood.; The sage blazer appears slightly less oversized than the inspiration's blazer, which might subtly reduce the 'volume up top' balance, though it still reads as relaxed.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

### aesthetic-substitute-weekend

_No olive overshirt owned: another casual outer layer takes its role._

**single_pass** · 22.2 s · all objective checks pass · human rating: ___/5
- **Relaxed Denim & Rust Layers** (closest) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Light-wash denim jacket → Olive cotton utility overshirt, Rust ribbed sweater → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - How to wear: Wear the denim jacket open over the sweater. / Ensure the sweater's hem falls relaxed over the jeans.
- **Sage Blazer & Cream Cardigan Layers** (creative) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Olive cotton utility overshirt, Cream cable-knit cardigan → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - How to wear: Wear the cream cardigan buttoned up as the main top. / Layer the sage blazer over the cardigan, worn open.
  - Declared deviations: Outerwear is a blazer rather than a utility overshirt, adding a slightly more refined touch.; Inner knit is a cardigan, introducing a different neckline.
- **Monochromatic Neutral Layers** (alternative) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Olive cotton utility overshirt, Cream cable-knit cardigan → Cream crew-neck knit sweater, Black straight-leg trousers → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - How to wear: Wear the cream cardigan buttoned up. / Layer the camel blazer open over the cardigan. / Ensure the straight-leg trousers create a clean line to the sneakers.
  - Declared deviations: The overall palette is more monochromatic neutrals rather than earthy tones.; Bottoms are black tailored trousers instead of blue jeans, elevating the formality slightly.

**agentic** · 29.1 s · 2 distinct looks · human rating: ___/5
- **Relaxed Weekend Denim** (closest) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Light-wash denim jacket → Olive cotton utility overshirt, Cream cable-knit cardigan → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - How to wear: Wear the cream cable-knit cardigan buttoned up, like a sweater, to act as the primary knit layer. / Keep the denim jacket unbuttoned and open to maintain the layered and relaxed top half.
  - Declared deviations: The outer layer is a denim jacket instead of an olive utility overshirt, shifting the exact color and material.; The knit is a buttoned cardigan rather than a crew-neck sweater, though it serves the same role in the layering.
  - Gemini critic: approved after 0 revision(s); notes: The denim jacket, while a good substitute for the overshirt's relaxed nature, lacks the specific 'utility' aesthetic of the inspiration's olive overshirt. It shifts the material from cotton twill to denim, which is a declared deviation but still a slight departure from the specific utility vibe.; The cream cable-knit cardigan, worn buttoned up, serves the function of the knit sweater but introduces a cable-knit texture and a V-neckline (when buttoned) instead of the crew-neck of the inspiration. While a good substitute, it's a slight textural and neckline deviation.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 0 passed validation, 1 removed (invalid or duplicate)

### category-substitute-dress

_Matching aesthetic with different categories: slip dress recreated by a top + skirt two-piece._

**single_pass** · 8.3 s · all objective checks pass · human rating: ___/5
- **Sleek Evening with a Modern Edge** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Tuck the black camisole into the champagne satin skirt to create a seamless, elongated line, mimicking a dress. / Wear the black blazer open to maintain the layering and highlight the fluid column underneath. / Consider adding a delicate gold necklace if no hoops are available to keep some metallic accent.
  - Declared deviations: Used a camisole and skirt combination instead of a single slip dress.; Used a fitted blazer instead of a cropped leather biker jacket.; Used ankle boots instead of strappy heels.
  - Gaps: Gold hoop earrings (optional)

**agentic** · 17.6 s · all objective checks pass · human rating: ___/5
- **Champagne & Black Edge** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Wear the black camisole tucked into the champagne satin skirt to create a seamless, long column line. / Leave the black blazer open to reveal the fluid layers beneath and maintain the 'short structured over long soft' silhouette.
  - Declared deviations: Color palette: champagne and black instead of emerald and black.; Material: suiting blazer instead of leather jacket; ankle boots instead of strappy heels.; The slip dress is created from two separates (camisole + skirt).
  - Gaps: Gold hoop earrings (optional)
  - Gemini critic: approved after 0 revision(s); notes: The black fitted blazer, while structured, lacks the 'cropped' silhouette and the 'biker' edge of the inspiration's leather jacket. It creates a more formal, less edgy feel, altering the core aesthetic of 'sheen against a tough edge'. The length of the blazer also changes the proportion of the 'short structured layer over a long soft line'.; The black leather ankle boots, while sleek, introduce a heavier, more casual element compared to the delicate, strappy heeled sandals of the inspiration. This detracts from the 'evening polish' and 'sleek' aesthetic, especially when paired with the formal blazer.; The blazer's length, while 'fitted', is not 'cropped' like the inspiration's jacket. This slightly alters the 'short structured layer over a long soft line' proportion, making the top layer longer than intended and potentially obscuring the waist definition more.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### multiple-substitutes-distinct

_Several reasonable substitutes: closest and creative looks must differ._

**single_pass** · 17.4 s · all objective checks pass · human rating: ___/5
- **Classic Tailored Neutrals** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open to maintain the relaxed silhouette. / Loosely front-tuck the white tee into the trousers for a defined yet effortless waist.
- **Modern Sage & Black Contrast** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Keep the blazer open to show the clean lines of the shirt. / Partially tuck the white shirt into the trousers for a smart, relaxed finish.
  - Declared deviations: Shifted color palette from warm neutrals to a cooler sage with classic black and white.; Elevated the base layer from a t-shirt to a crisp button-down shirt.

**agentic** · 50.1 s · all objective checks pass · human rating: ___/5
- **Classic Tailored Neutrals** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open over the tee. / Loosely front-tuck the white tee into the trousers.
- **Modern Sage & Ecru Palette** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Ecru wide-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open. / Tuck the white shirt fully or with a neat front-tuck into the ecru trousers.
  - Declared deviations: Lighter, more modern color palette.; Slightly more relaxed trouser silhouette.

### missing-item-optional

_Missing wardrobe item: no hat owned; it must be an optional gap, never an invented garment._

**single_pass** · 11.6 s · all objective checks pass · human rating: ___/5
- **Polished Travel Layers in Neutrals** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - How to wear: Wear the camel blazer open to emphasize the vertical line. / Ensure the navy knit is neatly tucked or sits smoothly over the trousers. / Pair with a simple tote bag if carrying essentials.
  - Declared deviations: Substitute of a blazer for a trench coat
  - Gaps: Wide-brim straw-coloured hat (optional)
- **Modern Monochrome with a Pop of Navy** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Sage tailored blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Black straight-leg trousers → Ecru high-rise wide-leg trousers, Black leather ankle boots → White minimal sneakers
  - How to wear: Wear the blazer open to create a long line over the dark trousers. / Ensure the knit is neatly tucked into the high-rise trousers. / Consider adding a simple silver or gold necklace to complement the sage and navy.
  - Declared deviations: Shifted palette to include sage green and black.; Sleeker, straight-leg silhouette for trousers instead of wide-leg.; Ankle boots instead of sneakers for a slightly more elevated feel.
  - Gaps: Wide-brim straw-coloured hat (optional)

**agentic** · 72.4 s · all objective checks pass · human rating: ___/5
- **Polished Travel Layers** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - How to wear: Wear the camel blazer open to maintain the relaxed feel and allow the inner layers to show. / Ensure the navy knit is fully tucked or lies smoothly over the trousers to keep the clean lines.
  - Declared deviations: Used an oversized blazer instead of a belted trench coat, which changes the exact length and waist definition.; No wide-brim hat is included.
  - Gaps: Wide-brim straw-coloured hat (optional)
  - Gemini critic: approved after 0 revision(s); notes: The camel oversized blazer, while longline, lacks the belted waist definition and the crisp, structured feel of a trench coat, which is a key element of the inspiration's silhouette and formality. The inspiration's trench creates a distinct vertical line and waist emphasis that the open blazer cannot replicate.; Without the belted trench, the outfit loses the defined waist and the specific volume balance of a long outer layer framing a fitted knit and wide trousers. The oversized blazer, worn open, creates a more relaxed, less defined silhouette than the inspiration.; The absence of a wide-brim hat, while declared, slightly diminishes the 'travel' and 'relaxed' aesthetic of the inspiration, making the overall look feel a bit less complete for the stated occasion.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 1 of 3; sending feedback to the stylist → Stylist proposed 2 look(s); 1 passed validation, 1 removed (invalid or duplicate) → Critic approved 0 of 1

### missing-key-piece

_Genuine gap: closet without any outer layer must report an essential outerwear gap._

**single_pass** · 7.2 s · all objective checks pass · human rating: ___/5
- No looks — stylist declined (no proposal) — review whether a coherent outfit existed: The core of the inspiration outfit is a relaxed, oversized blazer. Unfortunately, there are no suitable blazer-like outerwear pieces in your closet to recreate this essential element. Without it, the overall tailored, smart-casual silhouette and layering cannot be achieved, making it difficult to compose a coherent look that captures the inspiration's essence.

**agentic** · 4.8 s · all objective checks pass · human rating: ___/5
- No looks — stylist declined (no proposal) — review whether a coherent outfit existed: The user's wardrobe lacks a suitable tailored outer layer (like a blazer or a structured cardigan) to recreate the essential 'relaxed tailored top layer' of the inspiration outfit. This piece is crucial for achieving the specified silhouette, formality, and polished smart-casual aesthetic.
- Workflow: Stylist proposed 0 look(s); 0 passed validation

### formal-occasion-constraint

_Formal occasion: no casual sneakers, denim jacket or jeans for an evening event._

**single_pass** · 10.8 s · all objective checks pass · human rating: ___/5
- **Emerald & Black Polish** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Forest green wrap midi dress → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Wear the blazer open over the dress to maintain the visible column of the dress. / Consider adding a simple gold necklace or bracelet if available, to mimic the metallic accent.
  - Declared deviations: no gold accessory; blazer instead of leather jacket; boots instead of strappy heels
  - Gaps: Gold hoop earrings (optional)
- **Champagne Sheen & Black Contrast** (alternative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Tuck the black camisole neatly into the satin skirt to maintain a seamless, elongated silhouette. / Wear the blazer open to showcase the fluid lines of the cami and skirt.
  - Declared deviations: no gold accessory; blazer instead of leather jacket; boots instead of strappy heels; two-piece instead of dress
  - Gaps: Gold hoop earrings (optional)

**agentic** · 34.8 s · all objective checks pass · human rating: ___/5
- **Satin Column Chic** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Tuck the black camisole into the champagne satin skirt for a continuous, fluid column line. / Leave the black blazer open to emphasize the column silhouette and the contrast between textures. / Ensure the skirt sits at the natural waist for optimal proportions.
  - Declared deviations: Used a black camisole and champagne satin skirt to create the 'slip dress' effect, changing the core color.; Substituted a fitted blazer for a leather biker jacket.; Opted for black ankle boots instead of strappy heeled sandals.
  - Gaps: Gold hoop earrings (optional)
  - Gemini critic: approved after 0 revision(s); notes: The color palette shifts from emerald and black to champagne and black, which is a declared deviation but still maintains a sophisticated, high-contrast look.; The black blazer, while structured, lacks the 'edgy' quality of a leather biker jacket. However, it still provides the necessary contrast in material and structure.; Black leather ankle boots, while sleek, change the footwear aesthetic from 'delicate, strappy' heeled sandals to a more grounded option. This is an unavoidable deviation given the owned wardrobe.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 1 of 3; sending feedback to the stylist → Stylist proposed 1 look(s); 0 passed validation, 1 removed (invalid or duplicate)

### shopping-disabled

_Shopping disabled: gaps carry no sourcing hints._

**single_pass** · 11.9 s · all objective checks pass · human rating: ___/5
- **Polished Neutrals for Travel** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - How to wear: Wear the blazer open to emphasize the vertical line. / Ensure the knit is tucked or sits smoothly under the blazer. / Pair with the white sneakers for a relaxed, travel-friendly feel.
  - Declared deviations: Blazer instead of trench coat, so no belt detail.; No hat accessory.
  - Gaps: Wide-brim straw-coloured hat (optional)
- **Monochrome Base with Sage Accent** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Sage tailored blazer → Beige belted double-breasted trench coat, White poplin shirt → Navy fine-knit crew-neck sweater, Black straight-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - How to wear: Layer the white shirt under the sage blazer, ensuring the collar is neatly pressed. / Wear the blazer open to create a long line over the black trousers. / Pair with white sneakers to maintain a fresh, casual balance.
  - Declared deviations: Colour palette shifted to sage, black, and white.; Silhouette is more structured with straight-leg trousers instead of wide-leg.; No hat accessory.
  - Gaps: Wide-brim straw-coloured hat (optional)

**agentic** · 43.3 s · all objective checks pass · human rating: ___/5
- **Polished Travel Layers** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - How to wear: Wear the blazer open to maintain a relaxed feel and allow the full outfit to be seen. / Ensure the sweater is neatly tucked or hits at the waist to define the proportions with the high-rise trousers.
  - Declared deviations: The outer layer is a blazer instead of a long trench, resulting in a shorter vertical line and no belted waist definition.; The absence of a hat changes the accessorizing.
  - Gaps: Wide-brim straw-coloured hat (optional)
  - Gemini critic: approved after 0 revision(s); notes: The camel oversized blazer significantly alters the essential long vertical line and belted waist definition provided by the trench coat in the inspiration. This changes the overall silhouette and the polished, layered feel.; The shorter length of the blazer disrupts the intended long, flowing silhouette of the inspiration, creating a more truncated upper body line that doesn't harmonize as effectively with the wide-leg trousers.; While individually good pieces, the combination of an oversized blazer with wide-leg trousers can sometimes appear less intentional or polished than the trench's defined silhouette, especially without the belt to anchor the waist.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

### user-exclusion-and-keep

_Preference adherence: excluded pieces never appear, kept pieces always do._

**single_pass** · 17.1 s · all objective checks pass · human rating: ___/5
- **Classic Camel & Black for Work** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the camel blazer open over the white shirt. / Ensure the white shirt is neatly tucked into the black trousers for a clean line.
  - Declared deviations: A white poplin shirt replaces the white t-shirt for a slightly more polished, work-appropriate base.
- **Modern Sage & Black with Boots** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, Navy fine-knit sweater → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the sage blazer open over the navy knit. / Ensure the navy knit is neatly tucked or smoothly layered over the black trousers.
  - Declared deviations: A sage blazer replaces the camel blazer, introducing a cooler, modern color.; A navy fine-knit sweater replaces the white tee, changing the base layer's color and material.; Black ankle boots replace brown loafers, creating a more streamlined, monochromatic lower half.

**agentic** · 37.0 s · all objective checks pass · human rating: ___/5
- **Modern Sage & Black Contrast** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, Navy fine-knit sweater → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the sage blazer open to maintain the relaxed feel and ensure the base layer is visible. / Lightly front-tuck the navy fine-knit sweater to create a clean line and maintain the elongated leg line of the trousers.
  - Declared deviations: Blazer color is sage green instead of camel, shifting the neutral palette to a cooler tone.; Base layer is a navy fine-knit sweater instead of a white t-shirt, changing color, material, and formality slightly.; Footwear is black ankle boots instead of brown loafers, changing the shoe style and color.
  - Gemini critic: approved after 0 revision(s); notes: The sage blazer is described as 'tailored, relaxed shoulders' while the inspiration calls for an 'oversized, hip-length blazer'. The image of the sage blazer appears slightly less oversized than the camel blazer, which might subtly alter the intended volume balance of 'volume up top' if it's not hip-length.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

### ambiguous-not-an-outfit

_Ambiguous/non-outfit photo: no looks, honest reason._

**single_pass** · 0.0 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): We couldn't find a wearable outfit in this image. Try a clearer full-outfit photo.

**agentic** · 0.0 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): We couldn't find a wearable outfit in this image. Try a clearer full-outfit photo.
