#!/usr/bin/env bash
# Fetch the fine-tuned Laya (SOIC topic tags) from the PRIVATE soic-ladder release and install it ONCE. Verifies the sha256.
# usage: fetch_laya_model.sh [DEST_DIR=./models]      needs gh logged in with access to syedamber91/soic-ladder (in a soic-ladder
# workflow: env GH_TOKEN: ${{ github.token }}). Refuses to create a second copy. The model is derived from paid-course notes: keep it private.
set -euo pipefail
TAG=laya-soic-tags-2026-10-03; REPO=syedamber91/soic-ladder; DEST="${1:-./models}"; TAR=laya-soic-tags-vps-2026-10-03.tar
[ -e "$DEST/laya" ] && { echo "refusing: $DEST/laya already exists (keep ONE copy)"; exit 1; }
mkdir -p "$DEST"; tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
gh release download "$TAG" -R "$REPO" -p "$TAR" -p SHA256SUMS -D "$tmp"
( cd "$tmp" && grep " $TAR\$" SHA256SUMS > one.sum && { sha256sum -c one.sum 2>/dev/null || shasum -a 256 -c one.sum; } )
tar -xf "$tmp/$TAR" -C "$DEST" && echo "installed: $DEST/laya   (pip install laya==0.3.23 ; Agent('$DEST/laya', device='cpu'))"
