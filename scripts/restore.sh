#!/usr/bin/env bash
# Restore the database from a checkpoint snapshot.
# Usage: scripts/restore.sh m2a
# Restore the code first, by hand, e.g.:
#   git add <files> && git commit -m "chore: Save work before restoring m2a"   (on dev, optional)
#   git switch main && git reset --hard m2a
# This script only replaces the 'flats' database with snapshots/<tag>.sql.
set -euo pipefail
cd "$(dirname "$0")/.."

TAG="${1:?Usage: scripts/restore.sh <tag>}"
SNAPSHOT="snapshots/$TAG.sql"

if [ ! -f "$SNAPSHOT" ]; then
  echo "Snapshot $SNAPSHOT not found." >&2
  exit 1
fi

docker compose exec -T db psql -U postgres -d postgres \
  -c "DROP DATABASE IF EXISTS flats WITH (FORCE);" \
  -c "CREATE DATABASE flats;"
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U postgres -d flats < "$SNAPSHOT"

echo "Database restored to $TAG. Restart Streamlit."
