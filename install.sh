#!/bin/bash

# Cursor Memory Bank Installation Script
# This script installs the Cursor Memory Bank workflow system using git clone or curl as fallback.
# Test comment to trigger pre-commit hook line count check.
# Second test comment after fixing commit tool logic.

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Constants
REPO_URL="https://github.com/hjamet/cursor-memory-bank.git"
# ARCHIVE_URL was used to download a tarball of the repository. We now use git or the GitHub API directly.
# ARCHIVE_URL="https://github.com/hjamet/cursor-memory-bank/archive/refs/heads/master.tar.gz"
GITHUB_REPO="hjamet/cursor-memory-bank"
GITHUB_API="https://api.github.com/repos/$GITHUB_REPO"

# Detect default branch on GitHub (fallback to master)
# We try to detect early so functions using API_URL / RAW_URL_BASE use the correct branch.
DEFAULT_BRANCH=$(curl -s "$GITHUB_API" \
  | grep -o '"default_branch"[[:space:]]*:[[:space:]]*"[^"]*"' \
  | sed 's/.*: *"//; s/"$//' || true)
if [[ -z "$DEFAULT_BRANCH" ]]; then
    DEFAULT_BRANCH="master"
fi
API_URL="$GITHUB_API/commits/$DEFAULT_BRANCH"
RAW_URL_BASE="https://raw.githubusercontent.com/$GITHUB_REPO/$DEFAULT_BRANCH"
DEFAULT_WORKFLOW_DIR=".cursor/workflow-steps"
WORKFLOW_DIR="${TEST_WORKFLOW_DIR:-$DEFAULT_WORKFLOW_DIR}"
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

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Check Node.js and npm availability and versions
# Usage: check_nodejs_requirements
check_nodejs_requirements() {
    log "Checking Node.js and npm requirements..."
    
    # Check if Node.js is installed
    if ! command -v node >/dev/null 2>&1; then
        error "Node.js is not installed. Please install Node.js 14.0.0 or higher from https://nodejs.org/"
    fi
    
    # Check Node.js version
    local node_version
    node_version=$(node --version 2>/dev/null | sed 's/v//')
    local node_major
    node_major=$(echo "$node_version" | cut -d. -f1)
    
    if [[ "$node_major" -lt 14 ]]; then
        error "Node.js version $node_version is too old. Please install Node.js 14.0.0 or higher."
    fi
    
    log "✓ Node.js version $node_version detected"
    
    # Check if npm is installed
    if ! command -v npm >/dev/null 2>&1; then
        error "npm is not installed. Please install npm (usually comes with Node.js)."
    fi
    
    local npm_version
    npm_version=$(npm --version 2>/dev/null)
    log "✓ npm version $npm_version detected"
}

# Validate JSON file syntax
# Usage: validate_json_file "/path/to/file.json"
validate_json_file() {
    local json_file="$1"
    
    if [[ ! -f "$json_file" ]]; then
        error "JSON file not found: $json_file"
    fi
    
    # Try with jq if available (best option)
    if command -v jq >/dev/null 2>&1; then
        if ! jq empty "$json_file" 2>/dev/null; then
            error "Invalid JSON in file: $json_file"
        fi
        return 0
    fi
    
    # Fallback to python if available
    if command -v python3 >/dev/null 2>&1; then
        if ! python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
            error "Invalid JSON in file: $json_file"
        fi
        return 0
    fi
    
    if command -v python >/dev/null 2>&1; then
        if ! python -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
            error "Invalid JSON in file: $json_file"
        fi
        return 0
    fi
    
    # If no validator available, just check basic syntax
    if ! grep -q '{' "$json_file" || ! grep -q '}' "$json_file"; then
        error "JSON file appears malformed: $json_file"
    fi
    
    log "⚠️ Could not fully validate JSON (jq/python not available), basic checks passed"
}

# Convert Unix path to Windows path if running on Windows (Git Bash/MSYS)
# Usage: windows_path=$(convert_to_windows_path "/c/Users/...")
convert_to_windows_path() {
    local unix_path="$1"
    local os_type=""
    
    # Detect OS type
    if command -v uname >/dev/null 2>&1; then
        os_type=$(uname -o)
    fi
    
    # If not on Windows, return path as-is
    if [[ "$os_type" != "Msys" ]]; then
        echo "$unix_path"
        return 0
    fi
    
    # Try using cygpath if available (preferred method)
    if command -v cygpath >/dev/null 2>&1; then
        if win_path=$(cygpath -w "$unix_path" 2>/dev/null); then
            echo "$win_path"
            return 0
        fi
    fi
    
    # Fallback: manual conversion for Git Bash/MSYS
    # Convert /c/ to C:\\ and all / to \\
    local win_path
    win_path=$(echo "$unix_path" | sed -e 's|^/c/|C:\\|' -e 's|/|\\|g')
    echo "$win_path"
}

# ============================================================================
# REPOSITORY & VERSION FUNCTIONS
# ============================================================================

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

# ============================================================================
# FILE DOWNLOAD & REPOSITORY FUNCTIONS
# ============================================================================

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
# download_file(url, dest, [required])
# If third argument == "required" then missing files or HTTP errors are fatal (fail-fast).
download_file() {
    local url="$1"
    local dest="$2"
    local required_flag="${3:-}"

    log "Downloading file from $url"
    local http_code
    local curl_exit_code

    # Handle file:// protocol differently
    if [[ "$url" =~ ^file:// ]]; then
        local file_path="${url#file://}"
        if [ -f "$file_path" ]; then
            cp "$file_path" "$dest"
            return 0
        else
            if [[ "$required_flag" == "required" ]]; then
                error "Failed to download file: Local file not found: $file_path"
            else
                warn "Local file not found (optional): $file_path"
                return 0
            fi
        fi
    fi

    set +e
    http_code=$(curl -w "%{http_code}" -fsSL "$url" -o "$dest" 2>/dev/null)
    curl_exit_code=$?
    set -e

    debug_info="http_code=$http_code curl_exit_code=$curl_exit_code"

    if [[ $curl_exit_code -ne 0 ]] && [[ $curl_exit_code -ne 22 ]]; then
        if [[ "$required_flag" == "required" ]]; then
            error "curl command failed (exit $curl_exit_code) for URL: $url. Debug: $debug_info"
        else
            warn "curl command failed (exit $curl_exit_code) for optional URL: $url. Debug: $debug_info"
            return 0
        fi
    fi

    case "$http_code" in
        200)
            if [[ ! -s "$dest" ]]; then
                if [[ "$required_flag" == "required" ]]; then
                    error "Downloaded file is empty or missing after HTTP 200: $dest. Debug: $debug_info"
                else
                    warn "Downloaded file is empty or missing after HTTP 200 (optional): $dest. Debug: $debug_info"
                    return 0
                fi
            fi
            return 0
            ;;
        404)
            if [[ "$required_flag" == "required" ]]; then
                error "Failed to download file: URL not found (HTTP 404): $url. Debug: $debug_info"
            else
                warn "URL not found (HTTP 404) for optional file: $url. Skipping. Debug: $debug_info"
                return 0
            fi
            ;;
        403)
            if [[ "$required_flag" == "required" ]]; then
                error "Failed to download file: Access denied (HTTP 403). Please check your access permissions to: $url. Debug: $debug_info"
            else
                warn "Access denied (HTTP 403) for optional file: $url. Skipping. Debug: $debug_info"
                return 0
            fi
            ;;
        50[0-9])
            if [[ "$required_flag" == "required" ]]; then
                error "Failed to download file: Server error (HTTP $http_code). Please try again later or contact support. Debug: $debug_info"
            else
                warn "Server error (HTTP $http_code) for optional file: $url. Skipping. Debug: $debug_info"
                return 0
            fi
            ;;
        *)
            if [[ "$http_code" =~ ^[0-9]+$ ]]; then
                if [[ "$required_flag" == "required" ]]; then
                    error "Failed to download file (Unexpected HTTP status: $http_code) for URL: $url. Debug: $debug_info"
                else
                    warn "Unexpected HTTP status ($http_code) for optional file: $url. Skipping. Debug: $debug_info"
                    return 0
                fi
            else
                if [[ "$required_flag" == "required" ]]; then
                    error "Failed to download file: Unknown error (curl exit: $curl_exit_code, http code: '$http_code'). Check URL: $url. Debug: $debug_info"
                else
                    warn "Unknown download error for optional file: $url. Debug: $debug_info"
                    return 0
                fi
            fi
            ;;
    esac
}

# Ensure a rule file exists: copy from clone if available, otherwise download from RAW_URL_BASE
# ensure_rule_file(path_in_repo, dest_path, required_flag)
ensure_rule_file() {
    local path_in_repo="$1"
    local dest_path="$2"
    local required_flag="${3:-}"
    local clone_source="$TEMP_DIR/repo/$path_in_repo"
    local raw_url="$RAW_URL_BASE/$path_in_repo"

    mkdir -p "$(dirname "$dest_path")"

    if [[ -f "$clone_source" ]]; then
        log "Copying $path_in_repo from git clone to $dest_path"
        if cp "$clone_source" "$dest_path"; then
            if [[ ! -s "$dest_path" ]]; then
                warn "Copied file is empty: $dest_path"
                if [[ "$required_flag" == "required" ]]; then
                    log "Attempting to download missing/empty file from $raw_url"
                    download_file "$raw_url" "$dest_path" "$required_flag"
                fi
            fi
            return 0
        else
            warn "Failed to copy $clone_source to $dest_path"
        fi
    fi

    log "Downloading $path_in_repo to $dest_path (fallback)"
    download_file "$raw_url" "$dest_path" "$required_flag"
}

# Check membership helper: is_in_array "needle" "${array[@]}"
is_in_array() {
    local needle="$1"
    shift
    local item
    for item in "$@"; do
        if [[ "$item" == "$needle" ]]; then
            return 0
        fi
    done
    return 1
}

# Recursively fetch all rule files from GitHub API
# Usage: fetch_rules_recursive "path_in_repo" -> returns space-separated list of file paths
fetch_rules_recursive() {
    local path_in_repo="$1"
    local api_url="$GITHUB_API/contents/$path_in_repo?ref=$DEFAULT_BRANCH"
    local api_response
    local rules_list=""
    
    log "Fetching rules recursively from $path_in_repo"
    
    api_response=$(curl -s "$api_url" 2>/dev/null || true)
    if [[ -z "$api_response" ]]; then
        warn "Failed to fetch directory contents for $path_in_repo"
        return 1
    fi
    
    local names_and_types
    names_and_types=$(echo "$api_response" | grep -o '"name": *"[^"]*", *"type": *"[^"]*"' | sed 's/"name": *"\([^"]*\)", *"type": *"\([^"]*\)"/\1:\2/')
    
    while IFS= read -r name_type; do
        if [[ -n "$name_type" ]]; then
            local name="${name_type%%:*}"
            local type="${name_type##*:}"
            
            if [[ "$type" == "file" ]] && [[ "$name" == *.mdc ]]; then
                rules_list="$rules_list $path_in_repo/$name"
            elif [[ "$type" == "dir" ]]; then
                local subdir_rules=$(fetch_rules_recursive "$path_in_repo/$name")
                rules_list="$rules_list $subdir_rules"
            fi
        fi
    done <<< "$names_and_types"
    
    echo "${rules_list# }"
}

# ============================================================================
# GITIGNORE MANAGEMENT
# ============================================================================

manage_gitignore() {
    local target_dir="$1"
    local gitignore_file="$target_dir/.gitignore"
    local no_gitignore_flag="${NO_GITIGNORE:-}"

    if [[ -n "$no_gitignore_flag" ]]; then
        log "Skipping .gitignore management due to --no-gitignore flag"
        return
    fi

    log "Ensuring minimal .gitignore entries..."

    if [[ ! -d "$(dirname "$gitignore_file")" ]]; then
        mkdir -p "$(dirname "$gitignore_file")"
    fi

    if [[ ! -f "$gitignore_file" ]]; then
        cat > "$gitignore_file" <<EOF
# Cursor Memory Bank
.cursor/mcp
.cursor/mcp.json
.cursor/screenshots
EOF
        log "Created .gitignore with minimal rules at: $gitignore_file"
    else
        if [[ -s "$gitignore_file" ]]; then
            last_char=$(tail -c 1 "$gitignore_file" 2>/dev/null || printf '')
            if [[ "$last_char" != $'\n' ]]; then
                echo "" >> "$gitignore_file"
            fi
        fi

        if ! grep -Fxq "# Cursor Memory Bank" "$gitignore_file" 2>/dev/null; then
            cat >> "$gitignore_file" <<EOF
# Cursor Memory Bank
.cursor/mcp
.cursor/mcp.json
.cursor/screenshots
EOF
            log "Appended Cursor Memory Bank block to .gitignore: $gitignore_file"
        else
            log "Cursor Memory Bank .gitignore header already present; ensuring additional entries exist"
            for entry in ".cursor/screenshots"; do
                if ! grep -Fxq "$entry" "$gitignore_file" 2>/dev/null; then
                    echo "$entry" >> "$gitignore_file"
                    log "Appended '$entry' to $gitignore_file"
                fi
            done
        fi
    fi

    if validate_gitignore_rules "$target_dir"; then
        log "✅ .gitignore rules validated successfully"
    else
        warn "⚠️ .gitignore validation found issues - rules may need manual adjustment"
        warn "This is not a critical error and installation will continue"
    fi

    handle_tracked_files "$target_dir" || true

    log "✅ .gitignore configured"
}

validate_gitignore_rules() {
    local target_dir="$1"
    local test_passed=true

    if ! (cd "$target_dir" && git rev-parse --git-dir >/dev/null 2>&1); then
        log "Not in a Git repository - skipping validation"
        return 0
    fi

    log "Testing .gitignore rules..."

    if (cd "$target_dir" && echo ".cursor/test_file" | git check-ignore --stdin >/dev/null 2>&1); then
        log "✓ .cursor/ exclusion rule working"
    else
        warn "✗ .cursor/ exclusion rule may not be working"
        test_passed=false
    fi

    if ! (cd "$target_dir" && echo ".cursor/memory-bank/context/test_file" | git check-ignore --stdin >/dev/null 2>&1); then
        log "✓ .cursor/memory-bank/context/ inclusion rule working"
    else
        warn "✗ .cursor/memory-bank/context/ inclusion rule may not be working"
        test_passed=false
    fi

    if ! (cd "$target_dir" && echo ".cursor/memory-bank/workflow/test_file" | git check-ignore --stdin >/dev/null 2>&1); then
        log "✓ .cursor/memory-bank/workflow/ inclusion rule working"
    else
        warn "✗ .cursor/memory-bank/workflow/ inclusion rule may not be working"
        test_passed=false
    fi

    if (cd "$target_dir" && echo ".cursor/other_dir/test_file" | git check-ignore --stdin >/dev/null 2>&1); then
        log "✓ Other .cursor/ subdirectories exclusion working"
    else
        warn "✗ Other .cursor/ subdirectories may not be properly excluded"
        test_passed=false
    fi

    if $test_passed; then
        return 0
    else
        warn "Some gitignore tests failed, but installation will continue"
        return 0
    fi
}

handle_tracked_files() {
    local target_dir="$1"

    if ! (cd "$target_dir" && git rev-parse --git-dir >/dev/null 2>&1); then
        log "Not in a Git repository - skipping tracked files cleanup"
        return 0
    fi

    log "Checking for .cursor files that are tracked but should now be ignored..."

    local tracked_files
    tracked_files=$(cd "$target_dir" && git ls-files '.cursor/*' 2>/dev/null | grep -v -E '^\.cursor/memory-bank/(context|workflow)/' | head -20)

    if [[ -n "$tracked_files" ]]; then
        warn "Found tracked files in .cursor that should now be ignored:"
        echo "$tracked_files" | while IFS= read -r file; do
            warn "  - $file"
        done
        warn ""
        warn "MANUAL ACTION REQUIRED:"
        warn "To remove these files from Git tracking (but keep them locally), run:"
        warn "  cd '$target_dir'"
        echo "$tracked_files" | while IFS= read -r file; do
            warn "  git rm --cached '$file'"
        done
        warn "  git commit -m '🔧 chore: Remove .cursor files from tracking (except memory-bank/context and memory-bank/workflow)'"
        warn ""
        warn "⚠️ CAUTION: Review the files before running git rm --cached to ensure no important data is lost"
    else
        log "✅ No problematic tracked files found in .cursor directory"
    fi
}

# ============================================================================
# MAIN INSTALLATION FUNCTIONS
# ============================================================================

install_commands() {
    local target_dir="$1"
    local temp_dir="$2"
    
    log "Installing custom commands..."
    mkdir -p "$target_dir/.cursor/commands"

    local commands_list=""
    
    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        warn "Using curl mode - installing only basic commands (subdirectories not supported with curl)"
        commands_list=".cursor/commands/prompt.md"
    else
        local clone_dir="$temp_dir/repo"
        if [[ ! -d "$clone_dir" ]]; then
            log "Cloning repository for command discovery..."
            clone_repository "$REPO_URL" "$clone_dir"
        fi
        if [[ -d "$clone_dir/.cursor/commands" ]]; then
            commands_list=$(cd "$clone_dir/.cursor/commands" && find . -type f -name "*.md" | sed 's|^\./|.cursor/commands/|')
            log "Discovered commands recursively: $(echo "$commands_list" | wc -w) files"
        else
            warn "Git clone failed - using conservative fallback set"
            commands_list=".cursor/commands/prompt.md"
        fi
    fi

    for c in $commands_list; do
        if [[ "$c" != .cursor/commands/* ]]; then
            continue
        fi
        local dest="$target_dir/$c"
        log "Installing command: $c"
        ensure_rule_file "$c" "$dest"
    done

    log "✓ Commands installed successfully"
}

install_basic_rules() {
    local target_dir="$1"
    local temp_dir="$2"
    
    log "Installing basic rules and utilities (single mode)..."
    mkdir -p "$target_dir/.cursor/rules"

    local full_install_only_rules=("start.mdc")
    local rules_list=""

    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        warn "Using curl mode - installing only basic rules (subdirectories not supported with curl)"
        rules_list=".cursor/rules/agent.mdc .cursor/rules/debug.mdc .cursor/rules/README.mdc"
    else
        local clone_dir="$temp_dir/repo"
        if [[ ! -d "$clone_dir" ]]; then
            log "Cloning repository for rule discovery..."
            clone_repository "$REPO_URL" "$clone_dir"
        fi
        if [[ -d "$clone_dir/.cursor/rules" ]]; then
            rules_list=$(cd "$clone_dir/.cursor/rules" && find . -type f -name "*.mdc" | sed 's|^\./|.cursor/rules/|')
            log "Discovered rules recursively: $(echo "$rules_list" | wc -w) files"
        else
            warn "Git clone failed - using conservative fallback set"
            rules_list=".cursor/rules/agent.mdc .cursor/rules/debug.mdc .cursor/rules/README.mdc"
        fi
    fi

    for r in $rules_list; do
        if [[ "$r" != .cursor/rules/* ]]; then
            continue
        fi
        local rule_filename=$(basename "$r")
        if is_in_array "$rule_filename" "${full_install_only_rules[@]}"; then
            log "Skipping full-install-only rule (not used in single mode): $r"
            continue
        fi
        local dest="$target_dir/$r"
        log "Installing rule: $r"
        ensure_rule_file "$r" "$dest"
    done

    log "Installing custom commands..."
    install_commands "$target_dir" "$temp_dir"

    log "Updating .gitignore"
    manage_gitignore "$target_dir"

    log "✅ Installation completed (single mode)"
}

# ============================================================================
# COMMAND LINE & HELP FUNCTIONS
# ============================================================================

show_help() {
    cat << EOF
Cursor Memory Bank Installation Script v${VERSION}

Usage: $0 [options]

Options:
    -h, --help         Show this help message
    -v, --version      Show version information
    -d, --dir DIR      Install to a specific directory (default: current directory)
    --force            Force installation even if directory is not empty

This script will:
1. Install agent rules and custom commands
2. Update .gitignore
3. Clean up temporary files

For more information, visit: ${REPO_URL}
EOF
    exit 0
}

show_version() {
    local commit_date
    if [[ -d "$TEMP_DIR" ]]; then
        commit_date=$(get_last_commit_date "curl" "short")
    else
        mkdir -p "$TEMP_DIR" || error "Failed to create temporary directory"
        commit_date=$(get_last_commit_date "curl" "short")
    fi
    echo "Cursor Memory Bank Installation Script v${VERSION} ($commit_date)"
    exit 0
}

# Parse command line arguments
INSTALL_DIR="."
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

# Single-mode installation
install_basic_rules "$INSTALL_DIR" "$TEMP_DIR"
log "Installation completed successfully!"
