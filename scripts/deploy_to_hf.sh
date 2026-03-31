#!/usr/bin/env bash
set -euo pipefail

# scripts/deploy_to_hf.sh
# Usage:
#   ./scripts/deploy_to_hf.sh <HF_USERNAME> <SPACE_NAME> [branch] [slim] [wheelhouse]
# Example:
#   ./scripts/deploy_to_hf.sh plussunilsingh StockPricePrediction main slim wheelhouse
#
# The script will:
# - clone the empty Space repo from Hugging Face
# - copy the minimal set of files required to run the Docker Space
# - optionally use Dockerfile.slim (if 'slim' arg provided)
# - optionally include a 'wheelhouse' directory and modify the Dockerfile to install from it
# - commit and push to the Space repo
#
# Notes:
# - When prompted for credentials, use your Hugging Face access token as the password.
# - The script does not push data/, logs/, models/ to the Space to keep the repo small.

REPO_ROOT="$(pwd)"

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <HF_USERNAME> <SPACE_NAME> [branch] [slim|--slim] [wheelhouse|--wheelhouse]"
  exit 2
fi

HF_USER="$1"
SPACE_NAME="$2"
BRANCH="${3:-main}"

# Detect optional flags
USE_SLIM=0
USE_WHEELHOUSE=0
FETCH_WHEELHOUSE_URL=""
for a in "$@"; do
  if [ "$a" = "slim" ] || [ "$a" = "--slim" ]; then
    USE_SLIM=1
  fi
  if [ "$a" = "wheelhouse" ] || [ "$a" = "--wheelhouse" ]; then
    USE_WHEELHOUSE=1
  fi
  if [ "$a" = "--fetch-wheelhouse" ]; then
    FETCH_WHEELHOUSE_URL="$2"
    # skip next arg as it's the url
    shift || true
  fi
done

SPACE_REPO_URL="https://huggingface.co/spaces/${HF_USER}/${SPACE_NAME}"
TMP_DIR=$(mktemp -d)

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "Cloning Space repo: ${SPACE_REPO_URL} into ${TMP_DIR}"

# Clone the space repo (this may prompt for username/password -> use token)
if ! git clone "$SPACE_REPO_URL" "$TMP_DIR"; then
  echo "Failed to clone ${SPACE_REPO_URL}. Ensure the Space exists and you have permission."
  exit 1
fi

# Copy required files
echo "Copying project files into the space repo (excluding heavy folders)..."
rsync -av --exclude '.git' \
    --exclude 'data' --exclude 'models' --exclude 'logs' --exclude '__pycache__' \
    --exclude '.venv' --exclude 'venv' --exclude 'tests' \
    ./ "$TMP_DIR/"

# If user requested the slim Dockerfile and it exists in the repo, copy it over as Dockerfile
if [ "$USE_SLIM" -eq 1 ]; then
  if [ -f "$REPO_ROOT/Dockerfile.slim" ]; then
    echo "Using Dockerfile.slim -> copying to Space repo as Dockerfile"
    cp "$REPO_ROOT/Dockerfile.slim" "$TMP_DIR/Dockerfile"
  else
    echo "Warning: Dockerfile.slim was requested but does not exist in the project root. Continuing without it."
  fi
fi

# If user requested wheelhouse and it exists, copy it and adjust Dockerfile to use it
# Also support fetch-wheelhouse URL which is downloaded into TMP_DIR/wheelhouse
if [ "$USE_WHEELHOUSE" -eq 1 ] || [ -n "$FETCH_WHEELHOUSE_URL" ]; then
  if [ -n "$FETCH_WHEELHOUSE_URL" ]; then
    echo "Fetching wheelhouse from: $FETCH_WHEELHOUSE_URL"
    # download to tmp location
    if curl -fSL "$FETCH_WHEELHOUSE_URL" -o "$TMP_DIR/wheelhouse.tar.gz"; then
      mkdir -p "$TMP_DIR/wheelhouse"
      tar xzf "$TMP_DIR/wheelhouse.tar.gz" -C "$TMP_DIR" || true
      echo "Extracted wheelhouse into $TMP_DIR/wheelhouse"
    else
      echo "Failed to download wheelhouse from $FETCH_WHEELHOUSE_URL"
    fi
  fi

  # If local wheelhouse exists in project and user requested wheelhouse, copy it
  WHEEL_SRC="$REPO_ROOT/wheelhouse"
  if [ -d "$WHEEL_SRC" ] && [ "$USE_WHEELHOUSE" -eq 1 ]; then
    echo "Copying wheelhouse into Space repo (this may increase repo size)..."
    cp -R "$WHEEL_SRC" "$TMP_DIR/wheelhouse"
  fi

  if [ -d "$TMP_DIR/wheelhouse" ]; then
    # If there's a Dockerfile in the tmp dir, rewrite its pip install command to use the local wheelhouse
    if [ -f "$TMP_DIR/Dockerfile" ]; then
      echo "Patching Dockerfile in Space repo to install from local wheelhouse..."
      sed -i.bak -E "s#pip install --no-cache-dir --prefer-binary -r /app/requirements.txt#pip install --no-cache-dir --no-index --find-links /app/wheelhouse -r /app/requirements.txt#g" "$TMP_DIR/Dockerfile" || true
      sed -i.bak -E "s#pip install --no-cache-dir -r /app/requirements.txt#pip install --no-cache-dir --no-index --find-links /app/wheelhouse -r /app/requirements.txt#g" "$TMP_DIR/Dockerfile" || true
      rm -f "$TMP_DIR/Dockerfile.bak" || true
    else
      echo "No Dockerfile found in the Space repo to patch; wheelhouse copied but Dockerfile must be edited manually to use it."
    fi
  else
    echo "Warning: wheelhouse requested or fetched but no wheelhouse directory present in temp repo; skipping patch."
  fi
fi

cd "$TMP_DIR"

# Ensure git user.name/email are set (some CI/containers don't have global config)
if ! git config user.name >/dev/null; then
  git config user.name "hf-deploy-bot"
fi
if ! git config user.email >/dev/null; then
  git config user.email "hf-deploy@example.com"
fi

# Show copied files for debug
echo "Files in space repo after copy:"
ls -la | sed -n '1,200p'

# Commit and push
git add -A

# Detect changes (staged or unstaged)
if [ -z "$(git status --porcelain)" ]; then
  echo "No changes detected in the Space repo. Nothing to push."
  exit 0
fi

# Create commit (allow empty commit to succeed silently)
if ! git commit -m "Deploy app: Docker-based Hugging Face Space"; then
  echo "Warning: git commit returned non-zero (possibly no changes to commit)."
fi

echo "Pushing to ${SPACE_REPO_URL} (branch: ${BRANCH})"
# When prompted for username/password, use your Hugging Face username and an access token as password
if ! git push origin HEAD:${BRANCH}; then
  echo "git push failed. Ensure you provided a valid access token as the password and you have write access to the Space."
  exit 1
fi

echo "Done. Visit https://huggingface.co/spaces/${HF_USER}/${SPACE_NAME} to watch the build logs."
