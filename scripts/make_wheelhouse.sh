#!/usr/bin/env bash
set -euo pipefail

# scripts/make_wheelhouse.sh
# Build a wheelhouse (prebuilt wheels) for the packages in requirements.txt using
# the manylinux Docker images. This produces portable manylinux wheels suitable
# for most Linux hosts (x86_64 manylinux2014_x86_64 by default).
#
# Usage:
#   ./scripts/make_wheelhouse.sh [--python CPXY] [--manylinux IMAGE]
# Examples:
#   ./scripts/make_wheelhouse.sh
#   ./scripts/make_wheelhouse.sh --python cp311-cp311 --manylinux quay.io/pypa/manylinux2014_x86_64
#
# Requirements:
# - Docker installed locally
# - requirements.txt present at project root

REPO_ROOT="$(pwd)"
WHEEL_DIR="$REPO_ROOT/wheelhouse"
PY_TAG="cp311-cp311"
MANYLINUX_IMAGE="quay.io/pypa/manylinux2014_x86_64"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --python)
      PY_TAG="$2"
      shift 2
      ;;
    --manylinux)
      MANYLINUX_IMAGE="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--python cp311-cp311] [--manylinux quay.io/pypa/manylinux2014_x86_64]"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      exit 1
      ;;
  esac
done

if [ ! -f "requirements.txt" ]; then
  echo "requirements.txt not found in project root: $REPO_ROOT"
  exit 1
fi

mkdir -p "$WHEEL_DIR"

echo "Building wheelhouse in $WHEEL_DIR using image $MANYLINUX_IMAGE and python tag $PY_TAG"

docker run --rm -v "$REPO_ROOT":/io "$MANYLINUX_IMAGE" /bin/bash -lc \
  "/opt/python/${PY_TAG}/bin/pip wheel -r /io/requirements.txt -w /io/wheelhouse --no-deps"

echo "Wheelhouse build finished. Wheels available in: $WHEEL_DIR"
ls -la "$WHEEL_DIR" || true

# Helpful hint for downstream deploy
cat <<EOF
Next steps:
  - Inspect wheelhouse/ to confirm all required wheels were built.
  - If some packages failed, consider pinning versions or building wheels for additional python tags.
  - Deploy to Hugging Face Space including wheelhouse using:
      ./scripts/deploy_to_hf.sh <HF_USER> <SPACE_NAME> main slim wheelhouse
EOF

