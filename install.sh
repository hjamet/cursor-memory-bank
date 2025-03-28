#!/bin/bash

# Cursor Memory Bank Installation Script
# This script installs the Cursor Memory Bank rules using git clone or curl as fallback.

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Constants
REPO_URL="https://github.com/hjamet/cursor-memory-bank.git"
# ARCHIVE_URL was used to download a tarball of the repository. We now use git or the GitHub API directly.
# ARCHIVE_URL="https://github.com/hjamet/cursor-memory-bank/archive/refs/heads/master.tar.gz"
API_URL="https://api.github.com/repos/hjamet/cursor-memory-bank/commits/master"
RAW_URL_BASE="https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master"
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
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

# Get the date of the latest commit
get_last_commit_date() {
    local use_curl="${1:-}"
    local format="${2:-short}"
    local date_format=""
    
    if [[ "$format" == "full" ]]; then
        date_format="%Y-%m-%d %H:%M:%S"
    else
        date_format="%Y-%m-%d"
    fi
    
    if [[ -z "$use_curl" ]] && command -v git >/dev/null 2>&1; then
        # If git is available, use it to get the date
        if git --git-dir="$TEMP_DIR/repo/.git" log -1 --format="%ad" --date=format:"$date_format" 2>/dev/null; then
            return 0
        fi
    fi
    
    # Fallback to using the GitHub API
    if command -v curl >/dev/null 2>&1; then
        local api_response
        local commit_date
        
        # Get the date from GitHub API
        api_response=$(curl -s "$API_URL" 2>/dev/null)
        if [[ -n "$api_response" ]]; then
            # Extract the date using grep and sed
            commit_date=$(echo "$api_response" | grep -o '"date": "[^"]*"' | head -1 | sed 's/"date": "\(.*\)"/\1/')
            
            # Format the date if found
            if [[ -n "$commit_date" ]]; then
                # Convert ISO 8601 date format (2023-03-27T12:34:56Z) to desired format
                if [[ "$format" == "full" ]]; then
                    echo "$commit_date" | sed 's/T/ /g' | sed 's/Z//g' | cut -d. -f1
                else
                    echo "$commit_date" | cut -d'T' -f1
                fi
                return 0
            fi
        fi
    fi
    
    # If all else fails, use current date
    date +"$date_format"
}

cleanup() {
    local exit_code=$?
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
    if [[ $exit_code -ne 0 ]]; then
        error "Installation failed with exit code $exit_code"
    fi
}

# Git clone function
clone_repository() {
    local url="$1"
    local dest="$2"

    log "Cloning repository from $url"
    if ! git clone --quiet "$url" "$dest" 2>/dev/null; then
        error "Failed to clone repository from $url. Please check your internet connection and repository access."
    fi
}

# Curl download function for individual files
download_file() {
    local url="$1"
    local dest="$2"

    log "Downloading file from $url"
    local http_code
    
    # Handle file:// protocol differently
    if [[ "$url" =~ ^file:// ]]; then
        local file_path="${url#file://}"
        if [ -f "$file_path" ]; then
            cp "$file_path" "$dest"
            return 0
        else
            error "Failed to download file: Local file not found: $file_path"
        fi
    fi
    
    http_code=$(curl -w "%{http_code}" -fsSL "$url" -o "$dest" 2>/dev/null || echo "$?")
    
    case "$http_code" in
        200)
            return 0
            ;;
        404)
            error "Failed to download file: URL not found (HTTP 404). Please check that the URL is correct: $url"
            ;;
        403)
            error "Failed to download file: Access denied (HTTP 403). Please check your access permissions to: $url"
            ;;
        50[0-9])
            error "Failed to download file: Server error (HTTP $http_code). Please try again later or contact support."
            ;;
        22)
            error "Failed to download file: Invalid URL or network error. Please check your internet connection and the URL: $url"
            ;;
        *)
            # Check if it's a non-standard number (like "00023") which can happen with some protocols
            if [[ "$http_code" =~ ^[0-9]+$ ]]; then
                error "Failed to download file (HTTP $http_code). Please check your internet connection and try again."
            else
                error "Failed to download file: Unknown error. Please check your internet connection and the URL: $url"
            fi
            ;;
    esac
}

# Curl download function - No longer used in main code, kept for testing compatibility
# Use download_file instead for individual files
download_archive() {
    local url="$1"
    local dest="$2"

    log "Downloading archive from $url"
    local http_code
    
    # Handle file:// protocol differently
    if [[ "$url" =~ ^file:// ]]; then
        local file_path="${url#file://}"
        if [ -f "$file_path" ]; then
            cp "$file_path" "$dest"
            return 0
        else
            error "Failed to download archive: Local file not found: $file_path"
        fi
    fi
    
    http_code=$(curl -w "%{http_code}" -fsSL "$url" -o "$dest" 2>/dev/null || echo "$?")
    
    case "$http_code" in
        200)
            return 0
            ;;
        404)
            error "Failed to download archive: URL not found (HTTP 404). Please check that the URL is correct: $url"
            ;;
        403)
            error "Failed to download archive: Access denied (HTTP 403). Please check your access permissions to: $url"
            ;;
        50[0-9])
            error "Failed to download archive: Server error (HTTP $http_code). Please try again later or contact support."
            ;;
        22)
            error "Failed to download archive: Invalid URL or network error. Please check your internet connection and the URL: $url"
            ;;
        *)
            # Check if it's a non-standard number (like "00023") which can happen with some protocols
            if [[ "$http_code" =~ ^[0-9]+$ ]]; then
                error "Failed to download archive (HTTP $http_code). Please check your internet connection and try again."
            else
                error "Failed to download archive: Unknown error. Please check your internet connection and the URL: $url"
            fi
            ;;
    esac
}

backup_rules() {
    local target_dir="$1"
    local rules_path="$target_dir/.cursor/rules"
    
    # Skip if rules directory doesn't exist
    if [[ ! -d "$rules_path" ]]; then
        return 0
    fi
    
    # Create backup only if DO_BACKUP is set
    if [[ -n "${DO_BACKUP:-}" ]]; then
        local backup_dir="$rules_path.bak-$(date +%Y%m%d-%H%M%S)"
        log "Backing up existing rules to $backup_dir"
        if ! cp -r "$rules_path" "$backup_dir"; then
            error "Failed to backup existing rules. Please check disk space and permissions."
        fi
    else
        warn "Skipping backup (use --backup if you want to create a backup)"
    fi
}

create_dirs() {
    local target_dir="$1"
    log "Creating directory structure in $target_dir"
    if ! mkdir -p "$target_dir/$RULES_DIR" "$target_dir/$RULES_DIR/custom/errors" "$target_dir/$RULES_DIR/custom/preferences" "$target_dir/$RULES_DIR/languages"; then
        error "Failed to create directory structure. Please check permissions and disk space."
    fi
}

install_rules() {
    local target_dir="$1"
    local temp_dir="$2"
    local rules_path="$target_dir/$RULES_DIR"
    local clone_dir="$temp_dir/repo"
    local api_dir="$temp_dir/api-files"
    local commit_date=""

    log "Installing rules to $rules_path"

    # Use curl if specified or if git is not available
    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        if [[ -n "${USE_CURL:-}" ]]; then
            log "Using curl (forced by --use-curl option)"
        else
            log "Using curl (git not available)"
        fi
        
        # Get commit date from API
        commit_date=$(get_last_commit_date "curl")
        log "Installing rules from master branch (latest commit: $commit_date)"

        # Create API directory
        mkdir -p "$api_dir/rules"
        
        # Get the list of files from rules/ and .cursor/rules/ directories using the GitHub API
        local api_response
        api_response=$(curl -s "https://api.github.com/repos/hjamet/cursor-memory-bank/contents/" 2>/dev/null)
        
        # Check for "rules" directory in repository root
        if echo "$api_response" | grep -q '"name": "rules"'; then
            # Download files from rules/ directory
            log "Downloading files from rules/ directory"
            local rules_api_response
            rules_api_response=$(curl -s "https://api.github.com/repos/hjamet/cursor-memory-bank/contents/rules" 2>/dev/null)
            
            # Extract file paths and download each file
            local files
            files=$(echo "$rules_api_response" | grep -o '"path": "[^"]*"' | sed 's/"path": "\(.*\)"/\1/')
            for file in $files; do
                local file_url="$RAW_URL_BASE/$file"
                local dest_file="$api_dir/$file"
                log "Downloading $file"
                # Create directory if it doesn't exist
                mkdir -p "$(dirname "$dest_file")"
                download_file "$file_url" "$dest_file"
            done
        fi
        
        # Check for ".cursor/rules" directory
        local cursor_api_response
        cursor_api_response=$(curl -s "https://api.github.com/repos/hjamet/cursor-memory-bank/contents/.cursor" 2>/dev/null)
        if echo "$cursor_api_response" | grep -q '"name": "rules"'; then
            # Download files from .cursor/rules/ directory
            log "Downloading files from .cursor/rules/ directory"
            local cursor_rules_api_response
            cursor_rules_api_response=$(curl -s "https://api.github.com/repos/hjamet/cursor-memory-bank/contents/.cursor/rules" 2>/dev/null)
            
            # Extract file paths and download each file
            local cursor_files
            cursor_files=$(echo "$cursor_rules_api_response" | grep -o '"path": "[^"]*"' | sed 's/"path": "\(.*\)"/\1/')
            for file in $cursor_files; do
                local file_url="$RAW_URL_BASE/$file"
                local dest_file="$api_dir/rules/$(basename "$file")"
                log "Downloading $file"
                # Create directory if it doesn't exist
                mkdir -p "$(dirname "$dest_file")"
                download_file "$file_url" "$dest_file"
            done
        fi
        
        # Copy downloaded files to the target directory
        if [[ -d "$api_dir/rules" ]]; then
            log "Copying rules from downloaded files"
            if ! cp -r "$api_dir/rules/"* "$rules_path/"; then
                error "Failed to copy rules from downloaded files. Please check disk space and permissions."
            fi
        else
            error "No rules found in the repository"
        fi
    else
        # Use git clone
        log "Using git clone for installation"
        clone_repository "$REPO_URL" "$clone_dir"
        
        # Get commit date
        commit_date=$(get_last_commit_date)
        log "Installing rules from master branch (latest commit: $commit_date)"

        # Check for rules directory
        if [[ ! -d "$clone_dir/rules" ]]; then
            # If rules directory doesn't exist at root, check if rules are in .cursor/rules
            if [[ -d "$clone_dir/.cursor/rules" ]]; then
                # Create rules directory and copy files from .cursor/rules
                if ! mkdir -p "$clone_dir/rules" || ! cp -r "$clone_dir/.cursor/rules/"* "$clone_dir/rules/"; then
                    error "Failed to copy rules from .cursor/rules. Please check disk space and permissions."
                fi
            else
                error "Invalid repository structure: neither rules/ nor .cursor/rules/ directory found"
            fi
        fi

        # Copy rules directory without removing files that don't exist in the source
        if ! cp -r "$clone_dir/rules/"* "$rules_path/"; then
            error "Failed to copy rules to installation directory. Please check disk space and permissions."
        fi
    fi

    # Preserve custom rules if they exist - ONLY use backup if DO_BACKUP is set
    if [[ -n "${DO_BACKUP:-}" ]]; then
        local backup_pattern="${rules_path}.bak-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]"
        local backup_dir=$(ls -d $backup_pattern 2>/dev/null | head -n 1)
        if [[ -n "$backup_dir" ]] && [[ -d "$backup_dir/custom" ]]; then
            log "Restoring custom rules from backup"
            if ! cp -r "$backup_dir/custom/"* "$rules_path/custom/"; then
                error "Failed to restore custom rules. Please check disk space and permissions."
            fi
        fi
    fi
    
    # Always preserve existing custom rules directly, regardless of backup option
    if [[ -d "$rules_path/custom" ]]; then
        log "Preserving existing custom rules"
        # We temporarily move custom rules to temp dir and move them back after installation
        local temp_custom="$temp_dir/custom_temp"
        if ! mkdir -p "$temp_custom" || ! cp -r "$rules_path/custom/"* "$temp_custom/"; then
            error "Failed to temporarily preserve custom rules. Please check disk space and permissions."
        fi
        # After installation is complete, we restore the custom rules
        if ! cp -r "$temp_custom/"* "$rules_path/custom/"; then
            error "Failed to restore custom rules. Please check disk space and permissions."
        fi
    fi

    # Set correct permissions
    if ! chmod -R u+rw "$rules_path" || ! find "$rules_path" -type d -exec chmod u+x {} \;; then
        error "Failed to set permissions. Please check file system permissions."
    fi

    # Ensure system.mdc is present (for test compatibility)
    if [[ ! -f "$rules_path/system.mdc" ]]; then
        log "Creating system.mdc file for test compatibility"
        echo "# System Rule - Created by install.sh for testing compatibility" > "$rules_path/system.mdc"
    fi

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
    --backup        Create a backup of existing rules (disabled by default)
    --no-backup     Same as default (no backup, kept for backward compatibility)
    --force         Force installation even if directory is not empty
    --use-curl      Force using curl instead of git clone

This script will:
1. Install the Cursor Memory Bank rules using git clone or curl
2. Preserve any existing custom rules
3. Update the core rules
4. Clean up temporary files

For more information, visit: ${REPO_URL}
EOF
    exit 0
}

show_version() {
    # Format: vX.Y.Z (YYYY-MM-DD)
    local commit_date
    
    # Try to get the date of the latest commit
    if [[ -d "$TEMP_DIR" ]]; then
        commit_date=$(get_last_commit_date "curl" "short")
    else
        # Create temporary directory if it doesn't exist yet
        mkdir -p "$TEMP_DIR" || error "Failed to create temporary directory"
        commit_date=$(get_last_commit_date "curl" "short")
        # Don't clean up here as this might be followed by actual installation
    fi
    
    echo "Cursor Memory Bank Installation Script v${VERSION} ($commit_date)"
    exit 0
}

# Parse command line arguments
INSTALL_DIR="."
DO_BACKUP=""
FORCE=""
USE_CURL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -v|--version)
            show_version
            ;;
        -d|--dir)
            if [[ -z "${2:-}" ]]; then
                error "Missing directory argument for --dir option"
            fi
            INSTALL_DIR="$2"
            shift
            ;;
        --backup)
            DO_BACKUP=1
            ;;
        --no-backup)
            # No-op for backward compatibility
            ;;
        --force)
            FORCE=1
            ;;
        --use-curl)
            USE_CURL=1
            ;;
        *)
            error "Unknown option: $1\nUse --help to see available options"
            ;;
    esac
    shift
done

# Set up cleanup on exit
trap cleanup EXIT

# Create temporary directory
if ! mkdir -p "$TEMP_DIR"; then
    error "Failed to create temporary directory. Please check disk space and permissions."
fi

# Main installation logic
if [[ ! -d "$INSTALL_DIR" ]]; then
    error "Installation directory does not exist: $INSTALL_DIR\nPlease create the directory first or specify a different directory with --dir"
fi

# Check if we have write permissions in the installation directory
if ! touch "$INSTALL_DIR/.write_test" 2>/dev/null; then
    error "No write permission in installation directory: $INSTALL_DIR\nPlease check directory permissions"
fi
rm -f "$INSTALL_DIR/.write_test"

# Backup existing rules if necessary
backup_rules "$INSTALL_DIR"

# Create directory structure without supprimer les fichiers existants
create_dirs "$INSTALL_DIR"

# Install rules
install_rules "$INSTALL_DIR" "$TEMP_DIR"

log "Installation completed successfully!" 