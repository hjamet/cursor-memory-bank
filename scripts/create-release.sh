#!/bin/bash

# Script to create a release archive for Cursor Memory Bank rules

set -e  # Exit on error
set -u  # Exit on undefined variable

# Constants
RULES_DIR=".cursor/rules"
DIST_DIR="dist"
ARCHIVE_NAME="rules.tar.gz"
CHECKSUM_FILE="rules.sha256"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Create dist directory
mkdir -p "$DIST_DIR"

# Create rules archive
log "Creating rules archive..."
if ! tar -czf "$DIST_DIR/$ARCHIVE_NAME" -C "$RULES_DIR" .; then
    error "Failed to create rules archive"
fi

# Create checksum file
log "Creating checksum file..."
cd "$DIST_DIR"
if ! sha256sum "$ARCHIVE_NAME" > "$CHECKSUM_FILE"; then
    error "Failed to create checksum file"
fi
cd - > /dev/null

log "Release files created successfully in $DIST_DIR:"
ls -l "$DIST_DIR" 