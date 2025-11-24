#!/usr/bin/env bash
# watch_logs.sh - start uvicorn and monitor dev.log for errors
# Usage: ./scripts/watch_logs.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

LOGFILE="$ROOT_DIR/dev.log"
ERRORFILE="$ROOT_DIR/errors.log"
PIDFILE="$ROOT_DIR/.uvicorn.pid"

UVICORN_CMD=".venv/bin/uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
if [ ! -x .venv/bin/uvicorn ]; then
  UVICORN_CMD="uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
fi

# Kill existing uvicorn processes started from this project
if [ -f "$PIDFILE" ]; then
  OLD_PID=$(cat "$PIDFILE" 2>/dev/null || true)
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Killing previous uvicorn (PID $OLD_PID)"
    kill "$OLD_PID" || true
    sleep 1
  fi
fi
pkill -f "uvicorn backend.main:app" || true

# Start uvicorn writing to log
echo "Starting uvicorn: $UVICORN_CMD"
# run uvicorn in background and redirect output
bash -c "$UVICORN_CMD > \"$LOGFILE\" 2>&1 & echo \$! > \"$PIDFILE\""
sleep 1

# Ensure log file exists
touch "$LOGFILE"

# Follow the log and highlight errors
echo "Tailing $LOGFILE (errors go to $ERRORFILE)"

# tail and filter
tail -n +1 -F "$LOGFILE" | while IFS= read -r line; do
  echo "$line"
  if echo "$line" | grep -Ei "error|traceback|exception" >/dev/null; then
    printf "\n⚠️ [ALERTA] %s — %s\n\n" "$(date '+%F %T')" "$line" | tee -a "$ERRORFILE" >&2
  fi
done
