#!/bin/bash

# Streamlit UI Startup Script for Cursor Memory Bank
# This script launches the Streamlit interface for monitoring agent status

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STREAMLIT_APP_DIR="$SCRIPT_DIR/streamlit_app"
STREAMLIT_MAIN="$STREAMLIT_APP_DIR/app.py"

# Check if Streamlit app exists
if [[ ! -f "$STREAMLIT_MAIN" ]]; then
    error "Streamlit app not found at: $STREAMLIT_MAIN"
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    error "Streamlit is not installed. Please install it using: pip install streamlit"
fi

# Check if we're in the right directory structure
if [[ ! -d "$SCRIPT_DIR/.cursor" ]]; then
    warn "This script should be run from the cursor-memory-bank root directory"
fi

log "Starting Cursor Memory Bank Streamlit UI..."
log "Streamlit app location: $STREAMLIT_MAIN"
log "Opening browser at: http://localhost:8501"
log ""
log "To stop the server, press Ctrl+C"
log ""

# Change to the streamlit app directory and run
cd "$STREAMLIT_APP_DIR"
exec streamlit run app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false 