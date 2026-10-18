#!/usr/bin/env bash
# Repeatable end-to-end smoke test against a running Rewear web deployment (goes through the
# same /api proxy the browser uses): health -> session -> sample wardrobe -> sample
# inspiration -> generate -> swap -> save -> cleanup.
# Optional live check: IMAGE=path/to/outfit.jpg also uploads a real inspiration photo (needs Gemini).
#
# Usage: ./scripts/smoke_test.sh https://rewear-web-xxxx.run.app   (default http://localhost:3000)
set -euo pipefail
BASE="${1:-http://localhost:3000}/api"
command -v jq >/dev/null || { echo "jq is required" >&2; exit 2; }

step() { printf '\n==> %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

step "health"
HEALTH=$(curl -fsS "$BASE/health") || fail "health endpoint unreachable"
echo "$HEALTH" | jq -c .
AI=$(echo "$HEALTH" | jq -r .ai_enabled)

step "session"
TOKEN=$(curl -fsS -X POST "$BASE/session" | jq -r .token)
[[ "$TOKEN" == rw_* ]] || fail "no session token"
AUTH=(-H "Authorization: Bearer $TOKEN")

step "load sample wardrobe"
ADDED=$(curl -fsS -X POST "${AUTH[@]}" "$BASE/demo/wardrobe" | jq .added)
[[ "$ADDED" -ge 15 ]] || fail "expected >=15 sample garments, got $ADDED"
OWNED=$(curl -fsS "${AUTH[@]}" "$BASE/wardrobe/items" | jq -c '[.[].id]')

step "sample inspiration"
INSP=$(curl -fsS -X POST "${AUTH[@]}" -F sample_id=insp_camel_work "$BASE/inspirations" | jq -r .id)

step "generate looks"
GEN=$(curl -fsS -X POST "${AUTH[@]}" -H 'Content-Type: application/json' \
  -d "{\"inspiration_id\":\"$INSP\",\"preferences\":{\"occasion\":\"work\",\"fidelity\":\"aesthetic\"}}" \
  "$BASE/looks/generate")
echo "$GEN" | jq -c '{engine, engine_note, looks: [.looks[] | {title, headline: .impact.headline}]}'
[[ $(echo "$GEN" | jq '.looks | length') -ge 1 ]] || fail "no looks generated"
BAD=$(echo "$GEN" | jq --argjson owned "$OWNED" '[.looks[].items[].garment_id] - $owned | length')
[[ "$BAD" == 0 ]] || fail "look references garments that are not owned"
GEN_ID=$(echo "$GEN" | jq -r .id)
LOOK_ID=$(echo "$GEN" | jq -r '.looks[0].id')

step "swap shoes"
OLD=$(echo "$GEN" | jq -r '[.looks[0].items[] | select(.garment.category=="shoes")][0].garment_id')
NEW=$(echo "$OWNED" | jq -r --arg old "$OLD" '[.[] | select(. == "s_black_boots" or . == "s_brown_loafers") | select(. != $old)][0]')
curl -fsS -X POST "${AUTH[@]}" -H 'Content-Type: application/json' \
  -d "{\"generation_id\":\"$GEN_ID\",\"look_id\":\"$LOOK_ID\",\"old_garment_id\":\"$OLD\",\"new_garment_id\":\"$NEW\"}" \
  "$BASE/looks/swap" | jq -e --arg new "$NEW" '[.looks[0].items[].garment_id] | index($new) != null' >/dev/null \
  || fail "swap did not apply"

step "save look"
curl -fsS -X POST "${AUTH[@]}" -H 'Content-Type: application/json' \
  -d "{\"generation_id\":\"$GEN_ID\",\"look_id\":\"$LOOK_ID\"}" "$BASE/looks/saved" | jq -c '{id, title: .look.title}'

if [[ -n "${IMAGE:-}" && "$AI" == "true" ]]; then
  step "live inspiration upload ($IMAGE)"
  LIVE=$(curl -fsS -X POST "${AUTH[@]}" -F "file=@$IMAGE" "$BASE/inspirations")
  echo "$LIVE" | jq -c '{engine, pieces: [.analysis.pieces[].description]}'
  LIVE_ID=$(echo "$LIVE" | jq -r .id)
  curl -fsS -X POST "${AUTH[@]}" -H 'Content-Type: application/json' \
    -d "{\"inspiration_id\":\"$LIVE_ID\"}" "$BASE/looks/generate" \
    | jq -c '{engine, looks: [.looks[] | {title, items: [.items[].garment.name]}]}'
fi

step "cleanup"
curl -fsS -X DELETE "${AUTH[@]}" "$BASE/demo/wardrobe" >/dev/null
echo; echo "SMOKE TEST PASSED ($BASE, ai_enabled=$AI)"
