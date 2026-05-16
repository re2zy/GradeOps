#!/usr/bin/env bash
set -euo pipefail

BUCKET_NAME="${GCS_BUCKET_NAME:-gradeops-exams}"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT env var is required}"

echo "Creating GCS bucket: gs://$BUCKET_NAME (project: $PROJECT_ID)"

gsutil mb -p "$PROJECT_ID" -c STANDARD -l US-CENTRAL1 "gs://$BUCKET_NAME" \
  || echo "Bucket already exists — continuing."

# CORS so browsers can fetch signed URLs directly
cat > /tmp/gradeops_cors.json <<'EOF'
[{
  "origin": ["http://localhost:5173", "https://your-domain.com"],
  "method": ["GET", "HEAD", "PUT", "POST"],
  "responseHeader": ["Content-Type", "Authorization"],
  "maxAgeSeconds": 3600
}]
EOF
gsutil cors set /tmp/gradeops_cors.json "gs://$BUCKET_NAME"

# Lifecycle: auto-delete raw PDFs after 90 days to save costs
cat > /tmp/gradeops_lifecycle.json <<'EOF'
{
  "rule": [{
    "action": {"type": "Delete"},
    "condition": {"age": 90, "matchesPrefix": ["exams/"]}
  }]
}
EOF
gsutil lifecycle set /tmp/gradeops_lifecycle.json "gs://$BUCKET_NAME"

# Create top-level folder markers
gsutil -q cp /dev/null "gs://$BUCKET_NAME/exams/.keep"
gsutil -q cp /dev/null "gs://$BUCKET_NAME/crops/.keep"

echo "Done. Bucket structure:"
gsutil ls "gs://$BUCKET_NAME"
