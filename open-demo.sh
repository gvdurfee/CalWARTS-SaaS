#!/bin/zsh
# Start the demo and print a local URL for the Cursor browser.
# Run this in Cursor's integrated terminal. Cursor opens that URL
# in its browser when the command finishes.
# Do not use the macOS `open` command; that launches Safari.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8765}"

while lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; do
  PORT=$((PORT + 1))
done

python3 "$ROOT/demo/serve.py" "$ROOT/demo" "$PORT" >/tmp/calwatrs-demo-server.log 2>&1 &
echo $! >/tmp/calwatrs-demo-server.pid

URL="http://127.0.0.1:${PORT}/"
for _ in {1..50}; do
  if curl -sf -o /dev/null "$URL"; then
    break
  fi
  sleep 0.1
done

echo ""
echo "$URL"
echo "Cursor should open that address in the Cursor browser."
echo "Stop the server later with: kill \$(cat /tmp/calwatrs-demo-server.pid)"
