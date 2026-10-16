# Rewear — restyle what you already own

**Team Kyberium · AI Builder Cup 2026**

Rewear is a multimodal styling studio built on Gemini (Vertex AI). You digitise your wardrobe, drop in an outfit you love (a Pinterest screenshot, say), and Rewear rebuilds that look from **clothes you actually own**. It explains each substitution and flags any real gaps honestly. **Reuse first, your choice always.**

- **My Closet:** upload a garment photo. Gemini extracts its category, colours, cut, pattern, formality, layering role and occasions, and you review the result before saving. You can also load the 20-piece sample wardrobe.
- **Style Studio:** upload an inspiration photo (or pick a sample) and set occasion, closeness to the photo, and shopping preference. Rewear then returns up to three distinct looks on a styling board, shown beside the original.
- **Styling board:** each look shows which owned piece stands in for which inspiration piece, what each substitution preserves and what it changes, the wardrobe gaps (essential or optional), and an impact line such as "4/4 pieces already in your closet · No new purchase needed". You can swap any piece for another owned garment, refine in plain words ("keep the blazer, but change the trousers") or save the look.

## Architecture

```
Browser ──► Next.js (Cloud Run) ──/api proxy──► FastAPI (Cloud Run) ──► Gemini on Vertex AI
                                                     │                  Firestore (metadata)
                                                     │                  Cloud Storage (images)
                                                     └─► FashionKnowledgeRetriever (none | local | vector)
```

The pipeline is one orchestrated flow (`backend/app/pipeline/orchestrator.py`), not a swarm of agents:

1. **Garment understanding:** a photo goes to Gemini, which returns a validated `GarmentDraft`. Results are cached by image hash, prompt version and model. The user confirms or edits the tags.
2. **Inspiration understanding:** Gemini splits the outfit into slots (`outerwear-1`, `top-1`…) and describes proportions, layering, palette, formality and occasions. Hidden pieces are flagged rather than invented.
3. **Optional knowledge retrieval:** styling principles for the brief. This step is best-effort and can never block the pipeline or add garments.
4. **Wardrobe retrieval (deterministic):** candidates are filtered by category role, occasion suitability and user exclusions. They're then ranked on colour family, silhouette, garment type, formality and style tags, with weights set by the fidelity preference. Scores are ranking signals, not probabilities.
5. **Outfit composition:** Gemini reasons about whole outfits (closest, creative, alternative) using only shortlisted owned IDs.
6. **Validation and gap assessment:** unknown or unowned IDs, duplicates, category clashes, exclusions and occasion breaches are all removed. Every inspiration slot ends up covered or listed as a gap. Impact numbers are computed on the server.
7. **Refinement:** swaps and free-text requests become structured constraints (`keep_garment_ids`, `exclude_garment_ids`, occasion, fidelity), and the same grounded pipeline runs again.

**Reliability.** Calls have timeouts, a limited number of retries with backoff on 429/5xx, and one repair attempt when the model returns malformed JSON. The browser keeps its state when a request fails. If Gemini is unavailable, Rewear falls back to a deterministic matcher that is **clearly labelled** as such (`engine: "rules"`) and is never passed off as AI output. Without credentials the app runs in **demo mode**: sample inspirations carry reviewed, cached analyses, and the UI shows a "Demo mode" badge.

**Security.** All credentials stay on the server. The browser only talks to the same-origin `/api` proxy, which reads `API_URL` at runtime. Each visitor gets an anonymous bearer token, and their owner ID is a hash of it, so every query is owner-scoped and client-supplied IDs never grant access. Uploads are checked by decoding, capped at 8 MB, re-encoded and EXIF-stripped (which removes GPS data). Storage keys are allow-listed by regex, AI routes are rate-limited per owner, and the containers run as non-root users.

**Honesty rules.**
- No invented owned garments, products, stock, certifications or CO₂/water figures.
- Sample garments are labelled "sample illustration".
- Shopping ideas appear only when the shopping preference allows them, and are labelled "search idea — not a product recommendation".

## Repository layout

```
backend/   FastAPI app (app/), tests/, evals/ (14 labelled cases), scripts/render_assets.py
frontend/  Next.js 16 app (src/app, src/components, src/lib/{api,types,store}.ts)
scripts/   deploy_gcp.sh (Cloud Run + Vertex AI + Firestore + GCS), smoke_test.sh
docs/      PRD, UX handoff, KNOWLEDGE_RETRIEVAL.md (integration guide for the vector index)
```

## Run locally

Prerequisites: Python 3.12 with [uv](https://docs.astral.sh/uv/), Node 22 and pnpm.

```bash
# API
cd backend
cp .env.example .env            # set GOOGLE_CLOUD_PROJECT, or AI_BACKEND=off for demo mode
gcloud auth application-default login   # only for live Gemini
uv sync && uv run uvicorn app.main:app --reload --port 8000

# Web (new terminal)
cd frontend
pnpm install
API_URL=http://localhost:8000 pnpm dev   # http://localhost:3000
```

In the app: open **My Closet**, choose **Load sample wardrobe**, then go to **Style Studio**, pick a sample (or upload a photo) and choose **Find my outfits**.

### Environment variables

| Variable | Where | Default | Purpose |
|---|---|---|---|
| `AI_BACKEND` | API | `vertex` | `vertex` for Gemini via ADC, `off` for labelled demo mode |
| `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` | API | — / `global` | Vertex AI project and location |
| `GEMINI_MODEL` / `GEMINI_COMPOSER_MODEL` | API | `gemini-2.5-flash` / same | Models for tagging/analysis and composition |
| `GEMINI_TIMEOUT_S`, `GEMINI_MAX_RETRIES` | API | `45`, `2` | Reliability bounds |
| `COMPOSER_FALLBACK` | API | `rules` | `rules` uses the labelled fallback; `none` returns a retryable 503 |
| `STORAGE_BACKEND` | API | `local` | `local` (JSON and files in `LOCAL_DATA_DIR`) or `gcp` (Firestore and `GCS_BUCKET`) |
| `FASHION_KNOWLEDGE_BACKEND` | API | `local` | `none`, `local` or `vector` (see `docs/KNOWLEDGE_RETRIEVAL.md`) |
| `CORS_ORIGINS` | API | `http://localhost:3000` | Only needed if browsers call the API directly |
| `API_URL` | Web (runtime) | `http://localhost:8000` | Where the `/api` proxy forwards requests |
| `API_AUDIENCE` | Web (runtime) | — | Set when the API is private Cloud Run; the proxy then sends an ID token |

## Tests and evaluation

```bash
cd backend
uv run pytest -q                       # 55 tests: matching, validation, AI client, knowledge seam, API security, evals
uv run python -m evals.run_evals       # offline eval → evals/results/latest.md
uv run python -m evals.run_evals --live   # Gemini composer (needs credentials) → latest-live.md
cd ../frontend && pnpm lint && pnpm build
./scripts/smoke_test.sh http://localhost:3000   # end-to-end via the web proxy (needs jq)
```

The 14 eval cases cover:
- exact matches
- same silhouette in a different colour
- aesthetic substitutes
- category substitutes (a two-piece for a dress)
- distinct closest and creative looks
- optional and essential gaps
- formal occasion constraints
- shopping switched off
- keep and exclude preferences
- a photo with no outfit
- hallucinated garment IDs
- malformed model output
- an empty wardrobe

## Deploy to Google Cloud

```bash
gcloud auth login
PROJECT_ID=your-billed-project ./scripts/deploy_gcp.sh            # add PRIVATE_API=1 to make the API IAM-only
./scripts/smoke_test.sh https://rewear-web-xxxx.run.app
```

The script:
- enables the Cloud Run, Cloud Build, Artifact Registry, Vertex AI, Firestore, Storage and IAM APIs
- creates least-privilege service accounts (the API gets `aiplatform.user`, `datastore.user` and object admin on its own private bucket only)
- creates a native-mode Firestore database and a private bucket
- deploys both services from source and restricts the API's CORS to the web origin

**Requirements:** billing must be enabled on the project, and the deploying user needs Owner (or Editor plus IAM Admin) on it.

## Regenerating sample art

`uv run python scripts/render_assets.py` (in `backend/`) rewrites the garment SVGs and rasterises the inspiration boards using headless Chrome. All sample art is original and authored for this project.
