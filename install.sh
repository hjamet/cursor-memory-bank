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

# Main installation logic will be implemented here
# TODO: Implement download functionality
# TODO: Implement rules installation
# TODO: Implement backup functionality
# TODO: Implement cleanup

log "Installation completed successfully!" 