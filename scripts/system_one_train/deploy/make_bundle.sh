#!/usr/bin/env bash
# Build output/system_one_train/system-one-vps.tar.gz  (PRIVATE: contains models trained on your SOIC notes; never commit).
#   scripts/system_one_train/deploy/make_bundle.sh [--laya-dir /path/to/fine-tuned-laya]
set -euo pipefail
R="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$R/scripts/system_one_train"; O="$R/output/system_one_train"
PY="$O/.venv/bin/python"; B="$O/bundle/system-one-vps"
LAYA=""; [ "${1:-}" = "--laya-dir" ] && LAYA="$2"
[ -f "$O/tagger_final.joblib" ] || "$PY" "$S/train_minilm.py"
"$PY" "$S/vault_finder.py" build
rm -rf "$O/bundle"; mkdir -p "$B/models"
"$PY" - <<PYE
from sentence_transformers import SentenceTransformer
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2").save("$B/models/minilm")
PYE
cp "$O/tagger_final.joblib" "$O/vault_index.npz" "$O/vault_index.json" "$B/models/"
cp "$S/serve.py" "$S/minilm_core.py" "$S/laya_data.py" "$S/laya_choice_data.py" "$S/common.py" "$S/deploy/install_vps.sh" "$S/deploy/system-one.service" "$B/"
[ -n "$LAYA" ] && cp -R "$LAYA" "$B/models/laya"
"$PY" -m pip freeze | grep -i -E '^(sentence-transformers|scikit-learn|numpy|joblib|transformers|scipy|tokenizers|huggingface-hub|safetensors)==' > "$B/requirements.lock"
printf "built %s\nsklearn/numpy pinned in requirements.lock (joblib pickles need matching sklearn)\nlaya: %s\n" "$(date -u +%FT%TZ)" "${LAYA:-none}" > "$B/BUILD_INFO.txt"
(cd "$B" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 shasum -a 256 > SHA256SUMS)
tar -czf "$O/system-one-vps.tar.gz" -C "$O/bundle" system-one-vps
ls -lh "$O/system-one-vps.tar.gz"; cat "$B/requirements.lock"
