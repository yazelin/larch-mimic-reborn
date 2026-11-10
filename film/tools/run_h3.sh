#!/usr/bin/env bash
# 跑一批 H3：先試 G4；分不到就同時開 2 台 A100 各跑一半（同帳號同時最多 2 台，2026-11-11 實測）。結束（含失敗、中斷）一定關機。
#   bash film/tools/run_h3.sh film/h3/batch1.txt
set -u
LIST=$(realpath "$1"); WF=~/vendor/shanshiba-workflow-colab; LOG=$(dirname "$LIST")/$(basename "$LIST" .txt).log
cd "$WF"
NAMES=()
cleanup() {
  for n in h3g "${NAMES[@]}"; do python3 cloud/colab_h3.py --name "$n" stop >/dev/null 2>&1; done
  echo "[關機] 完成；帳號狀態：$(colab usage 2>&1 | tr '\n' ' ')" | tee -a "$LOG"
}
trap cleanup EXIT INT TERM
mapfile -t SPECS < "$LIST"
echo "[開始] $(date) 共 ${#SPECS[@]} 段" | tee "$LOG"
if python3 cloud/colab_h3.py --name h3g start --h3-only >>"$LOG" 2>&1; then
  echo "[G4] 開到了，全部在 G4 跑" | tee -a "$LOG"
  python3 cloud/colab_h3.py --name h3g batch --h3-only "${SPECS[@]}" >>"$LOG" 2>&1
else
  echo "[G4] 分不到，改 2 台 A100" | tee -a "$LOG"
  python3 cloud/colab_h3.py --name h3g stop >/dev/null 2>&1
  PIDS=()
  for k in 0 1; do
    n="h3a$k"; NAMES+=("$n"); part=()
    for i in "${!SPECS[@]}"; do (( i % 2 == k )) && part+=("${SPECS[$i]}"); done
    python3 cloud/colab_h3.py --name "$n" batch --gpu A100 --instances 1 --h3-only "${part[@]}" > "${LOG%.log}_$n.log" 2>&1 &
    PIDS+=($!); sleep 20
  done
  for p in "${PIDS[@]}"; do wait "$p"; done
fi
ok=$(for s in "${SPECS[@]}"; do [ -s "$(dirname "$s")/clip.mp4" ] && echo y; done | wc -l)
echo "[結束] $(date) 成品 $ok / ${#SPECS[@]}" | tee -a "$LOG"
