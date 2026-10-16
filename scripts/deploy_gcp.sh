#!/usr/bin/env bash
# Deploy Rewear to Google Cloud Run (API + web), with Vertex AI, Firestore and Cloud Storage.
#
# Usage:  PROJECT_ID=my-project ./scripts/deploy_gcp.sh
# Optional: REGION (default us-central1), API_SERVICE, WEB_SERVICE, BUCKET, GEMINI_MODEL,
#           PRIVATE_API=1 (API only reachable by the web service's identity).
#
# Requires: gcloud CLI logged in (`gcloud auth login`) with permission to enable services,
# create service accounts, buckets, Firestore and Cloud Run services; billing enabled on PROJECT_ID.
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
API_SERVICE="${API_SERVICE:-rewear-api}"
WEB_SERVICE="${WEB_SERVICE:-rewear-web}"
BUCKET="${BUCKET:-${PROJECT_ID}-rewear-media}"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
# A dedicated named database keeps Rewear data separate from other apps in the same project.
FIRESTORE_DB="${FIRESTORE_DB:-rewear}"
API_SA="rewear-api@${PROJECT_ID}.iam.gserviceaccount.com"
WEB_SA="rewear-web@${PROJECT_ID}.iam.gserviceaccount.com"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

gc() { gcloud --project "$PROJECT_ID" --quiet "$@"; }
# IAM is eventually consistent: freshly created service accounts can take a minute to be bindable.
retry() { for i in 1 2 3 4 5 6; do "$@" && return 0; echo "   retrying in 15s…"; sleep 15; done; return 1; }

echo "==> Checking billing"
BILLING="$(gcloud billing projects describe "$PROJECT_ID" --format='value(billingEnabled)' 2>/dev/null || true)"
if [[ "$BILLING" == "False" ]]; then
  echo "Billing is not enabled on $PROJECT_ID. Link a billing account first:" >&2
  echo "  gcloud billing projects link $PROJECT_ID --billing-account=XXXXXX-XXXXXX-XXXXXX" >&2
  exit 1
fi

echo "==> Enabling APIs"
gc services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  aiplatform.googleapis.com firestore.googleapis.com storage.googleapis.com iam.googleapis.com

echo "==> Service accounts (least privilege)"
gc iam service-accounts describe "$API_SA" >/dev/null 2>&1 || gc iam service-accounts create rewear-api --display-name "Rewear API"
gc iam service-accounts describe "$WEB_SA" >/dev/null 2>&1 || gc iam service-accounts create rewear-web --display-name "Rewear web"
retry gc projects add-iam-policy-binding "$PROJECT_ID" --member "serviceAccount:$API_SA" \
  --role roles/aiplatform.user --condition=None >/dev/null
# Firestore access limited to Rewear's own database.
retry gc projects add-iam-policy-binding "$PROJECT_ID" --member "serviceAccount:$API_SA" --role roles/datastore.user \
  --condition="expression=resource.name.startsWith('projects/${PROJECT_ID}/databases/${FIRESTORE_DB}'),title=rewear-db-only" >/dev/null

echo "==> Firestore database '$FIRESTORE_DB' (native mode)"
gc firestore databases describe --database="$FIRESTORE_DB" >/dev/null 2>&1 || \
  gc firestore databases create --database="$FIRESTORE_DB" --location="$REGION" --type=firestore-native

echo "==> Cloud Storage bucket for images (private)"
gcloud storage buckets describe "gs://$BUCKET" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud storage buckets create "gs://$BUCKET" --project "$PROJECT_ID" --location "$REGION" \
    --uniform-bucket-level-access --public-access-prevention
retry gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" --project "$PROJECT_ID" \
  --member "serviceAccount:$API_SA" --role roles/storage.objectAdmin >/dev/null

API_AUTH_FLAG="--allow-unauthenticated"
[[ "${PRIVATE_API:-0}" == "1" ]] && API_AUTH_FLAG="--no-allow-unauthenticated"

echo "==> Deploying API ($API_SERVICE)"
gc run deploy "$API_SERVICE" --source "$ROOT/backend" --region "$REGION" \
  --service-account "$API_SA" $API_AUTH_FLAG \
  --memory 1Gi --cpu 1 --timeout 300 --concurrency 20 --min-instances 0 --max-instances 5 \
  --set-env-vars "AI_BACKEND=vertex,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=global,GEMINI_MODEL=$GEMINI_MODEL,STORAGE_BACKEND=gcp,GCS_BUCKET=$BUCKET,FIRESTORE_DATABASE=$FIRESTORE_DB,FASHION_KNOWLEDGE_BACKEND=local,COMPOSER_FALLBACK=rules"
API_URL="$(gc run services describe "$API_SERVICE" --region "$REGION" --format='value(status.url)')"

if [[ "${PRIVATE_API:-0}" == "1" ]]; then
  retry gc run services add-iam-policy-binding "$API_SERVICE" --region "$REGION" \
    --member "serviceAccount:$WEB_SA" --role roles/run.invoker >/dev/null
  WEB_ENV="API_URL=$API_URL,API_AUDIENCE=$API_URL"
else
  WEB_ENV="API_URL=$API_URL"
fi

echo "==> Deploying web ($WEB_SERVICE)"
gc run deploy "$WEB_SERVICE" --source "$ROOT/frontend" --region "$REGION" \
  --service-account "$WEB_SA" --allow-unauthenticated \
  --memory 512Mi --cpu 1 --timeout 300 --min-instances 0 --max-instances 5 \
  --set-env-vars "$WEB_ENV"
WEB_URL="$(gc run services describe "$WEB_SERVICE" --region "$REGION" --format='value(status.url)')"

echo "==> Restricting API CORS to the web origin"
gc run services update "$API_SERVICE" --region "$REGION" --update-env-vars "CORS_ORIGINS=$WEB_URL" >/dev/null

echo
echo "API: $API_URL"
echo "Web: $WEB_URL"
echo "Smoke test: ./scripts/smoke_test.sh $WEB_URL"
