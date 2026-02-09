#!/bin/bash
set -e

# Start pcscd (smart card daemon) in background
pcscd --foreground &
PCSCD_PID=$!

# Give pcscd a moment to initialize
sleep 1

cleanup() {
    kill $PCSCD_PID 2>/dev/null || true
    wait $PCSCD_PID 2>/dev/null || true
}
trap cleanup EXIT

CMD="${1:-gui}"
shift 2>/dev/null || true

case "$CMD" in
    gui)
        exec python3 /app/gui_main.py "$@"
        ;;
    sja2)
        exec python3 /app/sysmo-isim-tool.sja2.py "$@"
        ;;
    sja5)
        exec python3 /app/sysmo-isim-tool.sja5.py "$@"
        ;;
    sjs1)
        exec python3 /app/sysmo-usim-tool.sjs1.py "$@"
        ;;
    bash|sh)
        exec /bin/bash "$@"
        ;;
    *)
        exec "$CMD" "$@"
        ;;
esac
