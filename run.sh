#!/usr/bin/env bash
set -e

PROJECT_HOME="$1"

if [ -z "$PROJECT_HOME" ]; then
    echo "Usage: $0 /path/to/TexQL"
    exit 1
fi

BACKEND_DIR="$PROJECT_HOME/texql/src"
FRONTEND_DIR="$PROJECT_HOME/fend"

echo "Starting Flask backend..."
(
    cd "$BACKEND_DIR"
    FLASK_APP=texql.app poetry run flask run
) &
BACKEND_PID=$!

echo "Starting Vue frontend..."
(
    cd "$FRONTEND_DIR"
    npm run dev
) &
FRONTEND_PID=$!

cleanup() {
    echo
    echo "Stopping Flask and Vue..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}

wait "$BACKEND_PID" "$FRONTEND_PID"
