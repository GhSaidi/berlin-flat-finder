#!/usr/bin/env bash
# Apply every SQL migration in sql/ in order. Files are idempotent, so re-running is safe.
set -euo pipefail
cd "$(dirname "$0")/.."

for f in sql/*.sql; do
  echo "Applying $f"
  docker compose exec -T db psql -v ON_ERROR_STOP=1 -U postgres -d flats < "$f"
done
echo "Migrations done."
