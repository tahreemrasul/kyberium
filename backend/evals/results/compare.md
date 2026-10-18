# Rewear — engine comparison (live Gemini)

Variants: `single_pass` {'styling_engine': 'single_pass'}, `agentic` {'styling_engine': 'agentic'}

## Summary

| Variant | Objective checks | Invalid owned ids | Looks returned | With styling instructions | Critic rejections | No-look runs (legit / suspect) | Median total | Max total |
|---|---|---|---|---|---|---|---|---|
| single_pass | 16/16 | 0 | 26 | 26 | 0 | 2 / 1 | 10.9 s | 23.6 s |
| agentic | 14/16 | 0 | 22 | 22 | 16 | 2 / 1 | 32.2 s | 105.2 s |

### Median per-stage latency (ms) and cost counters

| Variant | retrieval_ms | knowledge_ms | composer_ms | stylist_ms | critic_image_prep_ms | critic_ms | revision_ms | total_ms | passes | stylist_calls | critic_calls | critic_images | critic_image_tokens | stylist_tokens | critic_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| single_pass | 22 | 0 | 10828 | – | – | – | – | 10870 | – | – | – | – | – | – | – |
| agentic | 25 | 0 | 15090 | 19397 | 54 | 12612 | 14566 | 32175 | 2 | 2 | 2 | 12 | 3096 | 14985 | 12864 |

`revision_ms` = model time in passes after the first; `critic_ms` excludes image preparation (`critic_image_prep_ms`). Values are medians per request.

## Looks per case (human rating fields are intentionally blank)

### real-denim-skirt

_The reported failure: white tucked button-down + high-waisted denim midi skirt + sneakers, styled from a real 7-piece wardrobe with no white shirt or denim skirt. A strong answer protects the defined waist and relaxed mood (e.g. the belted shirt-dress, or sweater + skirt with a tuck and casual shoes) instead of stacking dressy substitutes and an unneeded jacket._

**single_pass** · 12.8 s · all objective checks pass · human rating: ___/5
- **Modern Midi Skirt & Sneaker Look** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Burgundy satin midi skirt → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Tuck the black sweater into the burgundy midi skirt to define the waist. / Allow the satin skirt to flow freely for movement.
  - Declared deviations: Color palette (darker top and bottom); Materiality (satin skirt and knit sweater); No front slit on skirt
- **Relaxed Wide-Leg & Shirt Dress Base** (creative) — 2/3 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Black high-rise wide-leg jeans → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Wear the camel shirt dress unbuttoned over the black wide-leg jeans, using its belt to cinch the waist over the jeans. / Ensure the shirt dress is styled to create a 'top' effect, possibly by tucking or knotting the bottom half if it's too long, or letting it flow open as a light layer.
  - Declared deviations: Garment types (shirt dress used as a top, wide-leg jeans instead of skirt); Color palette (warm neutrals)
  - Gaps: White cotton button-down shirt (essential)

**agentic** · 46.9 s · all objective checks pass · human rating: ___/5
- **Sophisticated Satin & Knit** (creative) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Burgundy satin midi skirt → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Half-tuck the black sweater into the front of the skirt to clearly mark the waist and define the silhouette. / Allow the satin skirt to flow naturally for an elegant drape and to highlight its fluid movement. / Consider pushing up the sweater sleeves to expose the wrists, adding to the relaxed vibe and balancing the skirt's length.
  - Declared deviations: Uses a soft knit sweater instead of a crisp cotton shirt, changing the top's texture and drape.; Features a lustrous satin midi skirt in burgundy instead of rigid denim in mid-blue, introducing a different material and color.; The overall formality is elevated from casual to smart-casual due to the satin skirt, balanced by the casual sneakers.
  - Gemini critic: approved after 1 revision(s); notes: The inspiration's 'light top against a mid-tone bottom' contrast is inverted to a dark top against a dark-toned bottom (burgundy). While the overall palette is cohesive, it deviates from the specific color contrast of the inspiration.; The relaxed fit of the black sweater, even with a half-tuck, might still add some volume around the waist area, potentially slightly obscuring the clean waist definition that a crisp, tucked shirt would provide with the satin skirt.
- **Monochromatic Shirt Dress** (alternative) — 2/2 pieces already in your closet · No new purchase needed
  - Pieces: Tan belted shirt dress → White cotton button-down shirt + High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Ensure the dress's belt is tied to cinch the waist, mimicking the tucked-in look. / Button the dress to just above the knee or higher for a touch of leg and movement.
  - Declared deviations: Monochromatic tan instead of white/mid-blue contrast; Shirt dress instead of separate top and skirt; Absence of crisp cotton and rigid denim textures
  - Gemini critic: approved after 0 revision(s); notes: The monochromatic tan palette lacks the crisp color contrast of white and mid-blue from the inspiration, and the matte woven fabric of the dress differs from the crisp cotton and rigid denim textures.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 1 of 3; sending feedback to the stylist → Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2

### real-emerald-evening

_Evening slip dress + cropped leather jacket + heels, from the real wardrobe (satin skirt, tweed and suede jackets, no heels)._

**single_pass** · 8.6 s · all objective checks pass · human rating: ___/5
- **Burgundy Satin & Cream Tweed Contrast** (creative) — 2/4 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Cream embellished tweed jacket → Black cropped leather biker jacket, Burgundy satin midi skirt → Emerald satin bias-cut slip dress
  - How to wear: Tuck the black sweater neatly into the burgundy satin skirt to maintain a seamless column line. / Wear the cream tweed jacket open to highlight the column underneath and maintain the cropped proportion.
  - Declared deviations: The dress is replaced by a two-piece skirt and top combination.; The 'tough edge' comes from tweed texture and structure rather than leather.; The color palette shifts from emerald/black to burgundy/black/cream.
  - Gaps: Black strappy heeled sandals (essential); Gold hoop earrings (optional)

**agentic** · 18.5 s · all objective checks pass · human rating: ___/5
- **Sleek Satin & Textured Edge** (creative) — 2/4 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Cream embellished tweed jacket → Black cropped leather biker jacket, Burgundy satin midi skirt → Emerald satin bias-cut slip dress
  - How to wear: Tuck the black sweater neatly into the burgundy skirt to create a smooth, continuous line, mimicking a slip dress. / Wear the cream tweed jacket open to emphasize the long vertical line of the skirt and top. / Ensure the black sweater is fully tucked to maintain the defined waist and sleek silhouette.
  - Declared deviations: Color palette shifted from emerald/black/gold to burgundy/black/cream.; Texture changed from leather to tweed for the jacket, reducing the 'tough edge' in favor of 'textured chic'.; Footwear is casual sneakers instead of formal heels, lowering the overall formality.; The 'slip dress' is replaced by a skirt and tucked sweater combo.
  - Gaps: Black strappy heeled sandals (essential); Gold hoop earrings (optional)
  - Gemini critic: approved after 0 revision(s); notes: The 'tough edge' essential trait from the inspiration's leather jacket is completely lost with the cream tweed jacket, which introduces a 'chic' or 'elegant' aesthetic instead of 'edgy'.; The color palette shift from high-contrast emerald/black to burgundy/black/cream significantly reduces the dramatic contrast and introduces a softer, more classic feel that clashes with the 'edgy' inspiration. The cream jacket also introduces a much lighter, more delicate texture than the inspiration's black leather.; The combination of a sophisticated, embellished tweed jacket, a sleek satin skirt, a matte knit sweater, and casual platform sneakers creates a disjointed formality and style clash. The sneakers drastically pull down the 'evening polish' and 'smart casual' formality intended for an 'event'.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### real-camel-work

_Camel blazer + tee + straight trousers + loafers for work, from the real wardrobe (no blazer, no tee, no loafers): expect honest gaps or declared deviations._

**single_pass** · 15.8 s · all objective checks pass · human rating: ___/5
- **Cream Tweed & Black Denim Work Look** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Cream embellished tweed jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - How to wear: Wear the cream jacket open over the black sweater. / Ensure the black sweater is neatly tucked or falls smoothly over the jeans' waistband. / Pair with simple gold or silver stud earrings to maintain the minimal aesthetic.
  - Declared deviations: The silhouette shifts from straight trousers to wide-leg jeans, and loafers to sneakers, making the bottom half more casual and contemporary.; The top layer is a structured tweed jacket rather than a relaxed blazer.
  - Gaps: Tan structured tote bag (optional)
- **Rust Overshirt & Skirt Remix** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Burgundy satin midi skirt → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - How to wear: Wear the rust jacket open over the black sweater, allowing the sweater to be visible. / Pair with delicate gold jewelry to complement the warm tones. / Consider a half-tuck of the sweater if the skirt's waistband is visually appealing.
  - Declared deviations: The bottom is a satin midi skirt instead of tailored trousers, changing the texture and silhouette significantly.; The outer layer is a casual overshirt rather than a structured blazer.; The palette shifts to warmer, deeper tones.
  - Gaps: Tan structured tote bag (optional)

**agentic** · 58.0 s · all objective checks pass · human rating: ___/5
- **Cream & Black Tailored Chic** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Cream embellished tweed jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - How to wear: Wear the cream tweed jacket open to maintain the layered line and let the black sweater show. / Ensure the black sweater is neatly tucked or falls smoothly over the jeans to keep a clean line.
  - Declared deviations: The blazer is replaced by a cropped tweed jacket, shifting the silhouette and texture.; The white tee is replaced by a black sweater, changing the top's color and material.; Loafers are replaced by sneakers, making the footwear more casual.
  - Gaps: Tan structured tote bag (optional)
  - Gemini critic: approved after 0 revision(s); notes: The cropped, embellished tweed jacket fundamentally alters the silhouette and formality of the inspiration's relaxed, oversized, matte camel blazer. It loses the 'relaxed tailored top layer' and 'minimal' aesthetic.; The cropped jacket over wide-leg jeans creates a very different proportion than the inspiration's hip-length blazer over straight trousers. The volume balance is lost, making the top half appear shorter and wider.; The highly embellished, textured tweed jacket clashes with the minimal, clean aesthetic of the inspiration. The formality is also elevated significantly by the jacket, while the sneakers pull it back down, creating a disjointed feel.
- **Warm Tones & Structured Base** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - How to wear: Wear the rust suede jacket open to emphasize the layered look and maintain the relaxed silhouette. / Ensure the black sweater is neatly tucked or falls smoothly over the jeans to maintain a clean line with the wide-leg bottom. / Pair with minimal accessories to keep the focus on the clean lines and warm tones of the garments.
  - Declared deviations: The blazer is replaced by a more casual suede-like jacket.; The white tee is replaced by a black sweater, flipping the light/dark contrast of the base layer.; The straight-leg trousers are replaced by wide-leg jeans, maintaining structure but with a different silhouette.; The brown loafers are replaced by platform sneakers, adding a modern, casual touch.
  - Gaps: Tan structured tote bag (optional)
  - Gemini critic: approved after 1 revision(s); notes: The 'relaxed tailored top layer' essential trait is lost. The inspiration's blazer is structured and tailored, even if relaxed. The rust suede jacket is a casual utility/overshirt style, lacking the tailored quality.; The combination of the cropped black sweater and the high-rise wide-leg jeans creates a very different proportion than the inspiration. The inspiration has a hip-length blazer and a straight trouser, leading to an elongated, smooth line. Here, the cropped sweater shortens the torso visually, and the wide-leg jeans, while intentional, shift the overall silhouette significantly from the inspiration's 'slim straight trouser' balance.; The inspiration features a medium contrast with warm camel and crisp white against black. This look flips the base to black, making the overall palette darker and losing the crisp white element, which was a key part of the 'minimal neutral palette' and 'polished' feel.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 1 of 3; sending feedback to the stylist → Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2

### real-satin-material-challenge

_Material challenge: satin slip skirt dressed down with a slouchy sweatshirt and sneakers. The burgundy satin skirt fits; the stylist must keep the dressed-down mood._

**single_pass** · 10.3 s · all objective checks pass · human rating: ___/5
- **Sleek & Sporty Contrast** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - How to wear: Front-tuck the Black crewneck sweater into the Burgundy satin midi skirt to define the waist, similar to the inspiration.
  - Declared deviations: The top is a sweater instead of a sweatshirt, and the skirt is burgundy instead of champagne.
- **Urban Edge with Fluidity** (creative) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Black high-rise wide-leg jeans → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - How to wear: Front-tuck the Black crewneck sweater into the high-rise Black wide-leg jeans to emphasize the waist and create the desired proportions. / Ensure the jeans skim the top of the platform sneakers for a modern look.
  - Declared deviations: The sleek satin skirt is replaced with wide-leg denim jeans, shifting the 'high-low' material contrast to a 'relaxed-fluid' silhouette contrast.

**agentic** · 29.0 s · all objective checks pass · human rating: ___/5
- **Modern High-Low Contrast** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - How to wear: Front-tuck the black sweater to define your waist and maintain the outfit's proportions. / Let the burgundy satin skirt drape naturally to emphasize its fluid silhouette.
  - Declared deviations: The top is a knit sweater instead of a fleece sweatshirt, altering the exact material texture.; The skirt color is burgundy instead of champagne.; The top color is black instead of heather grey.
  - Gemini critic: approved after 0 revision(s); notes: The black knit sweater, while relaxed, lacks the distinct 'sporty' and 'fleece' texture of the inspiration's sweatshirt, making the high-low contrast slightly less pronounced in texture.; The palette of black and burgundy is richer and more dramatic than the soft, low-contrast neutrals (heather grey, champagne) of the inspiration, shifting the overall mood slightly.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 1 of 3; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

### real-no-good-outfit

_No good outfit exists: black-tie tuxedo look from a casual 7-piece wardrobe. A good system admits the gap instead of forcing a match._

**single_pass** · 5.0 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): The inspiration is a very specific, strict black-tie tuxedo outfit. Your current wardrobe lacks the essential formal garments required to recreate this look, such as a formal jacket, dress shirt, tailored trousers, or dress shoes. The available items are primarily casual or smart-casual, and do not align with the strict formality, specific silhouettes, or traditional black-and-white palette of the inspiration. Given the 'close' fidelity preference, no reasonable substitutions can be made.

**agentic** · 5.3 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): The owned garments do not contain any items that meet the 'strict formality' and 'matching black tailoring' essential traits of the black-tie tuxedo inspiration. All available garments are casual or smart-casual, and there are no suitable formal pieces (tuxedo jacket, dress shirt, tailored trousers, formal shoes) in the wardrobe.
- Workflow: Stylist proposed 0 look(s); 0 passed validation

### exact-camel-work

_Exact garment matches: every key piece of the camel work look is owned._

**single_pass** · 10.9 s · all objective checks pass · human rating: ___/5
- **Classic Camel & Black Tailoring** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open over the tee. / Loosely front-tuck the white tee into the trousers.
- **Contemporary Sage & Ecru Tailoring** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Ecru wide-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the sage blazer open. / Button the white shirt and leave it untucked for a relaxed, modern line over the wide-leg trousers.
  - Declared deviations: Changed the primary color palette from warm camel/black to cool sage/ecru/black.; Swapped straight-leg trousers for wide-leg for a more relaxed, modern silhouette.; Replaced loafers with sleek ankle boots.

**agentic** · 32.2 s · all objective checks pass · human rating: ___/5
- **Classic Camel & Black** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the camel blazer open to maintain the relaxed silhouette and allow the white tee to peek through. / Loosely front-tuck the white tee into the trousers to create a clean line without hiding the waist. / Ensure trousers fall straight for a clean, elongated leg line.
  - Gemini critic: approved after 0 revision(s)
- **Sage & Streamlined Neutrals** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, White leather sneakers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the sage blazer open to maintain the relaxed silhouette and allow the white tee to peek through. / Loosely front-tuck the white tee into the trousers to create a clean line without hiding the waist. / Allow the straight-leg trousers to fall cleanly over the white sneakers for a refined, elongated look.
  - Declared deviations: Blazer color is sage green instead of camel, introducing a soft color accent.; Footwear is white leather sneakers instead of brown loafers, for a more modern, casual polish.
  - Gemini critic: approved after 1 revision(s); notes: The sage green blazer, while a good creative choice, shifts the palette from the warm, earthy tones of camel and brown to a cooler, more muted neutral. This is a declared deviation, but it does alter the overall color mood slightly.; The inspiration's palette included warm camel and brown, which provided a specific medium color contrast. The sage and white sneakers, while cohesive, create a slightly different, cooler contrast than the original.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### same-silhouette-different-colour

_Camel blazer removed: a blazer with the same structure in another colour should replace it._

**single_pass** · 13.2 s · all objective checks pass · human rating: ___/5
- **Sage Smart-Casual Tailoring** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open over the tee. / Lightly front-tuck the white tee into the trousers to define the waist without being too formal.
  - Declared deviations: Blazer color changed from camel to sage green.
- **Ecru Trousers & Sage Blazer Remix** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Ecru wide-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open. / Ensure the white tee is neatly tucked into the high-rise ecru trousers to maintain a polished line.
  - Declared deviations: Bottom color changed from black to ecru.; Bottom silhouette changed from straight-leg to wide-leg.
- **Monochrome Black & White with Sage Accent** (alternative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the white shirt buttoned up or slightly unbuttoned, neatly tucked into the trousers. / Layer the sage blazer open over the shirt.
  - Declared deviations: Base layer changed from tee to shirt.; Footwear changed from brown loafers to black ankle boots.

**agentic** · 37.6 s · all objective checks pass · human rating: ___/5
- **Sage & Neutrals Smart-Casual** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the sage blazer open to maintain the relaxed, undefined waistline and showcase the clean base layer. / Lightly front-tuck the white tee into the trousers to create a subtle break and keep the look polished. / Ensure the trousers fall cleanly over the loafers for a long, unbroken leg line.
  - Declared deviations: Blazer color is sage green instead of camel, introducing a cool-toned neutral.
  - Gemini critic: approved after 0 revision(s)
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

### aesthetic-substitute-weekend

_No olive overshirt owned: another casual outer layer takes its role._

**single_pass** · 17.0 s · all objective checks pass · human rating: ___/5
- **Earthy Layers with Denim** (closest) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Light-wash denim jacket → Olive cotton utility overshirt, Cream cable-knit cardigan → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - How to wear: Wear the cream cardigan unbuttoned under the denim jacket. / Ensure the jeans have a relaxed, full-length fit.
  - Declared deviations: The outer layer is a denim jacket rather than a utility overshirt, shifting the utility aesthetic slightly.
- **Warm Tones & Clean Lines** (creative) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Olive cotton utility overshirt, Rust ribbed sweater → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - How to wear: Wear the blazer open over the sweater. / Keep the sweater untucked for a relaxed profile. / Consider a half-tuck of the sweater if more waist definition is desired.
  - Declared deviations: The outer layer is a blazer, giving a slightly smarter feel than the utility overshirt.; The palette shifts to warmer, more muted tones with sage and rust.

**agentic** · 30.5 s · all objective checks pass · human rating: ___/5
- **Relaxed Denim Weekend** (closest) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Light-wash denim jacket → Olive cotton utility overshirt, Cream cable-knit cardigan → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - How to wear: Wear the cream cardigan buttoned up like a sweater to maintain the base layer's warmth and silhouette. / Keep the denim jacket unbuttoned to replicate the open, relaxed layering of the inspiration. / Ensure the jeans are full-length to maintain the clean, straight line to the shoes.
  - Declared deviations: Denim jacket instead of utility overshirt, changing material and exact color.; Cardigan worn as a sweater instead of a crew-neck sweater.
  - Gemini critic: approved after 0 revision(s); notes: The denim jacket, while boxy, lacks the specific 'utility' aesthetic of the inspiration's overshirt, shifting the style slightly more towards classic casual.; Using a cardigan buttoned up as a sweater works, but the V-neck opening is a subtle deviation from the crew-neck of the inspiration, slightly altering the neckline aesthetic.
- **Warm Tones & Denim** (creative) — 4/4 pieces already in your closet · No new purchase needed
  - Pieces: Light-wash denim jacket → Olive cotton utility overshirt, Rust ribbed sweater → Cream crew-neck knit sweater, Mid-wash straight jeans → Light-wash straight-leg jeans, White leather sneakers → White low-top sneakers
  - How to wear: Wear the denim jacket unbuttoned to maintain the open, relaxed layering of the inspiration. / Let the rust sweater hang loosely to keep the relaxed top half volume. / Ensure the straight jeans are full length, allowing them to fall cleanly over the sneakers.
  - Declared deviations: Outerwear is light-wash denim instead of olive cotton twill, shifting the color palette slightly and introducing a more classic casual material.; The top is a rust-colored knit instead of cream, introducing a warm color accent.
  - Gemini critic: approved after 1 revision(s); notes: The shift from an olive utility overshirt to a light-wash denim jacket, and a cream knit to a rust knit, significantly alters the original 'earthy, soft palette' to a warmer, more classic casual one. While the rust is earthy, the denim introduces a different tonal quality than the original olive.; The denim jacket, while casual and layered, lacks the specific 'utility' aesthetic of the original olive overshirt, leaning more towards a classic casual vibe.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### category-substitute-dress

_Matching aesthetic with different categories: slip dress recreated by a top + skirt two-piece._

**single_pass** · 8.1 s · all objective checks pass · human rating: ___/5
- **Sleek Evening Separates** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Ensure the black camisole is tucked smoothly into the champagne satin midi skirt to create a continuous, fluid line. / Wear the black fitted blazer open to maintain the layering and reveal the sleek top underneath.
  - Declared deviations: Uses a camisole and skirt combo instead of a single slip dress.; A black blazer provides a polished edge rather than the 'tough' edge of a leather biker jacket.; Ankle boots replace strappy heels for a more modern, grounded feel.
  - Gaps: Gold hoop earrings (optional)

**agentic** · 16.4 s · dress-1 covered by ['top', 'bottom'] · human rating: ___/5
- **Sleek Contrast: Champagne & Black** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → extra, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Wear the black camisole tucked into the champagne satin skirt to create a seamless, long fluid column. / Keep the black blazer unbuttoned to highlight the sleek lines of the camisole and skirt beneath. / Ensure the blazer's hem hits at or just above your natural waist to maintain the cropped-over-long proportion.
  - Declared deviations: Used a camisole and skirt combination instead of a single slip dress.; Changed the primary colour of the fluid base from emerald to champagne with a black top.; Substituted a black fitted blazer for a black leather biker jacket, changing the 'tough' material but keeping the structure and colour.; Used black leather ankle boots instead of strappy heels for a slightly more grounded, but still sleek, edgy feel.
  - Gaps: Gold hoop earrings (optional)
  - Gemini critic: approved after 0 revision(s); notes: While the blazer provides structure, it lacks the specific 'tough edge' of a leather biker jacket, making the material interplay slightly less pronounced than in the inspiration.; The black camisole on top of the champagne skirt, while creating a column, introduces a color break at the waist that the original slip dress did not have, slightly altering the unbroken fluid line.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### multiple-substitutes-distinct

_Several reasonable substitutes: closest and creative looks must differ._

**single_pass** · 23.6 s · all objective checks pass · human rating: ___/5
- **Classic Camel & Black Tailoring** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open to maintain the relaxed feel. / Loosely front-tuck the white tee into the trousers for a subtle waist definition.
- **Modern Sage & Black with Wide-Leg Trousers** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Ecru wide-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open to showcase the clean lines of the shirt and trousers. / Fully tuck the white shirt into the high-rise wide-leg trousers to define the waist and enhance leg length. / Ensure the trousers skim the top of the ankle boots for an elongated line.
  - Declared deviations: Swapped the straight-leg trousers for wide-leg, altering the lower silhouette.; Changed blazer colour to sage green for a cooler palette.; Used a crisp shirt instead of a tee for a slightly more formal base.
- **Monochromatic Black with a Pop of Sage** (alternative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, Black silk-look camisole → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open to reveal the sleek black camisole. / Ensure the camisole is neatly tucked or drapes smoothly over the trousers for a seamless line. / Pair with delicate gold jewelry to complement the sage and tan accents.
  - Declared deviations: Created a monochromatic black base with camisole and trousers.; Introduced a silky texture with the camisole for a slightly dressier feel.; Used black boots to maintain the sleek, unbroken line.

**agentic** · 32.4 s · 2 distinct looks · human rating: ___/5
- **Sage & Black Smart-Casual** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, White crew-neck tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Brown leather loafers → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the sage blazer open to maintain the relaxed top layer and the outfit's easy flow. / Half-tuck the white tee into the black trousers to maintain a neat yet comfortable base. / Ensure the trousers fall to a modern length, just skimming the top of the loafers for a clean line.
  - Declared deviations: The blazer color shifts from camel to sage green, introducing a subtle cool-toned accent to the otherwise neutral palette.
  - Gemini critic: approved after 1 revision(s); notes: While the sage blazer is a good creative choice, its fit appears slightly more structured and less overtly 'oversized' than the inspiration's blazer, which was a key element of the relaxed proportion. It still reads as relaxed, but less voluminous.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### missing-item-optional

_Missing wardrobe item: no hat owned; it must be an optional gap, never an invented garment._

**single_pass** · 9.3 s · all objective checks pass · human rating: ___/5
- **Polished Travel Layers** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - How to wear: Wear the blazer open to maintain a relaxed feel. / Ensure the knit is tucked or neatly layered under the blazer.
  - Declared deviations: The outer layer is a blazer instead of a trench, losing the belted waist and the full length of the inspiration's coat.
  - Gaps: Wide-brim straw-coloured hat (optional)
- **Modern Navy & Ecru Remix** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Sage tailored blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, Brown leather loafers → White minimal sneakers
  - How to wear: Wear the blazer open to maintain a relaxed silhouette. / Consider a half-tuck for the knit to subtly define the waist with the high-rise trousers.
  - Declared deviations: The outer layer is a blazer instead of a trench, and in a different color. The footwear is loafers instead of sneakers.
  - Gaps: Wide-brim straw-coloured hat (optional)

**agentic** · 105.2 s · all objective checks pass · human rating: ___/5
- **Polished Travel Layers with a Modern Twist** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - How to wear: Wear the camel blazer open to maintain a long vertical line. / Ensure the navy knit is neatly tucked or sits smoothly over the trousers.
  - Declared deviations: Replaced the belted trench with an oversized blazer, losing the defined waist but keeping a long vertical line when worn open.
  - Gaps: Wide-brim straw-coloured hat (optional)
- **Monochromatic Neutral Layers with a Pop of Navy** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, White crew-neck tee → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, Brown leather loafers → White minimal sneakers, Tan structured tote → extra
  - How to wear: Keep the blazer open for a relaxed, layered look. / Pair with a simple necklace to draw attention to the neckline of the white tee.
  - Declared deviations: Introduced a monochromatic neutral base with a white tee instead of navy, and opted for more polished loafers over sneakers.
  - Gaps: Wide-brim straw-coloured hat (optional)
- **Modern Minimalist with a Sage Accent** (alternative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Sage tailored blazer → Beige belted double-breasted trench coat, Black silk-look camisole → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, Black leather ankle boots → White minimal sneakers
  - How to wear: Wear the blazer open to showcase the sleek camisole and maintain a long line. / Ensure the camisole is neatly tucked into the high-rise trousers.
  - Declared deviations: Introduced a sage green accent color, a black camisole, and black ankle boots for a more urban, minimalist feel.
  - Gaps: Wide-brim straw-coloured hat (optional)

### missing-key-piece

_Genuine gap: closet without any outer layer must report an essential outerwear gap._

**single_pass** · 6.2 s · all objective checks pass · human rating: ___/5
- No looks — stylist declined (no proposal) — review whether a coherent outfit existed: The inspiration outfit heavily relies on a key piece: an oversized camel blazer. Unfortunately, you do not own any garment that can reasonably substitute for this essential tailored outer layer. Without it, the core structure, proportion, and smart-casual aesthetic of the inspiration cannot be recreated, making it impossible to form a coherent look.

**agentic** · 5.4 s · all objective checks pass · human rating: ___/5
- No looks — stylist declined (no proposal) — review whether a coherent outfit existed: The wardrobe lacks a key piece: a relaxed, tailored outer layer like a blazer. This piece is essential for achieving the core aesthetic of 'relaxed tailored top layer over a clean base' and 'polished but easy smart-casual' tailoring, which is central to the inspiration's DNA. Without it, a coherent and occasion-appropriate outfit cannot be formed that aligns with the inspiration.
- Workflow: Stylist proposed 0 look(s); 0 passed validation

### formal-occasion-constraint

_Formal occasion: no casual sneakers, denim jacket or jeans for an evening event._

**single_pass** · 8.6 s · all objective checks pass · human rating: ___/5
- **Green Glamour with a Sharp Edge** (closest) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Forest green wrap midi dress → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Wear the blazer open over the wrap dress to maintain the long line of the dress. / Cinch the wrap dress at the waist to emphasize its silhouette.
  - Declared deviations: The outer layer is a blazer, not a biker jacket, and is not cropped.; The dress is a wrap style, not a slip dress.
  - Gaps: Gold hoop earrings (optional)
- **Sleek Black Column with a Soft Edge** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Tuck the black camisole into the champagne satin skirt to create a seamless, fluid line, mimicking a dress. / Wear the blazer open to maintain the long, sleek silhouette of the camisole and skirt combination.
  - Declared deviations: The 'dress' is a two-piece camisole and skirt.; The color palette is black and champagne, not emerald green.; The outer layer is a blazer, not a biker jacket, and is not cropped.
  - Gaps: Gold hoop earrings (optional)

**agentic** · 18.0 s · all objective checks pass · human rating: ___/5
- **Sleek Green Edge** (closest) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Forest green wrap midi dress → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Wear the blazer open to highlight the long line of the dress and maintain the layered proportion. / Ensure the dress is smoothed for a clean, fluid column silhouette.
  - Declared deviations: The dress is a jersey wrap midi instead of a satin slip, altering the material sheen and exact silhouette.; A fitted blazer replaces the leather biker jacket, changing the 'tough edge' to a more tailored one and the material from leather to suiting.; Ankle boots replace strappy heels, offering a different type of sleekness and formality.
  - Gaps: Gold hoop earrings (optional)
  - Gemini critic: approved after 0 revision(s); notes: The 'tough edge' of the inspiration's biker jacket is completely lost with the formal blazer. The blazer, while structured, lacks the specific cropped, edgy silhouette that creates the dynamic contrast with the fluid dress.; The forest green wrap dress, described as fluid jersey, lacks the luxurious sheen and bias-cut drape of the inspiration's satin slip dress. This significantly reduces the 'evening polish' and 'sheen' essential traits.; The wrap dress has a defined waist and a different neckline/sleeve structure than a slip dress, which alters the 'long fluid column' effect, especially when worn under a blazer. The blazer also appears longer than the cropped jacket, further obscuring the desired proportion.
- **Champagne & Black Column** (creative) — 3/4 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Black cropped leather biker jacket, Black silk-look camisole → Emerald satin bias-cut slip dress, Champagne satin midi skirt → Emerald satin bias-cut slip dress, Black leather ankle boots → Black strappy heeled sandals
  - How to wear: Tuck the black camisole neatly into the champagne skirt to create a seamless, long column silhouette. / Wear the blazer open to maintain the layered line and highlight the contrast between the black top and champagne skirt.
  - Declared deviations: The base is a two-piece (camisole + skirt) instead of a single slip dress.; The color palette shifts from emerald and black to champagne and black.; A fitted blazer replaces the leather biker jacket, changing the material and specific 'toughness'.; Ankle boots replace strappy heels.
  - Gaps: Gold hoop earrings (optional)
  - Gemini critic: approved after 0 revision(s); notes: The 'tough edge' from the inspiration's leather biker jacket is reinterpreted as a more tailored edge with the blazer. While a valid creative choice, it's less overtly 'tough'.; The ankle boots, while sleek, are a more substantial shoe than the delicate strappy heels of the inspiration, slightly altering the overall lightness of the look.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 2 of 2

### shopping-disabled

_Shopping disabled: gaps carry no sourcing hints._

**single_pass** · 13.0 s · all objective checks pass · human rating: ___/5
- **Polished Travel Layers** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - How to wear: Wear the blazer open to maintain a long vertical line. / Ensure the knit is tucked in or neatly layered under the blazer for a streamlined look.
  - Declared deviations: The outer layer is an oversized blazer instead of a belted trench coat, altering the waist definition from the inspiration.
  - Gaps: Wide-brim straw-coloured hat (optional)
- **Modern Navy & Black Ensemble** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Black fitted blazer → Beige belted double-breasted trench coat, Navy Breton striped tee → Navy fine-knit crew-neck sweater, Black straight-leg trousers → Ecru high-rise wide-leg trousers, Black leather ankle boots → White minimal sneakers, Tan structured tote → extra
  - How to wear: Wear the blazer open for a relaxed, yet polished feel. / Tuck in the Breton tee for a neat finish.
  - Declared deviations: The palette shifts from light neutrals to a darker, more contrasting navy and black. The silhouette is more structured and streamlined due to the fitted blazer and straight-leg trousers.
  - Gaps: Wide-brim straw-coloured hat (optional)

**agentic** · 39.2 s · all objective checks pass · human rating: ___/5
- **Polished Travel Layers** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Camel oversized blazer → Beige belted double-breasted trench coat, Navy fine-knit sweater → Navy fine-knit crew-neck sweater, Ecru wide-leg trousers → Ecru high-rise wide-leg trousers, White leather sneakers → White minimal sneakers
  - How to wear: Wear the camel blazer open to showcase the vertical line and layered effect. / Ensure the blazer's sleeves are slightly pushed up or cuffed to maintain a relaxed, modern feel.
  - Declared deviations: The outerwear is a blazer instead of a long trench coat, changing the 'long vertical line' to a shorter, boxier silhouette.; The waist definition is less pronounced without a belted trench.
  - Gaps: Wide-brim straw-coloured hat (optional)
  - Gemini critic: approved after 0 revision(s); notes: The camel oversized blazer, while a good color match, significantly alters the silhouette and proportion. It lacks the length and belted waist definition of the inspiration's trench coat, losing the 'long vertical line' and 'belted at natural waist' essential traits. The oversized nature also creates a boxier top half that doesn't quite balance the wide-leg trousers in the same way as the long, fluid trench.; The core 'long vertical line' and 'waist definition' from the belted trench are lost with the oversized blazer. While the stylist declared this deviation, it's a critical element of the inspiration's overall proportion and aesthetic that isn't adequately reinterpreted.; While the individual pieces work, the combination of an oversized blazer with wide-leg trousers can sometimes lean into an overly voluminous silhouette if not carefully balanced. The inspiration's trench provided a more structured, defined top line despite its length.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

### user-exclusion-and-keep

_Preference adherence: excluded pieces never appear, kept pieces always do._

**single_pass** · 18.9 s · all objective checks pass · human rating: ___/5
- **Classic Tailored Neutrals** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open to maintain the relaxed feel. / Ensure the white shirt is neatly tucked or styled for a clean line under the blazer.
- **Modern Sage & Black Contrast** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, Navy fine-knit sweater → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open to showcase the clean lines of the knit. / Ensure the knit is neatly tucked or falls smoothly for a streamlined silhouette.
  - Declared deviations: Colour palette shifted from warm neutrals to cooler, more muted tones.; Footwear changed from loafers to sleek ankle boots for a modern edge.

**agentic** · 44.5 s · all objective checks pass · human rating: ___/5
- **Modern Classic with a Twist** (closest) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, White poplin shirt → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open to maintain the relaxed feel and show off the clean base layer. / Half-tuck the white shirt into the trousers at the front to maintain a casual ease while hinting at the waistline. / Ensure the black ankle boots are sleek enough to not disrupt the elongated leg line of the trousers.
  - Declared deviations: Used a white poplin shirt instead of a jersey t-shirt, introducing a crisper texture and slightly more volume.; Used black ankle boots instead of brown loafers, shifting the shoe color and style but maintaining polish.
  - Gemini critic: approved after 0 revision(s); notes: The inspiration features a soft jersey t-shirt as a base layer, contributing to the 'easy smart-casual' feel. The crisp poplin shirt, while clean, introduces a more formal and structured element that deviates from the relaxed base layer of the DNA.; The user explicitly excluded 's_white_tee' in their preferences, yet the inspiration's base layer is a white crew-neck t-shirt. The stylist has used a white poplin shirt as a substitute, which changes the texture and formality.; The black ankle boots, while sleek, introduce a slightly dressier and more winter-appropriate feel compared to the brown loafers in the inspiration, subtly shifting the overall casualness.
- **Green Tailoring & Stripes** (creative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Sage tailored blazer → Camel oversized single-breasted blazer, Navy Breton striped tee → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the blazer open to allow the striped tee to be visible and maintain the relaxed silhouette. / Partially tuck the Breton tee into the trousers to define the waist without being too formal. / Use the tan tote to introduce warmth and complement the sage green blazer.
  - Declared deviations: Introduced sage green blazer instead of camel, and a navy/white striped tee instead of solid white, shifting the color palette.; Used black ankle boots instead of brown loafers.
  - Gemini critic: approved after 0 revision(s); notes: The inspiration's palette is minimal neutrals with warm camel. This look introduces sage green and navy/white stripes, which, while harmonious, shift the 'minimal neutral palette' trait significantly.
- **Monochromatic Chic with a Pop** (alternative) — 5/5 pieces already in your closet · No new purchase needed
  - Pieces: Camel oversized blazer → Camel oversized single-breasted blazer, Black silk-look camisole → White crew-neck t-shirt, Black straight-leg trousers → Black straight-leg trousers, Black leather ankle boots → Brown leather penny loafers, Tan structured tote → Tan structured tote bag
  - How to wear: Wear the camel blazer open to maintain its relaxed feel and showcase the sleek black camisole underneath. / Tuck the black camisole fully into the high-rise black trousers for a clean, elongated line. / Ensure the black ankle boots are sleek and do not break the continuous line of the trousers.
  - Declared deviations: The base layer is a sleek black camisole instead of a white t-shirt, creating a darker, more monochromatic internal look.; The primary color contrast is black and camel, rather than the original's black, white, and camel.; The shoes are black ankle boots instead of brown loafers, leaning slightly sleeker.
  - Gemini critic: approved after 1 revision(s); notes: The inspiration's palette includes crisp white for a medium contrast, while this look uses a black camisole, shifting the internal contrast to a darker, more monochromatic feel. This is a declared deviation, but it does alter the 'easy smart-casual' feel slightly towards a sleeker, more evening-appropriate vibe.; The satin-finish camisole, while sleek, introduces a slightly dressier texture compared to the inspiration's casual cotton tee. This subtly elevates the formality of the base layer, making it less 'easy' than the original.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 2 of 3; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### ambiguous-not-an-outfit

_Ambiguous/non-outfit photo: no looks, honest reason._

**single_pass** · 0.0 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): We couldn't find a wearable outfit in this image. Try a clearer full-outfit photo.

**agentic** · 0.0 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): We couldn't find a wearable outfit in this image. Try a clearer full-outfit photo.
