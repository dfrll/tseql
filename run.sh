#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_HOME="${1:-}"

if [[ -z "$PROJECT_HOME" ]]; then
    echo "Usage: $0 /path/to/project"
    exit 1
fi

PROJECT_HOME="$(cd "$PROJECT_HOME" && pwd)"

BACKEND_DIR="$PROJECT_HOME/tseql/src"
FRONTEND_DIR="$PROJECT_HOME/fend"

if [[ ! -d "$BACKEND_DIR" ]]; then
    echo "Error: backend directory not found:"
    echo "  $BACKEND_DIR"
    exit 1
fi

if [[ ! -d "$FRONTEND_DIR" ]]; then
    echo "Error: frontend directory not found:"
    echo "  $FRONTEND_DIR"
    exit 1
fi

if [[ ! -x "$FRONTEND_DIR/node_modules/.bin/vite" ]]; then
    echo "Error: Vite is not installed."
    echo "Run:"
    echo "  cd \"$FRONTEND_DIR\" && npm install"
    exit 1
fi

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    trap - INT TERM EXIT

    echo
    echo "Stopping Flask and Vue..."

    if [[ -n "$BACKEND_PID" ]]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi

    if [[ -n "$FRONTEND_PID" ]]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi

    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

echo "Starting Flask backend..."

(
    cd "$BACKEND_DIR"
    exec poetry run flask \
        --app tseql.app \
        run \
        --debug \
        --host 127.0.0.1 \
        --port 5000
) &
BACKEND_PID=$!

echo "Starting Vue frontend..."

(
    cd "$FRONTEND_DIR"
    exec npm run dev -- --host 127.0.0.1
) &
FRONTEND_PID=$!

# Keep the script running while both services are running.
wait "$BACKEND_PID" "$FRONTEND_PID"
