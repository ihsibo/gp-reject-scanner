#!/usr/bin/env bash
set -euo pipefail

# Robust temporal clone: prefers main if present, else default branch
# Usage:
#   REPO_URL="..." TARGET_DIR="..." ./scripts/clone_repo.sh
##
REPO_URL="${REPO_URL:-}"
TARGET_DIR="${TARGET_DIR:-}"

if [[ -z "$REPO_URL" || -z "$TARGET_DIR" ]]; then
  echo "Error: REPO_URL and TARGET_DIR env vars must be set." >&2
  exit 1
fi

BRANCH_MAIN="${BRANCH_MAIN:-main}"

echo "🔍 Cloning target repository: ${REPO_URL}"
if git ls-remote --heads "$REPO_URL" | grep -q "refs/heads/${BRANCH_MAIN}"; then
  echo "Info: Found ${BRANCH_MAIN} branch. Cloning that branch."
  git clone -b "${BRANCH_MAIN}" --depth 1 "$REPO_URL" "$TARGET_DIR"
else
  echo "Warning: Branch ${BRANCH_MAIN} not found. Cloning default branch instead."
  git clone --depth 1 "$REPO_URL" "$TARGET_DIR"
fi
