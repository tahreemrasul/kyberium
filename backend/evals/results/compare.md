# Rewear — baseline vs agentic stylist (live Gemini)

Baseline = single Gemini composition pass + deterministic validation.
Agentic = ADK workflow: stylist → validation → multimodal critic → bounded refinement (max_refinement_rounds=1).

## Summary

| Engine | Cases passed | Invalid owned ids | Looks returned | Looks with styling instructions | Critic interventions | Median latency | Max latency | Avg tokens* |
|---|---|---|---|---|---|---|---|---|
| single_pass | 5/5 | 0 | 7 | 7 | 0 | 14577 ms | 17555 ms | n/a |
| agentic | 5/5 | 0 | 4 | 4 | 4 | 41352 ms | 53806 ms | 15490 |

*Token totals are tracked for the agentic workflow's model calls (single-pass logs them per call).

## Per case

| Case | Engine | Objective checks | Looks | Latency | Rounds | Critic flags |
|---|---|---|---|---|---|---|
| real-denim-skirt | single_pass (gemini) | all pass | 2 | 15657 ms | 1 | 0 |
| real-denim-skirt | agentic (agentic) | all pass | 1 | 41352 ms | 2 | 1 |
| real-emerald-evening | single_pass (gemini) | all pass | 1 | 14577 ms | 1 | 0 |
| real-emerald-evening | agentic (gemini) | all pass | 1 | 46766 ms | 1 | 0 |
| real-camel-work | single_pass (gemini) | all pass | 3 | 17555 ms | 1 | 0 |
| real-camel-work | agentic (agentic) | all pass | 1 | 53806 ms | 2 | 3 |
| real-satin-material-challenge | single_pass (gemini) | all pass | 1 | 7846 ms | 1 | 0 |
| real-satin-material-challenge | agentic (agentic) | all pass | 1 | 12299 ms | 1 | 0 |
| real-no-good-outfit | single_pass (gemini) | all pass | 0 | 5934 ms | 1 | 0 |
| real-no-good-outfit | agentic (agentic) | all pass | 0 | 5143 ms | 1 | 0 |

## Side-by-side looks for human rating

Rate each engine's output 1–5 for coherence, inspiration fidelity and styling usefulness.

### real-denim-skirt

_The reported failure: white tucked button-down + high-waisted denim midi skirt + sneakers, styled from a real 7-piece wardrobe with no white shirt or denim skirt. A strong answer protects the defined waist and relaxed mood (e.g. the belted shirt-dress, or sweater + skirt with a tuck and casual shoes) instead of stacking dressy substitutes and an unneeded jacket._

**single_pass** — human rating: ___/5
- **Modern Casual with Satin** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Burgundy satin midi skirt → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - Coherence: This look achieves a relaxed yet put-together aesthetic. The dark top against the rich burgundy skirt maintains a similar visual weight distribution to the inspiration, while the satin fabric adds a touch of elevated casualness. The platform sneakers ground the look with a modern, comfortable vibe.
  - How to wear: Tuck the black sweater into the high-waisted satin skirt to define the waist. / Ensure the sweater is not too bulky for tucking; if it is, consider a half-tuck or belting over it. / Pair with the platform sneakers for a modern, casual finish.
  - Declared deviations: Color palette shifted from white/mid-blue to black/burgundy.; Fabric changed from crisp cotton/rigid denim to knit/satin.
- **Monochromatic Modern Casual** (creative) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Black high-rise wide-leg jeans → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - Coherence: This look creates a sleek, monochromatic base with the black sweater and wide-leg jeans, offering a different take on the 'relaxed but put-together' aesthetic. The white and black sneakers provide a subtle contrast and maintain the casual mood.
  - How to wear: Tuck the black sweater into the high-rise wide-leg jeans to emphasize the waist and create a long leg line. / Consider a French tuck if a full tuck feels too bulky. / Wear with the platform sneakers for a comfortable, modern finish.
  - Declared deviations: Color palette is largely monochromatic black with white shoes, instead of a white top and blue bottom.; Bottom silhouette is wide-leg jeans instead of an A-line midi skirt.; Top is a sweater instead of a crisp shirt.

**agentic** — human rating: ___/5
- **Modern Dark Denim** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → White cotton button-down shirt, Black high-rise wide-leg jeans → High-waisted mid-blue denim midi skirt with front slit, White and black platform sneakers → White low-top sneakers
  - Coherence: This outfit achieves a modern, relaxed yet put-together feel by pairing a soft knit sweater with structured denim jeans. The high-rise wide-leg jeans create a long, clean line from the waist down, balancing the relaxed volume of the sweater. The matte textures of the sweater and jeans, along with the casual sneakers, ensure a cohesive, contemporary vibe.
  - How to wear: Half-tuck the black sweater into the front of the jeans to emphasize your waist. / Let the sweater drape loosely at the back to maintain a relaxed silhouette. / Ensure the jeans sit at your natural waist for the intended high-rise effect.
  - Declared deviations: Color palette shifts to a darker, monochromatic feel (black top and bottom) instead of white and mid-blue, reversing the light/dark contrast.; Bottom changes from an A-line midi skirt to wide-leg jeans, altering the specific silhouette but maintaining the elongated lower line and structured denim feel.; Material contrast changes from crisp cotton/rigid denim to soft knit/matte denim, maintaining casualness but losing the 'crisp' element.
  - Critic: approved after 1 revision(s); notes: The inspiration features a crisp, structured white button-down shirt, which provides a distinct material contrast and a 'put-together' feel. The black crewneck sweater, while relaxed, lacks the crispness and structure, altering the material interplay and the 'put-together' aspect of the top.; The inspiration relies on a medium-high color contrast of crisp white against mid-blue. This look shifts to a monochromatic black palette, losing the light-dark contrast and the visual interest it provides. The declared deviation acknowledges this, but it's a significant departure from an essential trait.; The inspiration's volume balance is a relaxed shirt controlled by a full tuck into a streamlined midi skirt. Here, the relaxed sweater is half-tucked into wide-leg jeans. While the jeans create a long line, the combination of a relaxed, potentially bulky sweater (even half-tucked) with very wide-leg jeans can create a heavier, less streamlined silhouette than the inspiration's A-line midi skirt, potentially losing some of the 'chic' and 'put-together' feel.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 0 of 1; sending feedback to the stylist → Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### real-emerald-evening

_Evening slip dress + cropped leather jacket + heels, from the real wardrobe (satin skirt, tweed and suede jackets, no heels)._

**single_pass** — human rating: ___/5
- **Edgy Evening Shine** (creative) — 2/4 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Cream embellished tweed jacket → Black cropped leather biker jacket, Burgundy satin midi skirt → Emerald satin bias-cut slip dress
  - Coherence: This look balances the fluid sheen of the satin skirt with the structured texture of the tweed jacket. The dark top grounds the outfit, while the cream jacket provides a bright contrast. The overall silhouette maintains the short-over-long proportion, creating an elegant yet contemporary feel suitable for an event.
  - How to wear: Ensure the black sweater is neatly tucked into the burgundy satin skirt to maintain a clean, long line. / Wear the tweed jacket open to showcase the base layers and maintain the desired proportion.
  - Declared deviations: The base is a two-piece skirt and sweater instead of a slip dress, resulting in a less revealing neckline and different texture.; The outerwear is a tweed jacket instead of a leather biker jacket, shifting the 'edge' to 'sophistication' and introducing a lighter color.
  - Gaps: Black strappy heeled sandals (essential); Gold hoop earrings (optional)

**agentic** — human rating: ___/5
- **Satin & Tweed Event Look** (creative) — 2/4 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Cream embellished tweed jacket → Black cropped leather biker jacket, Burgundy satin midi skirt → Emerald satin bias-cut slip dress
  - Coherence: The look maintains the inspiration's core structure: a long, fluid base layer topped with a short, structured jacket. The burgundy satin skirt and black sweater create a rich, dark column, beautifully contrasted by the cream tweed jacket's texture and lighter tone. The mix of satin, knit, and tweed adds sophisticated textural interest suitable for an event.
  - How to wear: Tuck the black sweater neatly into the burgundy satin skirt to create a seamless, elongated silhouette. / Wear the tweed jacket open to showcase the column created by the skirt and sweater.
  - Declared deviations: Replaced the single slip dress with a skirt and sweater combination.; Substituted the edgy black leather jacket with a more refined cream tweed jacket.; Shifted the color palette from emerald/black to burgundy/black/cream.
  - Gaps: Black strappy heeled sandals (essential); Gold hoop earrings (optional)

### real-camel-work

_Camel blazer + tee + straight trousers + loafers for work, from the real wardrobe (no blazer, no tee, no loafers): expect honest gaps or declared deviations._

**single_pass** — human rating: ___/5
- **Smart-Casual Foundation** (closest) — 3/5 inspiration pieces from your closet · 1 wardrobe gap
  - Pieces: Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - Coherence: This look maintains a largely neutral palette of black and white, creating a cohesive, modern smart-casual outfit. The relaxed fit of the sweater and wide-leg jeans create a comfortable yet stylish silhouette, grounded by the platform sneakers.
  - How to wear: Wear the black crewneck sweater untucked or with a slight front-tuck to maintain a relaxed feel. / Allow the wide-leg jeans to fall over the platform sneakers for an elongated leg line.
  - Declared deviations: The blazer is omitted due to lack of a suitable match, shifting the overall formality slightly more casual.; The bottom changes from tailored trousers to wide-leg jeans, and shoes from loafers to sneakers, for a more relaxed aesthetic.
  - Gaps: Camel oversized single-breasted blazer (essential); Tan structured tote bag (optional)
- **Workday Chic with a Skirt** (creative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Cream embellished tweed jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Burgundy satin midi skirt → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - Coherence: This look blends textures and colours for a sophisticated yet comfortable aesthetic. The cream and black provide a neutral foundation, while the burgundy skirt adds a rich pop of colour. The mix of structured tweed, fluid satin, and casual sneakers creates a dynamic smart-casual ensemble.
  - How to wear: Wear the cream tweed jacket open over the black sweater. / Ensure the midi skirt falls gracefully, allowing for movement. / Consider a half-tuck of the sweater into the skirt if desired for waist definition.
  - Declared deviations: The blazer is replaced by a cropped tweed jacket, altering the silhouette and layering from oversized to more fitted.; The bottom changes from trousers to a satin midi skirt, introducing a different texture and silhouette.; The shoes are sneakers instead of loafers, adding a casual, modern twist.
  - Gaps: Tan structured tote bag (optional)
- **Monochromatic Comfort** (alternative) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - Coherence: This look embraces a monochromatic dark base with a warm, earthy outer layer. The relaxed fits of the suede jacket, sweater, and wide-leg jeans create a comfortable, contemporary silhouette. The platform sneakers add a touch of modern street style while maintaining a cohesive colour story.
  - How to wear: Wear the rust suede jacket open over the black sweater for a relaxed, layered look. / Allow the wide-leg jeans to drape naturally over the platform sneakers. / Consider a half-tuck of the sweater if you want to subtly define the waist.
  - Declared deviations: The blazer is replaced by a casual suede jacket, shifting the overall formality from smart-casual to more casual.; The bottom changes from tailored trousers to wide-leg jeans, emphasizing comfort and a relaxed silhouette.; The shoes are sneakers instead of loafers, further enhancing the casual, modern vibe.
  - Gaps: Tan structured tote bag (optional)

**agentic** — human rating: ___/5
- **Suede & Wide-Leg Refined** (closest) — 4/5 inspiration pieces recreated from your closet · No purchase needed — the gaps are optional
  - Pieces: Rust suede-like jacket → Camel oversized single-breasted blazer, Black crewneck sweater → White crew-neck t-shirt, Black high-rise wide-leg jeans → Black straight-leg trousers, White and black platform sneakers → Brown leather penny loafers
  - Coherence: This outfit achieves a cohesive smart-casual aesthetic by balancing the relaxed rust suede jacket with the clean black sweater and wide-leg jeans. The textures — soft suede, matte knit, and structured denim — work together, while the black and rust palette provides a warm, modern feel. The platform sneakers complete the look with a contemporary, polished touch.
  - How to wear: Wear the rust suede jacket open to maintain the relaxed top layer and create a continuous vertical line. / Ensure the black sweater is neatly tucked or styled to complement the high-rise jeans, balancing the proportions. / Allow the wide-leg jeans to skim over the platform sneakers for an elongated, streamlined leg line.
  - Declared deviations: The top layer is a relaxed suede jacket instead of a tailored blazer, shifting the formality slightly more casual.; The bottom is wide-leg denim instead of straight-leg suiting trousers, altering the material and silhouette.; The footwear is modern platform sneakers instead of classic loafers, changing the overall footwear style.
  - Gaps: Tan structured tote bag (optional)
  - Critic: approved after 1 revision(s); notes: The inspiration's core aesthetic is 'tailored' and 'polished smart-casual'. Replacing a tailored blazer with a casual suede jacket and tailored trousers with denim jeans fundamentally shifts the formality and aesthetic away from the inspiration's 'smart-casual tailoring' to a more casual, streetwear-influenced look.; The inspiration features an oversized, hip-length blazer providing volume up top, balanced by a straight, slim trouser. This look pairs a shorter, more cropped suede jacket with wide-leg jeans. This alters the intended volume balance and silhouette, making the top appear shorter and wider relative to the very wide bottom, rather than an elongated, skimming top layer.; The combination of a casual suede jacket, a basic knit sweater, wide-leg denim jeans, and chunky platform sneakers creates a very casual ensemble. This clashes with the inspiration's 'polished' and 'tailored' smart-casual aesthetic, making the overall outfit less cohesive in its formality.
- Workflow: Stylist proposed 3 look(s); 3 passed validation → Critic approved 0 of 3; sending feedback to the stylist → Stylist proposed 2 look(s); 1 passed validation, 1 removed (invalid or duplicate) → Critic approved 1 of 1

### real-satin-material-challenge

_Material challenge: satin slip skirt dressed down with a slouchy sweatshirt and sneakers. The burgundy satin skirt fits; the stylist must keep the dressed-down mood._

**single_pass** — human rating: ___/5
- **Modern High-Low Neutrals** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - Coherence: This look maintains the inspiration's core high-low contrast by pairing a relaxed, casual sweater with a sleek satin midi skirt and chunky sneakers. The palette shifts to deeper neutrals (black and burgundy) but remains soft, complementing the modern aesthetic.
  - How to wear: Front-tuck the black sweater to define the waist and emphasize the skirt's silhouette, just like in the inspiration. / Wear the burgundy satin skirt at your natural waist for optimal proportion with the tucked sweater.

**agentic** — human rating: ___/5
- **Modern Casual Contrast** (closest) — 3/3 pieces already in your closet · No new purchase needed
  - Pieces: Black crewneck sweater → Oversized heather grey crewneck sweatshirt, Burgundy satin midi skirt → Champagne satin slip midi skirt, White and black platform sneakers → Chunky white sneakers
  - Coherence: This outfit achieves a compelling high-low contrast by pairing a soft, relaxed knit sweater with a luxurious satin midi skirt. The proportions are balanced with volume on top and a fluid line below, enhanced by tucking the sweater. The chunky sneakers maintain the casual, off-duty aesthetic, while the burgundy skirt adds a richer, deeper tone to the otherwise neutral palette, creating a more intentional color story.
  - How to wear: Half-tuck the front of the sweater to define your waist and show off the skirt's waistband. / Allow the skirt to skim your body, appreciating its fluid movement as you walk. / Wear the sneakers to keep the look grounded and casually cool.
  - Declared deviations: The top is a black knit sweater instead of a heather grey fleece sweatshirt, changing the color palette and texture but retaining the relaxed volume.; The skirt is burgundy satin with an A-line cut instead of champagne bias-cut satin, introducing a richer color and slightly more volume.; The sneakers are white and black platform style, adding a graphic element compared to plain white.
  - Critic: approved after 0 revision(s); notes: The black knit sweater, while relaxed, lacks the distinct 'oversized' volume and sporty fleece texture of the inspiration's sweatshirt, making the 'sporty' aspect of the high-low contrast slightly less pronounced.; The burgundy satin skirt appears to be a straight A-line cut rather than a bias-cut slip skirt, which might slightly reduce the fluid, body-skimming drape of the inspiration, though it still reads as a sleek midi.
- Workflow: Stylist proposed 1 look(s); 1 passed validation → Critic approved 1 of 1

### real-no-good-outfit

_No good outfit exists: black-tie tuxedo look from a casual 7-piece wardrobe. A good system admits the gap instead of forcing a match._

**single_pass** — human rating: ___/5
- No looks: The inspiration is a strict black-tie ensemble, requiring specific formal garments (tuxedo jacket, dress shirt, tuxedo trousers, patent oxfords) in black and white. Your wardrobe currently contains only casual or smart-casual items, and no garments that align with the required formality, specific garment types, or color palette for a black-tie event. Given the 'close' fidelity preference, it is not possible to create a reasonable outfit that matches the inspiration's strict formal requirements.

**agentic** — human rating: ___/5
- No looks: The inspiration is for a 'strict black tie' event, requiring formal black tailoring, a crisp white shirt, and formal shoes. Your current wardrobe does not contain any garments that meet the 'strict formality' essential trait, nor the specific items like a tuxedo jacket, dress shirt, or formal shoes. The available pieces are all smart casual or casual, making it impossible to create a coherent and occasion-appropriate outfit that preserves the inspiration's core essence.
- Workflow: Stylist proposed 0 look(s); 0 passed validation
