#!/bin/bash

# Script to create a release archive for Cursor Memory Bank

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Error handling
error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

# Logging
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default directories
DIST_DIR="${DIST_DIR:-$PROJECT_ROOT/dist}"
VERSION="1.0.0"
ARCHIVE_NAME="cursor-memory-bank-$VERSION.tar.gz"

# Main function
main() {
    # Create distribution directory if it doesn't exist
    if ! mkdir -p "$DIST_DIR"; then
        error "Cannot create distribution directory"
    fi

    # Create project archive
    log "Creating project archive..."
    if ! cd "$PROJECT_ROOT"; then
        error "Cannot change to project root directory"
    fi

    # Create archive excluding dist/ and .git/
    if ! tar --exclude='./dist' --exclude='./.git' -czf "$DIST_DIR/$ARCHIVE_NAME" .; then
        error "Failed to create project archive"
    fi

    if ! cd - > /dev/null; then
        error "Cannot change back to original directory"
    fi

    log "Release files created successfully in $DIST_DIR:"
    ls -l "$DIST_DIR"
}

# Run main function
main 