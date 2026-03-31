#!/usr/bin/env bash
set -euo pipefail

# scripts/deploy_hf_slim.sh
# Usage: ./scripts/deploy_hf_slim.sh <HF_USER> <SPACE_NAME> [branch] [wheelhouse|--fetch-wheelhouse <url>]
# This script copies Dockerfile.slim -> Dockerfile and invokes deploy_to_hf.sh with 'slim' and optional wheelhouse flags.

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <HF_USER> <SPACE_NAME> [branch] [wheelhouse|--fetch-wheelhouse <url>]"
  exit 2
fi

HF_USER="$1"
SPACE_NAME="$2"
BRANCH="${3:-main}"

# Copy slim Dockerfile to Dockerfile so HF builds using the slim image
if [ -f Dockerfile.slim ]; then
  cp Dockerfile.slim Dockerfile
  echo "Copied Dockerfile.slim -> Dockerfile"
else
  echo "Dockerfile.slim not found in repo root. Aborting."
  exit 1
fi

# Shift first two args and pass remaining to deploy_to_hf.sh
shift 2

# Ensure deploy helper exists
if [ ! -x ./scripts/deploy_to_hf.sh ]; then
  chmod +x ./scripts/deploy_to_hf.sh || true
fi

./scripts/deploy_to_hf.sh "$HF_USER" "$SPACE_NAME" "$BRANCH" slim "$@"

