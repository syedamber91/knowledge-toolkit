#!/usr/bin/env bash
# Run ON THE VPS inside the unpacked bundle:  bash install_vps.sh [--service]
# CPU-only. Needs python3 (>=3.10) with venv. Creates ./venv, installs pinned deps, smoke-tests.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3,10), "need python >= 3.10"'
"$PY" -m venv venv
./venv/bin/pip install -q --upgrade pip
if [ "$(uname -m)" = "x86_64" ]; then
  ./venv/bin/pip install -q torch --index-url https://download.pytorch.org/whl/cpu   # CPU wheel (no CUDA download)
else
  ./venv/bin/pip install -q torch
fi
./venv/bin/pip install -q -r requirements.lock
[ -d models/laya ] && ./venv/bin/pip install -q laya || echo "no models/laya -> Laya endpoint off (MiniLM tagger + finder only)"
echo "smoke test..."
(SYSTEM_ONE_PORT=18765 ./venv/bin/python serve.py & echo $! > .pid; \
 for i in $(seq 1 60); do curl -fsS localhost:18765/health >/dev/null 2>&1 && break; sleep 3; done; \
 curl -fsS localhost:18765/health; echo; \
 curl -fsS -X POST localhost:18765/find -d '{"query":"which model for 77 classes","k":3}'; echo; kill "$(cat .pid)"; rm .pid)
if [ "${1:-}" = "--service" ]; then
  sed "s#__DIR__#$(pwd)#g; s#__USER__#$(id -un)#g" system-one.service > /tmp/system-one.service
  sudo mv /tmp/system-one.service /etc/systemd/system/system-one.service
  sudo systemctl daemon-reload && sudo systemctl enable --now system-one && systemctl --no-pager status system-one | head -5
else
  echo "OK. Run:  $(pwd)/venv/bin/python $(pwd)/serve.py    (or re-run with --service for systemd)"
fi
