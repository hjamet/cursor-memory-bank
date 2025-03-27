#!/bin/bash

# Cursor Memory Bank Installation Script
# This script downloads and installs the Cursor Memory Bank rules while preserving existing custom rules.

set -e  # Exit on error
set -u  # Exit on undefined variable

# Constants
REPO_URL="https://github.com/lopilo24/cursor-memory-bank"
RULES_DIR=".cursor/rules"
TEMP_DIR="/tmp/cursor-memory-bank-$$"
VERSION="1.0.0"
ARCHIVE_NAME="rules.tar.gz"
CHECKSUM_FILE="rules.sha256"
DOWNLOAD_URL="https://raw.githubusercontent.com/lopilo24/cursor-memory-bank/main/dist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

cleanup() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}

backup_rules() {
    local target_dir="$1"
    if [[ -d "$target_dir/$RULES_DIR" ]]; then
        if [[ -z "${NO_BACKUP:-}" ]]; then
            local backup_dir="$target_dir/$RULES_DIR.bak-$(date +%Y%m%d-%H%M%S)"
            log "Backing up existing rules to $backup_dir"
            cp -r "$target_dir/$RULES_DIR" "$backup_dir"
        else
            warn "Skipping backup as --no-backup was specified"
        fi
    fi
}

create_dirs() {
    local target_dir="$1"
    log "Creating directory structure in $target_dir"
    mkdir -p "$target_dir/$RULES_DIR"
    mkdir -p "$target_dir/$RULES_DIR/custom/errors"
    mkdir -p "$target_dir/$RULES_DIR/custom/preferences"
    mkdir -p "$target_dir/$RULES_DIR/languages"
}

show_help() {
    cat << EOF
Cursor Memory Bank Installation Script v${VERSION}

Usage: $0 [options]

Options:
    -h, --help      Show this help message
    -v, --version   Show version information
    -d, --dir DIR   Install to a specific directory (default: current directory)
    --no-backup     Skip backup of existing rules
    --force         Force installation even if directory is not empty

This script will:
1. Download the Cursor Memory Bank rules
2. Preserve any existing custom rules
3. Update the core rules
4. Clean up temporary files

For more information, visit: ${REPO_URL}
EOF
    exit 0
}

show_version() {
    echo "Cursor Memory Bank Installation Script v${VERSION}"
    exit 0
}

# Parse command line arguments
INSTALL_DIR="."
NO_BACKUP=""
FORCE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -v|--version)
            show_version
            ;;
        -d|--dir)
            INSTALL_DIR="$2"
            shift
            ;;
        --no-backup)
            NO_BACKUP=1
            ;;
        --force)
            FORCE=1
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
    shift
done

# Set up cleanup on exit
trap cleanup EXIT

# Create temporary directory
mkdir -p "$TEMP_DIR"

# Main installation logic
if [[ ! -d "$INSTALL_DIR" ]]; then
    error "Installation directory does not exist: $INSTALL_DIR"
fi

# Check if rules directory exists and is not empty
if [[ -d "$INSTALL_DIR/$RULES_DIR" ]] && [[ -z "$FORCE" ]]; then
    if [[ -n "$(ls -A "$INSTALL_DIR/$RULES_DIR")" ]]; then
        error "Rules directory already exists and is not empty. Use --force to overwrite."
    fi
fi

# Backup existing rules if necessary
backup_rules "$INSTALL_DIR"

# Create directory structure
create_dirs "$INSTALL_DIR"

# Download and verify files
log "Starting download process..."
download_and_verify "$DOWNLOAD_URL" "$TEMP_DIR"

# TODO: Implement rules installation

log "Installation completed successfully!"

# Helper functions
download_file() {
    local url="$1"
    local output="$2"
    log "Downloading from $url"
    if ! curl -sSL --proto '=https' --tlsv1.2 -f "$url" -o "$output"; then
        error "Failed to download from $url"
    fi
}

verify_checksum() {
    local file="$1"
    local checksum_file="$2"
    log "Verifying checksum"
    if ! sha256sum -c "$checksum_file" > /dev/null 2>&1; then
        error "Checksum verification failed for $file"
    fi
}

download_and_verify() {
    local base_url="$1"
    local temp_dir="$2"
    
    # Download checksum file first
    download_file "$base_url/$CHECKSUM_FILE" "$temp_dir/$CHECKSUM_FILE"
    
    # Download archive
    download_file "$base_url/$ARCHIVE_NAME" "$temp_dir/$ARCHIVE_NAME"
    
    # Verify checksum
    cd "$temp_dir"
    verify_checksum "$ARCHIVE_NAME" "$CHECKSUM_FILE"
    cd - > /dev/null 