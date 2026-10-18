# Rewear — engine comparison (live Gemini)

Variants: `agentic` {'styling_engine': 'agentic'}, `agentic_no_images` {'styling_engine': 'agentic', 'critic_uses_images': False}, `agentic_no_revision` {'styling_engine': 'agentic', 'max_refinement_rounds': 0}

## Summary

| Variant | Objective checks | Invalid owned ids | Looks returned | With styling instructions | Critic rejections | No-look runs (legit / suspect) | Median total | Max total |
|---|---|---|---|---|---|---|---|---|
| agentic | 4/5 | 0 | 6 | 6 | 3 | 1 / 1 | 25.6 s | 43.4 s |
| agentic_no_images | 5/5 | 0 | 6 | 6 | 5 | 1 / 0 | 29.6 s | 47.7 s |
| agentic_no_revision | 4/5 | 0 | 3 | 3 | 4 | 2 / 1 | 18.6 s | 35.0 s |

### Median per-stage latency (ms) and cost counters

| Variant | retrieval_ms | knowledge_ms | composer_ms | stylist_ms | critic_image_prep_ms | critic_ms | revision_ms | total_ms | passes | stylist_calls | critic_calls | critic_images | critic_image_tokens | stylist_tokens | critic_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| agentic | 9 | 0 | – | 15653 | 19 | 10987 | 6377 | 25553 | 2 | 2 | 1 | 3 | 903 | 10918 | 5750 |
| agentic_no_images | 6 | 0 | 8319 | 17463 | – | 12141 | 13415 | 29586 | 2 | 2 | 2 | – | – | 11751 | 7913 |
| agentic_no_revision | 6 | 0 | – | 10263 | 82 | 8228 | – | 18608 | 1 | 1 | 1 | 3 | 774 | 5951 | 5313 |

`revision_ms` = model time in passes after the first; `critic_ms` excludes image preparation (`critic_image_prep_ms`). Values are medians per request.

## Looks per case (human rating fields are intentionally blank)

### real-denim-skirt

_The reported failure: white tucked button-down + high-waisted denim midi skirt + sneakers, styled from a real 7-piece wardrobe with no white shirt or denim skirt. A strong answer protects the defined waist and relaxed mood (e.g. the belted shirt-dress, or sweater + skirt with a tuck and casual shoes) instead of stacking dressy substitutes and an unneeded jacket._

**agentic** · 25.6 s · all objective checks pass · human rating: ___/5
- **Modern Casual Chic** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Black high-rise wide-leg jeans → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Fully tuck the black sweater into the high-rise jeans to emphasize your waist. / Ensure the jeans fall to a long length, creating an elongated line over your sneakers.
  - Declared deviations: Flipped color contrast (dark top, dark bottom instead of light top, mid-tone bottom).; Wide-leg jeans instead of an A-line midi skirt.; Soft knit top instead of crisp cotton.
  - Gemini critic: approved after 0 revision(s); notes: The black crewneck sweater appears to be a slightly cropped, boxy fit. When fully tucked into the high-rise wide-leg jeans, it creates a very bulky waistline that disrupts the clean, defined waist intended by the inspiration. The inspiration's shirt is relaxed but tucks cleanly.; The inspiration features a crisp, structured top (button-down) against a rigid bottom (denim skirt). This look uses a soft knit sweater and flowy wide-leg jeans, which fundamentally changes the material interplay and overall silhouette from crisp and structured to soft and flowing. The 'relaxed but put-together' feel of the inspiration comes from the crispness, which is lost here.; The monochrome black palette, while sleek, loses the medium-high contrast of the inspiration (white top/mid-blue bottom). While declared, the resulting look is much heavier and less 'light' than the original, which impacts the overall feel.
- **Satin & Knit Contrast** (creative) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Burgundy satin midi skirt → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Half-tuck the black sweater at the front to maintain the defined waist while allowing for some relaxed drape. / Let the satin skirt hang freely to showcase its fluid movement and midi length. / Wear the platform sneakers to add a contemporary, casual edge to the dressier skirt.
  - Declared deviations: Dark top and rich-toned bottom instead of light top and mid-tone bottom.; Satin skirt instead of denim, introducing a lustrous texture and dressier feel.; Burgundy color instead of mid blue.
  - Gemini critic: approved after 0 revision(s); notes: The instruction to 'half-tuck' the black sweater, given its slightly cropped and boxy nature, might still create some bulk at the waist with the sleek satin skirt. While better than a full tuck, it could still disrupt the clean line of the skirt.
- **Effortless Shirtdress & Sneakers** (alternative) — 2/2 pieces already in your closet · No new purchase needed
  - Pieces: Tan belted shirt dress → White cotton button-down shirt + High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Wear the shirtdress belted at your natural waist to create a strong, defined silhouette. / Roll up the sleeves of the shirtdress for a more relaxed, casual feel. / Ensure the shirtdress buttons are undone to create a v-neck, adding to the relaxed aesthetic.
  - Declared deviations: Single-piece dress instead of separates.; Tan color replaces the white and mid-blue palette.; Matte woven fabric instead of crisp cotton and rigid denim.
  - Gemini critic: approved after 0 revision(s); notes: While the shirtdress captures the overall feel, it lacks the distinct two-piece contrast (light top/mid-tone bottom) and the specific material interplay (crisp cotton/rigid denim) of the inspiration. This is a declared deviation, but it's worth noting as a slight departure from the original's specific textural story.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 3 of 3

**agentic_no_images** · 25.6 s · all objective checks pass · human rating: ___/5
- **Modern Denim & Knit** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Black high-rise wide-leg jeans → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Half-tuck the front of the black sweater into the jeans to emphasize your waist. / Roll up the sleeves of the sweater for an effortless, relaxed look.
  - Declared deviations: Color palette shifts to black and white, losing the 'light top against mid-tone bottom' contrast.; Wide-leg jeans replace the A-line midi skirt, changing the exact silhouette and removing the slit.; Soft knit replaces crisp cotton for the top.
  - Gemini critic: approved after 0 revision(s); notes: The essential trait of 'light top against a mid-tone bottom' is completely lost, replaced by a dark top and dark bottom, which fundamentally alters the visual balance and contrast of the inspiration.; The styling instruction to half-tuck a relaxed fit knit sweater into high-rise wide-leg jeans is likely to create bulk and disrupt the clean waist definition, rather than enhance it. The knit fabric is also less structured than the crisp cotton of the inspiration.; While the wide-leg jeans provide an elongated lower line, they lack the specific A-line silhouette and front slit of the inspiration's skirt, which contributed to movement and a distinct shape.
- **Effortless Tan Shirtdress** (creative) — 2/2 pieces already in your closet · No new purchase needed
  - Pieces: Tan belted shirt dress → White cotton button-down shirt + High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Wear the shirtdress belted at your natural waist to emphasize the defined waist. / Roll up the sleeves of the shirtdress for a more relaxed and effortless feel.
  - Declared deviations: Replaces separate top and bottom with a single shirtdress.; Color palette changes from white/mid-blue to monochromatic tan.; Material changes from crisp cotton/rigid denim to a matte woven fabric.
  - Gemini critic: approved after 0 revision(s); notes: The color palette shifts significantly from the inspiration's white/mid-blue to monochromatic tan, losing the specific 'light top against mid-tone bottom' contrast. However, this is a declared deviation and the resulting monochromatic look is coherent.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 2 of 3; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

**agentic_no_revision** · 18.6 s · all objective checks pass · human rating: ___/5
- **Modern Monochrome Casual** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Black high-rise wide-leg jeans → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Half-tuck the front of the black sweater into the jeans to emphasize the defined waist. / Ensure the sweater is not too bulky to maintain a streamlined top half.
  - Declared deviations: Monochromatic black bottom half instead of mid-blue denim and white top.; Wide-leg jeans instead of an A-line midi skirt with a slit.; Soft knit sweater instead of crisp cotton shirt.; Flipped light/dark contrast (dark top, dark bottom).
  - Gemini critic: approved after 0 revision(s); notes: The essential trait of 'light top against a mid-tone bottom' is completely inverted to 'dark top against a dark bottom', fundamentally altering the inspiration's visual balance and aesthetic.; The black crewneck sweater, even half-tucked, appears too voluminous and boxy to create the 'relaxed but put-together' and 'defined waist' silhouette of the inspiration. The image shows a relatively short, wide sweater that will likely create bulk rather than a streamlined top half when tucked.; The soft knit of the sweater lacks the crispness and structure of the inspiration's cotton shirt, changing the overall texture and formality slightly from the original 'crisp cotton against rigid denim' material interplay.
- **Relaxed Shirtdress Chic** (creative) — 2/2 pieces already in your closet · No new purchase needed
  - Pieces: Tan belted shirt dress → White cotton button-down shirt + High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - How to wear: Ensure the shirtdress is belted at your natural waist to create the defined silhouette. / Roll up the sleeves of the shirtdress to echo the inspiration's relaxed styling and add an effortless touch.
  - Declared deviations: Single garment (shirtdress) replaces top and bottom.; Tan color instead of white/mid-blue palette.; Matte woven fabric instead of crisp cotton and rigid denim.; No explicit slit, relying on the A-line flow for movement.
  - Gemini critic: approved after 0 revision(s); notes: The tan color palette deviates significantly from the inspiration's white and mid-blue, and the matte woven fabric lacks the crispness of cotton and rigidity of denim. While declared, this changes the overall material and color contrast feel.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 2 of 2

### real-emerald-evening

_Evening slip dress + cropped leather jacket + heels, from the real wardrobe (satin skirt, tweed and suede jackets, no heels)._

**agentic** · 43.4 s · >=1 looks · human rating: ___/5
- No looks — possible over-rejection (stylist proposed valid looks; critic rejected all): No suitable top or shoes in the wardrobe can create an 'evening' look with the available bottom (satin skirt) and outerwear (tweed jacket). The black sweater is too casual, and there are no dressy shoes. Therefore, the essential traits of 'sleek evening glamour' and 'evening polish' cannot be met for an 'event' occasion.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

**agentic_no_images** · 33.5 s · all objective checks pass · human rating: ___/5
- **Edgy Event Glamour: Burgundy & Tweed Remix** (creative) — 2/4 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Cream embellished tweed jacket → Black cropped leather biker jacket, Burgundy satin midi skirt → Emerald satin bias-cut slip dress
  - How to wear: Tuck the black sweater neatly into the burgundy satin skirt to maintain a smooth, continuous line. / Wear the cream tweed jacket open over the outfit.
  - Declared deviations: Color palette shifted from emerald/black to burgundy/black/cream.; Material contrast is satin/tweed instead of satin/leather.
  - Gaps: Black strappy heeled sandals (essential); Gold hoop earrings (optional)

**agentic_no_revision** · 35.0 s · >=1 looks · human rating: ___/5
- No looks — possible over-rejection (stylist proposed valid looks; critic rejected all): This creative interpretation successfully captures the fluid column and sheen, but the choice of the tweed jacket fundamentally alters the essential 'tough edge' and high-contrast aesthetic of the inspiration, resulting in a less coherent and less edgy look that needs revision. What didn't work: Burgundy Sheen with Textured Edge: [critical] fidelity: The 'sheen against a tough edge' essential trait is completely lost. The inspiration relies on the stark material contrast between fluid satin and edgy leather. The proposed tweed jacket, while structured and cropped, introduces a 'polished, textured edge' that lacks the 'toughness' and sleekness of leather, fundamentally altering the aesthetic. Fix: Replace the cream tweed jacket with the rust suede-like jacket. While not leather, its matte, slightly rugged texture offers a better approximation of the 'tough edge' compared to the polished tweed. The color contrast would also be more aligned with the inspiration's dark jacket over a jewel tone.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

### real-camel-work

_Camel blazer + tee + straight trousers + loafers for work, from the real wardrobe (no blazer, no tee, no loafers): expect honest gaps or declared deviations._

**agentic** · 33.5 s · all objective checks pass · human rating: ___/5
- **Modern Suede Contrast** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - How to wear: Wear the rust suede jacket open to highlight the layering and maintain a relaxed vibe. / Half-tuck the black sweater into the high-rise jeans to define your waist and create a long leg line. / Let the wide-leg jeans fall over the top of the sneakers for a contemporary silhouette.
  - Declared deviations: Outerwear is a rust suede-like jacket instead of a camel suiting blazer, introducing a strong color and different texture.; Base layer is a black knit sweater instead of a white cotton tee, creating a darker internal column.; Bottoms are wide-leg denim jeans instead of straight-leg suiting trousers, shifting formality and silhouette.; Shoes are platform sneakers instead of classic loafers, for a more modern, casual feel.
  - Gaps: Tan structured tote bag (optional)
  - Gemini critic: approved after 0 revision(s); notes: While the rust suede jacket is a relaxed outer layer, it lacks the 'tailored' aspect of the inspiration's blazer. It reads more as a utility jacket or overshirt, shifting the aesthetic from 'minimal, polished smart-casual tailoring' to a more rugged, casual vibe.; The styling instruction to 'half-tuck the black sweater' might disrupt the clean, elongated line intended by the wide-leg jeans, especially if the sweater is bulky. The inspiration's tee is loosely tucked, maintaining a smooth line.; The combination of a suede-like jacket, knit sweater, denim jeans, and platform sneakers leans heavily into casual textures. While coherent, it loses some of the 'polished' feel of the inspiration's suiting and leather loafers.
- **Effortless Tan Shirtdress** (alternative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Tan belted shirt dress → White crew-neck t-shirt + Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - How to wear: Wear the tan belted shirt dress buttoned up and belted to create a defined waist and A-line shape. / Leave the rust suede jacket open to maintain a relaxed, layered look. / Ensure the shirtdress length works well with the platform sneakers, allowing a glimpse of ankle or falling just above the shoe.
  - Declared deviations: Uses a single tan shirtdress instead of separate top and bottom, changing the core structure.; Outerwear is a rust suede-like jacket instead of a camel suiting blazer, introducing a strong color and different texture.; Shoes are platform sneakers instead of classic loafers, for a more modern, casual feel.
  - Gaps: Tan structured tote bag (optional)
  - Gemini critic: approved after 0 revision(s); notes: The inspiration's 'undefined waist' (due to the open blazer) is replaced by a 'defined waist' from the belted shirtdress. While a deviation, it's a coherent and stylish reinterpretation for an 'alternative' strategy.; The combination of a matte woven shirtdress and a suede-like jacket works well, but the overall material mix is more casual than the inspiration's suiting and jersey, shifting the 'polished' aspect slightly towards 'effortless casual'.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 2 of 3; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

**agentic_no_images** · 47.7 s · all objective checks pass · human rating: ___/5
- **Monochromatic Modern Ease** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - How to wear: Wear the rust jacket open to highlight the dark column underneath and maintain the layered look. / Ensure the black sweater is loosely tucked or hits at the hip to maintain a clean line. / Let the wide-leg jeans drape fully to emphasize the elongated leg line.
  - Declared deviations: Rust suede-like jacket replaces camel suiting blazer, changing color, material, and formality slightly.; Black sweater replaces white t-shirt, creating a monochromatic dark base.; Wide-leg denim jeans replace straight-leg suiting trousers, altering material and leg volume.; Platform sneakers replace leather loafers, changing shoe style and color.
  - Gaps: Tan structured tote bag (optional)
  - Gemini critic: approved after 0 revision(s); notes: The material of the rust jacket (suede-like) and the jeans (denim) are less formal than the suiting materials of the inspiration, making the overall look lean slightly more casual than the original 'polished smart-casual tailoring'.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 1 of 3; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1

**agentic_no_revision** · 22.4 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): Look 0 struggles with fidelity due to the highly embellished tweed jacket, which fundamentally alters the inspiration's minimal and relaxed tailored aesthetic, while Look 1 fails to achieve coherence and loses essential DNA traits by combining disparate textures and silhouettes into a disjointed outfit. What didn't work: Modern Tailored Cream: [critical] fidelity: The cream embellished tweed jacket fundamentally alters the 'relaxed tailored top layer' and 'minimal' aesthetic of the inspiration. Its cropped, collarless, and highly embellished nature is a direct contrast to the oversized, relaxed, matte blazer, making it unsuitable for a 'closest' interpretation. Fix: Replace the cream tweed jacket with the rust suede-like jacket for a more relaxed, less formal outer layer, or the tan belted shirt dress worn open as an outer layer if a longer silhouette is desired.; Suede Chic with a Pop: [critical] coherence: The combination of a casual suede-like jacket, a relaxed black sweater, a lustrous burgundy satin midi skirt, and chunky platform sneakers lacks overall coherence. The skirt's material and drape feel disconnected from the casual, matte top half and footwear, creating a disjointed aesthetic. Fix: To create a coherent outfit, either swap the skirt for a more casual bottom like the black wide-leg jeans, or swap the jacket and sneakers for more elevated pieces that complement the satin skirt.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 0 of 2

### real-satin-material-challenge

_Material challenge: satin slip skirt dressed down with a slouchy sweatshirt and sneakers. The burgundy satin skirt fits; the stylist must keep the dressed-down mood._

**agentic** · 22.5 s · all objective checks pass · human rating: ___/5
- **Burgundy Satin & Black Knit Contrast** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - How to wear: Half-tuck the front of the black sweater into the skirt to emphasize the waistline. / Let the sweater drape loosely at the back for a relaxed silhouette.
  - Declared deviations: The palette is darker (black and burgundy instead of grey and champagne).; The skirt is A-line instead of bias-cut, adding slightly more volume.
  - Gemini critic: approved after 0 revision(s); notes: The black sweater, while relaxed, appears to be a standard knit sweater rather than an oversized sweatshirt, slightly reducing the 'sporty' aspect of the high-low contrast.; The skirt is declared as A-line, which is a slight deviation from the bias-cut slip skirt of the inspiration, potentially altering the fluid drape slightly, though the image still shows a sleek, fluid line.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 0 look(s); 0 passed validation

**agentic_no_images** · 29.6 s · all objective checks pass · human rating: ___/5
- **Burgundy Satin & Black Knit** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - How to wear: Half-tuck the front of the black sweater into the skirt to define your waist, mimicking the inspiration's proportions. / Let the burgundy satin skirt flow freely to showcase its elegant drape and midi length.
  - Declared deviations: Top color is black instead of heather grey.; Skirt color is burgundy instead of champagne.; Sneakers have black accents rather than being all white.
  - Gemini critic: approved after 0 revision(s); notes: The overall palette is darker and richer than the inspiration's soft neutrals, shifting the mood slightly from light and airy to more sophisticated.
- **Shirtdress & Sneakers** (alternative) — 2/2 pieces already in your closet · No new purchase needed
  - Pieces: Tan belted shirt dress → Oversized heather grey crewneck sweatshirt + Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - How to wear: Wear the shirtdress belted at your natural waist to create the defined silhouette, similar to the tucked sweatshirt. / Ensure the shirtdress falls to a midi length to maintain the long, fluid line of the bottom. / Leave the dress unbuttoned at the bottom few buttons for a more relaxed, airy feel.
  - Declared deviations: The 'fluid midi skirt' is interpreted as a fluid midi shirtdress, combining top and bottom into one piece.; The material contrast shifts from satin/fleece to matte woven fabric/leather, but the high-low principle remains.; Palette shifts from neutrals (champagne/grey) to camel/white.
  - Gemini critic: approved after 1 revision(s); notes: The essential 'high-low mix of sleek and sporty' is significantly weakened. The inspiration relies on the distinct material contrast between a sleek satin skirt and a sporty fleece sweatshirt. Replacing both with a single matte woven shirtdress loses this crucial textural interplay, making the outfit less dynamic and more uniform in texture.; While the shirtdress is relaxed, its matte woven fabric doesn't provide the 'sporty' material counterpoint to the 'sleek' element that the inspiration's fleece sweatshirt did. The overall material story becomes less about contrast and more about a singular, casual woven texture.; The styling instruction to 'leave the dress unbuttoned at the bottom few buttons' could disrupt the desired fluid, unbroken line of the midi skirt, potentially creating a less cohesive silhouette than intended.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

**agentic_no_revision** · 18.1 s · all objective checks pass · human rating: ___/5
- **Burgundy Satin & Black Knit** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - How to wear: Half-tuck the front of the black sweater into the skirt to define your waist. / Let the burgundy satin skirt flow freely to maintain its fluid silhouette.
  - Declared deviations: Skirt color is burgundy instead of champagne.; Top color is black instead of heather grey.; Top material is a knit instead of fleece jersey.
  - Gemini critic: approved after 0 revision(s); notes: The black sweater, while relaxed, is not as oversized as the inspiration's sweatshirt, slightly reducing the 'volume on top' aspect.; The skirt is A-line rather than a bias-cut slip, which slightly alters the fluid silhouette compared to the inspiration, though it still reads as a fluid midi.
- Workflow: Stylist proposed 2 look(s); 2 passed validation → Critic approved 1 of 2

### real-no-good-outfit

_No good outfit exists: black-tie tuxedo look from a casual 7-piece wardrobe. A good system admits the gap instead of forcing a match._

**agentic** · 7.9 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): The inspiration is a very specific 'strict black tie' look requiring formal black tailoring, a crisp white dress shirt, and patent formal shoes. Your wardrobe contains only casual and smart-casual items, with no formal wear, no matching black tailoring, and no suitable formal shirting or shoes. Therefore, it's not possible to create any coherent interpretation of this look while preserving its essential traits of matching black tailoring, a crisp white shirt, and strict formality.
- Workflow: Stylist proposed 0 look(s); 0 passed validation

**agentic_no_images** · 6.5 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): Your wardrobe lacks the essential formal black tailoring, crisp white shirt, and formal shoes required for a black-tie look. The available garments are primarily casual or smart-casual, making it impossible to recreate the strict formality and specific aesthetic of the inspiration.
- Workflow: Stylist proposed 0 look(s); 0 passed validation

**agentic_no_revision** · 6.3 s · all objective checks pass · human rating: ___/5
- No looks — legitimate no-match (expected for this case): The wardrobe lacks any formal attire or pieces that can be styled to achieve a formal black-tie look. Specifically, there are no black tailored garments (jacket or trousers), no crisp white shirt, and no formal shoes. The owned garments are all casual or smart-casual, making it impossible to recreate the essential traits of 'matching black tailoring', 'crisp white shirt', and 'strict formality'.
- Workflow: Stylist proposed 0 look(s); 0 passed validation
