#!/bin/bash
# Run sysmo-usim-tool in Docker
#
# Usage:
#   ./docker-run.sh              # Launch GUI
#   ./docker-run.sh sja5 --help  # CLI tool
#   ./docker-run.sh bash         # Debug shell

docker run --rm -it \
    --privileged \
    -e DISPLAY="$DISPLAY" \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --network host \
    johneff/sysmo-usim-tool "$@"
