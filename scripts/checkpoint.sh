#!/usr/bin/env bash
# Save a database snapshot for a finished, working task.
# Usage: scripts/checkpoint.sh m1    (then m2a, m2b, m3a, m3b)
# Only writes snapshots/<tag>.sql. Staging, committing, tagging and pushing are done
# by hand; the script prints the suggested git commands at the end.
set -euo pipefail
cd "$(dirname "$0")/.."

TAG="${1:?Usage: scripts/checkpoint.sh <tag>}"

mkdir -p snapshots
docker compose exec -T db pg_dump -U postgres -d flats > "snapshots/$TAG.sql"
echo "Database snapshot saved: snapshots/$TAG.sql"
echo
echo "Next, by hand (review 'git status' and 'git diff' first):"
echo "  git add <changed files> snapshots/$TAG.sql"
echo "  git commit -m \"<message>\""
echo "  git switch main && git merge --ff-only dev && git tag $TAG"
echo "  git push origin main --tags && git switch dev"
