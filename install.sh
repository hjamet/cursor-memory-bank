#!/bin/bash

# Cursor Memory Bank Installation Script
# This script clones the Cursor Memory Bank repository and installs the rules while preserving existing custom rules.

set -e  # Exit on error
set -u  # Exit on undefined variable

# Constants
REPO_URL="https://github.com/hjamet/cursor-memory-bank.git"
DEFAULT_RULES_DIR=".cursor/rules"
RULES_DIR="${TEST_RULES_DIR:-$DEFAULT_RULES_DIR}"
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

cleanup() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}

# Git clone function
clone_repository() {
    local url="$1"
    local dest="$2"

    log "Cloning repository from $url"
    if ! git clone --quiet "$url" "$dest"; then
        error "Failed to clone repository from $url"
    fi
}

backup_rules() {
    local target_dir="$1"
    local rules_path="$target_dir/.cursor/rules"
    if [[ -d "$rules_path" ]]; then
        if [[ -z "${NO_BACKUP:-}" ]]; then
            local backup_dir="$rules_path.bak-$(date +%Y%m%d-%H%M%S)"
            log "Backing up existing rules to $backup_dir"
            cp -r "$rules_path" "$backup_dir"
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

install_rules() {
    local target_dir="$1"
    local temp_dir="$2"
    local rules_path="$target_dir/$RULES_DIR"
    local clone_dir="$temp_dir/repo"

    log "Installing rules to $rules_path"

    # Clone repository to temporary directory
    clone_repository "$REPO_URL" "$clone_dir"

    # Check for rules directory
    if [[ ! -d "$clone_dir/rules" ]]; then
        # If rules directory doesn't exist at root, check if rules are in .cursor/rules
        if [[ -d "$clone_dir/.cursor/rules" ]]; then
            # Create rules directory and copy files from .cursor/rules
            mkdir -p "$clone_dir/rules"
            cp -r "$clone_dir/.cursor/rules/"* "$clone_dir/rules/"
        else
            error "Invalid repository structure: neither rules/ nor .cursor/rules/ directory found"
        fi
    fi

    # Copy rules directory
    cp -r "$clone_dir/rules/"* "$rules_path/"

    # Preserve custom rules if they exist
    local backup_pattern="${rules_path}.bak-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]"
    local backup_dir=$(ls -d $backup_pattern 2>/dev/null | head -n 1)
    if [[ -n "$backup_dir" ]] && [[ -d "$backup_dir/custom" ]]; then
        log "Restoring custom rules from backup"
        cp -r "$backup_dir/custom/"* "$rules_path/custom/"
    fi

    # Set correct permissions
    chmod -R u+rw "$rules_path"
    find "$rules_path" -type d -exec chmod u+x {} \;

    log "Rules installed successfully"
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
1. Clone the Cursor Memory Bank repository
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

# Check if rules directory exists and is not empty (skip in test mode)
if [[ -z "${TEST_MODE:-}" ]]; then
    if [[ -d "$INSTALL_DIR/$RULES_DIR" ]] && [[ -z "$FORCE" ]]; then
        if [[ -n "$(ls -A "$INSTALL_DIR/$RULES_DIR")" ]]; then
            error "Rules directory already exists and is not empty. Use --force to overwrite."
        fi
    fi
fi

# Backup existing rules if necessary
backup_rules "$INSTALL_DIR"

# Create directory structure
create_dirs "$INSTALL_DIR"

# Install rules
install_rules "$INSTALL_DIR" "$TEMP_DIR"

log "Installation completed successfully!" 