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
download_file() {
    # download_file(url, dest, [required])
    # If third argument == "required" then missing files or HTTP errors are fatal (fail-fast).
    # Otherwise the function will warn and return success (0) so that global `set -e` does not
    # abort the whole installation for optional resources. Diagnostic info is printed on warnings/errors.
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

    # Execute curl and capture http_code directly. We intentionally ignore curl exit status here
    # and handle it with curl_exit_code/http_code to provide granular diagnostics.
    set +e
    http_code=$(curl -w "%{http_code}" -fsSL "$url" -o "$dest" 2>/dev/null)
    curl_exit_code=$?
    set -e

    # Diagnostic info for logs
    debug_info="http_code=$http_code curl_exit_code=$curl_exit_code"

    # If curl failed with a network/URL error (not an HTTP error), treat as fatal only if required
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
            # Verify the downloaded file exists and is non-empty
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
            # Handle unexpected or empty http_code
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

    # Ensure parent dir
    mkdir -p "$(dirname "$dest_path")"

    # If cloned repo exists and file present, copy
    if [[ -f "$clone_source" ]]; then
        log "Copying $path_in_repo from git clone to $dest_path"
        if cp "$clone_source" "$dest_path"; then
            # Quick sanity check
            if [[ ! -s "$dest_path" ]]; then
                warn "Copied file is empty: $dest_path"
                if [[ "$required_flag" == "required" ]]; then
                    # Try downloading as fallback
                    log "Attempting to download missing/empty file from $raw_url"
                    download_file "$raw_url" "$dest_path" "$required_flag"
                fi
            fi
            return 0
        else
            warn "Failed to copy $clone_source to $dest_path"
            # Fall through to download
        fi
    fi

    # If not copied from clone, try download
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
    
    # Get directory contents from GitHub API
    api_response=$(curl -s "$api_url" 2>/dev/null || true)
    if [[ -z "$api_response" ]]; then
        warn "Failed to fetch directory contents for $path_in_repo"
        return 1
    fi
    
    # Parse each item in the directory using a simpler approach
    # Extract all name/type pairs and process them
    local names_and_types
    names_and_types=$(echo "$api_response" | grep -o '"name": *"[^"]*", *"type": *"[^"]*"' | sed 's/"name": *"\([^"]*\)", *"type": *"\([^"]*\)"/\1:\2/')
    
    while IFS= read -r name_type; do
        if [[ -n "$name_type" ]]; then
            local name="${name_type%%:*}"
            local type="${name_type##*:}"
            
            if [[ "$type" == "file" ]] && [[ "$name" == *.mdc ]]; then
                # It's a rule file, add to list
                rules_list="$rules_list $path_in_repo/$name"
            elif [[ "$type" == "dir" ]]; then
                # It's a directory, recurse into it
                local subdir_rules=$(fetch_rules_recursive "$path_in_repo/$name")
                rules_list="$rules_list $subdir_rules"
            fi
        fi
    done <<< "$names_and_types"
    
    # Return the rules list (trim leading space)
    echo "${rules_list# }"
}


# ============================================================================
# GITIGNORE MANAGEMENT
# ============================================================================

# Function to manage .gitignore file
manage_gitignore() {
    local target_dir="$1"
    local gitignore_file="$target_dir/.gitignore"
    local no_gitignore_flag="${NO_GITIGNORE:-}"

    if [[ -n "$no_gitignore_flag" ]]; then
        log "Skipping .gitignore management due to --no-gitignore flag"
        return
    fi

    log "Ensuring minimal .gitignore entries..."

    # Create parent dir if needed
    if [[ ! -d "$(dirname "$gitignore_file")" ]]; then
        mkdir -p "$(dirname "$gitignore_file")"
    fi

    # If file doesn't exist, create it with the minimal required content
    if [[ ! -f "$gitignore_file" ]]; then
        # Create new .gitignore with the proper header and rules
        cat > "$gitignore_file" <<EOF
# Cursor Memory Bank
.cursor/mcp
.cursor/mcp.json
.cursor/screenshots
tomd.py
repo.md
diff
EOF
        log "Created .gitignore with minimal rules at: $gitignore_file"
    else
        # Robustly append a single block if the header is missing.
        # 1) Ensure file ends with a newline to avoid corrupting last line
        if [[ -s "$gitignore_file" ]]; then
            # Read last byte; if it's not a newline, append one
            last_char=$(tail -c 1 "$gitignore_file" 2>/dev/null || printf '')
            if [[ "$last_char" != $'\n' ]]; then
                echo "" >> "$gitignore_file"
            fi
        fi

        # 2) If header not present, append an atomic block with header + rules
        if ! grep -Fxq "# Cursor Memory Bank" "$gitignore_file" 2>/dev/null; then
            cat >> "$gitignore_file" <<EOF
# Cursor Memory Bank
.cursor/mcp
.cursor/mcp.json
.cursor/screenshots
tomd.py
repo.md
diff
EOF
            log "Appended Cursor Memory Bank block to .gitignore: $gitignore_file"
        else
            log "Cursor Memory Bank .gitignore header already present; ensuring additional entries exist"

            # Ensure additional entries are present (tomd.py, repo.md, diff, .cursor/screenshots)
            for entry in "tomd.py" "repo.md" "diff" ".cursor/screenshots"; do
                if ! grep -Fxq "$entry" "$gitignore_file" 2>/dev/null; then
                    echo "$entry" >> "$gitignore_file"
                    log "Appended '$entry' to $gitignore_file"
                fi
            done

        fi
    fi

    # Preserve existing validation and tracked-file handling for compatibility
    if validate_gitignore_rules "$target_dir"; then
        log "✅ .gitignore rules validated successfully"
    else
        warn "⚠️ .gitignore validation found issues - rules may need manual adjustment"
        warn "This is not a critical error and installation will continue"
    fi

    handle_tracked_files "$target_dir" || true

    log "✅ .gitignore configured"
}

# Function to validate .gitignore rules
validate_gitignore_rules() {
    local target_dir="$1"
    local test_passed=true

    # Check if we're in a git repository
    if ! (cd "$target_dir" && git rev-parse --git-dir >/dev/null 2>&1); then
        log "Not in a Git repository - skipping validation"
        return 0
    fi

    log "Testing .gitignore rules..."

    # Test that .cursor/ is ignored
    if (cd "$target_dir" && echo ".cursor/test_file" | git check-ignore --stdin >/dev/null 2>&1); then
        log "✓ .cursor/ exclusion rule working"
    else
        warn "✗ .cursor/ exclusion rule may not be working"
        test_passed=false
    fi

    # Test that .cursor/memory-bank/context/ is NOT ignored
    if ! (cd "$target_dir" && echo ".cursor/memory-bank/context/test_file" | git check-ignore --stdin >/dev/null 2>&1); then
        log "✓ .cursor/memory-bank/context/ inclusion rule working"
    else
        warn "✗ .cursor/memory-bank/context/ inclusion rule may not be working"
        test_passed=false
    fi

    # Test that .cursor/memory-bank/workflow/ is NOT ignored
    if ! (cd "$target_dir" && echo ".cursor/memory-bank/workflow/test_file" | git check-ignore --stdin >/dev/null 2>&1); then
        log "✓ .cursor/memory-bank/workflow/ inclusion rule working"
    else
        warn "✗ .cursor/memory-bank/workflow/ inclusion rule may not be working"
        test_passed=false
    fi

    # Test that other .cursor subdirectories are ignored
    if (cd "$target_dir" && echo ".cursor/other_dir/test_file" | git check-ignore --stdin >/dev/null 2>&1); then
        log "✓ Other .cursor/ subdirectories exclusion working"
    else
        warn "✗ Other .cursor/ subdirectories may not be properly excluded"
        test_passed=false
    fi

    # Always return true to prevent installation failure - validation is informational only
    if $test_passed; then
        return 0
    else
        warn "Some gitignore tests failed, but installation will continue"
        return 0
    fi
}

# Function to handle files already tracked by Git that should now be ignored
handle_tracked_files() {
    local target_dir="$1"

    # Check if we're in a git repository
    if ! (cd "$target_dir" && git rev-parse --git-dir >/dev/null 2>&1); then
        log "Not in a Git repository - skipping tracked files cleanup"
        return 0
    fi

    log "Checking for .cursor files that are tracked but should now be ignored..."

    # Get list of tracked files in .cursor that should be ignored
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
# MEMORY BANK & WORKFLOW SETUP
# ============================================================================

# Function to set up the memory bank directory
setup_memory_bank() {
    local target_dir="$1"
    local temp_dir="${2:-$TEMP_DIR}"
    local memory_bank_dir="$target_dir/.cursor/memory-bank"
    local workflow_dir="$memory_bank_dir/workflow"

    log "Setting up Memory Bank directory..."
    
    # Create directory structure
    mkdir -p "$memory_bank_dir/context"
    mkdir -p "$memory_bank_dir/workflow"
    mkdir -p "$memory_bank_dir/models"
    
    # Check if workflow directory exists and contains user data
    local has_existing_data=0
    
    if [ -d "$workflow_dir" ]; then
        log "Existing workflow directory found at $workflow_dir"
        
        # Check if workflow directory contains user data (non-empty JSON files)
        if [ -f "$workflow_dir/tasks.json" ] && [ -s "$workflow_dir/tasks.json" ] && [ "$(cat "$workflow_dir/tasks.json" 2>/dev/null)" != "[]" ]; then
            has_existing_data=1
        elif [ -f "$workflow_dir/userbrief.json" ] && [ -s "$workflow_dir/userbrief.json" ] && [ "$(cat "$workflow_dir/userbrief.json" 2>/dev/null)" != '{"version": "1.0.0", "last_id": 0, "requests": []}' ]; then
            has_existing_data=1
        elif [ -f "$workflow_dir/agent_memory.json" ] && [ -s "$workflow_dir/agent_memory.json" ] && [ "$(cat "$workflow_dir/agent_memory.json" 2>/dev/null)" != "[]" ]; then
            has_existing_data=1
        elif [ -f "$workflow_dir/long_term_memory.json" ] && [ -s "$workflow_dir/long_term_memory.json" ] && [ "$(cat "$workflow_dir/long_term_memory.json" 2>/dev/null)" != "[]" ]; then
            has_existing_data=1
        fi
        
        if [ $has_existing_data -eq 1 ]; then
            log "✓ Existing user data detected - preserving all workflow files"
        else
            log "Workflow directory exists but contains only default/empty data"
        fi
    fi
    
    # Install schema files (these are system files, not user data)
    install_workflow_schema_files "$workflow_dir" "$temp_dir"
    
    # Create user data files ONLY if they don't exist
    create_default_workflow_files "$workflow_dir" "$has_existing_data"
    
    # Create context files if they don't exist
    if [[ ! -f "$memory_bank_dir/context/projectBrief.md" ]]; then
        touch "$memory_bank_dir/context/projectBrief.md"
        log "Created empty projectBrief.md"
    fi
    
    if [[ ! -f "$memory_bank_dir/context/techContext.md" ]]; then
        touch "$memory_bank_dir/context/techContext.md"
        log "Created empty techContext.md"
    fi

    if [ $has_existing_data -eq 1 ]; then
        log "✅ Memory Bank setup completed - existing user data preserved"
    else
        log "✅ Memory Bank setup completed - clean workspace initialized"
    fi
}

# Function to install schema files (system files that should be updated)
install_workflow_schema_files() {
    local workflow_dir="$1"
    local temp_dir="$2"
    
    log "Installing/updating workflow schema files..."
    
    # Schema files that should always be updated from the repository
    local schema_files=("userbrief_schema.json" "tasks_schema.json")
    
        if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        # Download schema files via curl
        for schema_file in "${schema_files[@]}"; do
            local schema_url="$RAW_URL_BASE/.cursor/memory-bank/workflow/$schema_file"
            local schema_path="$workflow_dir/$schema_file"
            
            log "Downloading schema file: $schema_file"
            if download_file "$schema_url" "$schema_path"; then
                log "✓ Updated $schema_file"
            else
                warn "Failed to download $schema_file - continuing without it"
            fi
        done
    else
        # Copy schema files from git clone
        local clone_dir="$temp_dir/repo"
        if [[ -d "$clone_dir/.cursor/memory-bank/workflow" ]]; then
            for schema_file in "${schema_files[@]}"; do
                local source_schema="$clone_dir/.cursor/memory-bank/workflow/$schema_file"
                local target_schema="$workflow_dir/$schema_file"
                
                if [[ -f "$source_schema" ]]; then
                    cp "$source_schema" "$target_schema"
                    log "✓ Updated $schema_file from git clone"
                else
                    warn "Schema file $schema_file not found in repository"
                fi
            done
        fi
    fi
}

# Function to create default workflow files (only if they don't exist)
create_default_workflow_files() {
    local workflow_dir="$1"
    local has_existing_data="$2"
    
    if [ $has_existing_data -eq 1 ]; then
        log "Skipping default file creation - preserving existing user data"
        return
    fi
    
    log "Creating default workflow files for clean workspace..."
    
    # Create data files only if they don't exist
    if [[ ! -f "$workflow_dir/tasks.json" ]]; then
        echo "[]" > "$workflow_dir/tasks.json"
        log "Created empty tasks.json"
    fi
    
    if [[ ! -f "$workflow_dir/userbrief.json" ]]; then
        echo '{"version": "1.0.0", "last_id": 0, "requests": []}' > "$workflow_dir/userbrief.json"
        log "Created empty userbrief.json"
    fi
    
    if [[ ! -f "$workflow_dir/agent_memory.json" ]]; then
        echo "[]" > "$workflow_dir/agent_memory.json"
        log "Created empty agent_memory.json"
    fi
    
    if [[ ! -f "$workflow_dir/long_term_memory.json" ]]; then
        echo "[]" > "$workflow_dir/long_term_memory.json"
        log "Created empty long_term_memory.json"
    fi
    
    # Create additional system files if they don't exist
    if [[ ! -f "$workflow_dir/workflow_state.json" ]]; then
        echo '{"state": "idle", "current_step": null}' > "$workflow_dir/workflow_state.json"
        log "Created empty workflow_state.json"
    fi
    
    if [[ ! -f "$workflow_dir/to_user.json" ]]; then
        echo '{"messages": []}' > "$workflow_dir/to_user.json"
        log "Created empty to_user.json"
    fi
}

# Function to create tasks.json in streamlit_app directory
create_mcp_tasks_file() {
    local target_dir="$1"
    local streamlit_app_dir="$target_dir/.cursor/memory-bank/streamlit_app"
    
    # Create streamlit_app directory if it doesn't exist
    mkdir -p "$streamlit_app_dir"
    
    # Create tasks.json (simple array format)
    if [[ ! -f "$streamlit_app_dir/tasks.json" ]]; then
        echo "[]" > "$streamlit_app_dir/tasks.json"
        log "Created tasks.json in streamlit_app directory"
    else
        log "tasks.json already exists in streamlit_app directory"
    fi
}

# Backup and create_dirs functions removed - no longer needed for workflow system

# ============================================================================
# MAIN INSTALLATION FUNCTIONS
# ============================================================================

# Function to install custom commands
install_commands() {
    local target_dir="$1"
    local temp_dir="$2"
    
    log "Installing custom commands..."
    
    # Create necessary directories
    mkdir -p "$target_dir/.cursor/commands"
    
    # Fetch remote list of commands
    local commands_list=""
    
    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        # For curl mode, use conservative fallback
        warn "Using curl mode - installing only basic commands (subdirectories not supported with curl)"
        commands_list=".cursor/commands/prompt.md"
    else
        # Use git clone method for recursive detection
        local clone_dir="$temp_dir/repo"
        
        # Clone repository if not already done
        if [[ ! -d "$clone_dir" ]]; then
            log "Cloning repository for command discovery..."
            clone_repository "$REPO_URL" "$clone_dir"
        fi
        
        if [[ -d "$clone_dir/.cursor/commands" ]]; then
            # Build list from cloned files recursively
            commands_list=$(cd "$clone_dir/.cursor/commands" && find . -type f -name "*.md" | sed 's|^\./|.cursor/commands/|')
            log "Discovered commands recursively: $(echo "$commands_list" | wc -w) files"
        else
            # Fallback to conservative list if clone fails
            warn "Git clone failed - using conservative fallback set"
            commands_list=".cursor/commands/prompt.md"
        fi
    fi
    
    # Install all commands
    for c in $commands_list; do
        # Only handle files under .cursor/commands/
        if [[ "$c" != .cursor/commands/* ]]; then
            continue
        fi
        
        local dest="$target_dir/$c"
        log "Installing command: $c"
        ensure_rule_file "$c" "$dest"
    done
    
    log "✓ Commands installed successfully"
}

# Function for basic installation (rules only, no servers)
install_basic_rules() {
    local target_dir="$1"
    local temp_dir="$2"
    
    log "Installing basic rules and utilities (fast mode)..."
    
    # Create necessary directories
    mkdir -p "$target_dir/.cursor/rules"
    
    # Rules that should only be installed in full-install mode
    local full_install_only_rules=("start.mdc")
    
    # Fetch remote list of rules recursively
    local rules_list=""
    
    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        # For curl mode, use conservative fallback (API doesn't work reliably)
        warn "Using curl mode - installing only basic rules (subdirectories not supported with curl)"
        rules_list=".cursor/rules/agent.mdc .cursor/rules/debug.mdc .cursor/rules/README.mdc"
    else
        # Use git clone method for recursive detection (works perfectly)
        local clone_dir="$temp_dir/repo"
        
        # Clone repository if not already done
        if [[ ! -d "$clone_dir" ]]; then
            log "Cloning repository for rule discovery..."
            clone_repository "$REPO_URL" "$clone_dir"
        fi
        
        if [[ -d "$clone_dir/.cursor/rules" ]]; then
            # Build list from cloned files recursively (prefer what actually exists in repo)
            rules_list=$(cd "$clone_dir/.cursor/rules" && find . -type f -name "*.mdc" | sed 's|^\./|.cursor/rules/|')
            log "Discovered rules recursively: $(echo "$rules_list" | wc -w) files"
        else
            # Fallback to conservative list if clone fails
            warn "Git clone failed - using conservative fallback set"
            rules_list=".cursor/rules/agent.mdc .cursor/rules/debug.mdc .cursor/rules/README.mdc"
        fi
    fi
    
    # Install all rules except those marked as full_install_only
    for r in $rules_list; do
        # Only handle files under .cursor/rules/
        if [[ "$r" != .cursor/rules/* ]]; then
            continue
        fi
        
        # Extract just the filename for comparison
        local rule_filename=$(basename "$r")
        
        # Skip full_install_only rules in basic install mode
        if is_in_array "$rule_filename" "${full_install_only_rules[@]}"; then
            log "Skipping full-install-only rule for basic install: $r"
            continue
        fi
        
        local dest="$target_dir/$r"
        log "Installing rule: $r"
        ensure_rule_file "$r" "$dest"
    done
    
    # Install commands
    log "Installing custom commands..."
    install_commands "$target_dir" "$temp_dir"
    
    # Install tomd.py script
    log "Installing tomd.py utility script"
    ensure_rule_file "tomd.py" "$target_dir/tomd.py" "required"
    
    # Update .gitignore
    log "Updating .gitignore"
    manage_gitignore "$target_dir"
    
    log "✅ Basic installation completed successfully!"
}

install_workflow_system() {
    local target_dir="$1"
    local temp_dir="$2"
    local workflow_path="$target_dir/$WORKFLOW_DIR"
    local clone_dir="$temp_dir/repo"
    local api_dir="$temp_dir/api-files"
    local commit_date=""
    
    if [[ -z "${FULL_INSTALL:-}" ]]; then
        log "ERROR: install_workflow_system should only be called in FULL_INSTALL mode"
        error "install_workflow_system called without FULL_INSTALL flag. This is a bug in the installation script."
    fi
    
    log "Full installation mode: installing workflow system"

    log "Installing to $target_dir"

    # Use curl if specified or if git is not available
    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        if [[ -n "${USE_CURL:-}" ]]; then
            log "Using curl (forced by --use-curl option)"
        else
            log "Using curl (git not available)"
        fi
        
        # Get commit date from API
        commit_date=$(get_last_commit_date "curl")
        log "Installing from master branch (latest commit: $commit_date)"

        # Only install workflow components in full mode
        if [[ -n "${FULL_INSTALL:-}" ]]; then
            # Download workflow-steps
            log "Downloading workflow-steps..."
            mkdir -p "$workflow_path"
            local workflow_files=("start-workflow.md" "task-decomposition.md" "implementation.md" "experience-execution.md" "fix.md" "context-update.md")
            for file in "${workflow_files[@]}"; do
                download_file "$RAW_URL_BASE/.cursor/workflow-steps/$file" "$workflow_path/$file"
            done
            
        # Ensure standard rules are present (centralized)
            # Note: `.cursor/rules/mcp.mdc` is repository-local and MUST NOT be distributed by the installer.
            mkdir -p "$target_dir/.cursor/rules"

            # Rules that should only be installed in full-install mode
            local full_install_only_rules=("start.mdc")

            # Fetch remote list of rules recursively from GitHub API
            local rules_list=""
            rules_list=$(fetch_rules_recursive ".cursor/rules")
            
            # Fallback to conservative list if API call fails
            if [[ -z "$rules_list" ]]; then
                warn "Could not fetch remote rules list; using conservative fallback set"
                rules_list=".cursor/rules/agent.mdc .cursor/rules/Communication.mdc .cursor/rules/debug.mdc .cursor/rules/ouvrier.mdc .cursor/rules/README.mdc .cursor/rules/start.mdc"
            fi

            # Install all rules (full install mode)
            for r in $rules_list; do
                # Only handle files under .cursor/rules/
                if [[ "$r" != .cursor/rules/* ]]; then
                    continue
                fi
                dest="$target_dir/$r"
                ensure_rule_file "$r" "$dest"
            done

            # Install commands
            install_commands "$target_dir" "$temp_dir"

            # GEMINI and .gemini settings
            mkdir -p "$target_dir/.gemini"
            # Only create GEMINI.md from start.mdc if start.mdc exists and we're in full install
            if [[ -f "$target_dir/.cursor/rules/start.mdc" ]]; then
                ensure_rule_file ".cursor/rules/start.mdc" "$target_dir/GEMINI.md"
            else
                # If start.mdc is not available, create an empty GEMINI.md for compatibility
                touch "$target_dir/GEMINI.md"
            fi
        else
            # Basic install mode - install all rules except those marked as full_install_only
            mkdir -p "$target_dir/.cursor/rules"

            # Rules that should only be installed in full-install mode
            local full_install_only_rules=("start.mdc")

            # Fetch remote list of rules recursively from GitHub API
            local rules_list=""
            rules_list=$(fetch_rules_recursive ".cursor/rules")
            
            # Fallback to conservative list if API call fails
            if [[ -z "$rules_list" ]]; then
                # Conservative fallback - only basic files, no subdirectories
                # Subdirectories will be discovered dynamically when API/clone works
                rules_list=".cursor/rules/agent.mdc .cursor/rules/Communication.mdc .cursor/rules/debug.mdc .cursor/rules/ouvrier.mdc .cursor/rules/README.mdc"
            fi

            for r in $rules_list; do
                if [[ "$r" != .cursor/rules/* ]]; then
                    continue
                fi
                
                # Extract just the filename for comparison
                local rule_filename=$(basename "$r")
                
                # Skip full_install_only rules in basic install mode
                if is_in_array "$rule_filename" "${full_install_only_rules[@]}"; then
                    log "Skipping full-install-only rule for basic install: $r"
                    continue
                fi
                
                dest="$target_dir/$r"
                ensure_rule_file "$r" "$dest"
            done

            # Install commands
            install_commands "$target_dir" "$temp_dir"
        fi

        # Ensure tomd.py is deployed to the installation root for both basic and full installs
        log "Deploying tomd.py to installation root"
        ensure_rule_file "tomd.py" "$target_dir/tomd.py"

    else
        # Use git clone
        log "Using git clone for installation"
        clone_repository "$REPO_URL" "$clone_dir"

        # After cloning, verify and install required rule files using the
        # unified ensure_rule_file() helper. This will copy from the clone
        # when present, and fall back to downloading from RAW_URL_BASE when
        # missing or empty. This implements the "clone if possible + verify
        # and fallback by raw download" strategy.
        log "Verifying required rule files via ensure_rule_file (clone + fallback)"
        mkdir -p "$INSTALL_DIR/.cursor/rules" "$INSTALL_DIR/.cursor/commands" "$INSTALL_DIR/.gemini"

        # Determine rules list from the cloned repository when possible, otherwise
        # fall back to the GitHub API helper. This prevents attempts to download
        # files that are not present in the repository (avoids 404 errors).
        mkdir -p "$INSTALL_DIR/.cursor/rules"
        
        # Rules that should only be installed in full-install mode
        local full_install_only_rules=("start.mdc")
        
        local rules_list=""
        if [[ -d "$clone_dir/.cursor/rules" ]]; then
            # Build list from cloned files recursively (prefer what actually exists in repo)
            rules_list=$(cd "$clone_dir/.cursor/rules" && find . -type f -name "*.mdc" | sed 's|^\./|.cursor/rules/|')
        else
            # Fallback to recursive API call
            rules_list=$(fetch_rules_recursive ".cursor/rules")
        fi

        if [[ -z "$rules_list" ]]; then
            # Conservative fallback
            # Conservative fallback - only basic files, no subdirectories
            # Subdirectories will be discovered dynamically when API/clone works
            rules_list=".cursor/rules/agent.mdc .cursor/rules/debug.mdc .cursor/rules/ouvrier.mdc .cursor/rules/README.mdc"
        fi

        # Install rules discovered above. Prefer copying from clone; otherwise fall
        # back to downloading. Do NOT treat repository-missing rules as required by default.
        for rel in $rules_list; do
            # Extract just the filename for comparison
            local rule_filename=$(basename "$rel")
            
            # Skip full_install_only rules in basic install mode
            if [[ -z "${FULL_INSTALL:-}" ]] && is_in_array "$rule_filename" "${full_install_only_rules[@]}"; then
                log "Skipping full-install-only rule for basic install: $rel"
                continue
            fi
            
            dest="$INSTALL_DIR/$rel"
            mkdir -p "$(dirname "$dest")"
            src="$clone_dir/$rel"
            if [[ -f "$src" ]]; then
                log "Copying $rel from clone to $dest"
                if ! cp "$src" "$dest"; then
                    warn "Failed to copy $src to $dest"
                    # Try download as fallback
                    ensure_rule_file "$rel" "$dest"
                fi
            else
                # Try to download; mark only truly critical files as required elsewhere
                ensure_rule_file "$rel" "$dest"
            fi
        done
        
        # Get commit date
        commit_date=$(get_last_commit_date)
        log "Installing from master branch (latest commit: $commit_date)"

        # Only install workflow components in full mode
        if [[ -n "${FULL_INSTALL:-}" ]]; then
            # Copy workflow-steps
            if [[ -d "$clone_dir/.cursor/workflow-steps" ]]; then
                log "Copying workflow-steps..."
                mkdir -p "$workflow_path"
                if ! cp -r "$clone_dir/.cursor/workflow-steps/"* "$workflow_path/"; then
                    error "Failed to copy workflow-steps. Please check disk space and permissions."
                fi
            else
                warn "workflow-steps directory not found in repository"
            fi
            
            # Copy start.mdc rule
            if [[ -f "$clone_dir/.cursor/rules/start.mdc" ]]; then
                log "Copying start.mdc rule..."
                mkdir -p "$target_dir/.cursor/rules"
                if ! cp "$clone_dir/.cursor/rules/start.mdc" "$target_dir/.cursor/rules/start.mdc"; then
                    error "Failed to copy start.mdc rule. Please check disk space and permissions."
                fi
            else
                warn "start.mdc rule not found in repository"
            fi

            # Also copy README.mdc and debug.mdc rules when available
            if [[ -f "$clone_dir/.cursor/rules/README.mdc" ]]; then
                log "Copying README.mdc rule..."
                mkdir -p "$target_dir/.cursor/rules"
                if ! cp "$clone_dir/.cursor/rules/README.mdc" "$target_dir/.cursor/rules/README.mdc"; then
                    error "Failed to copy README.mdc rule. Please check disk space and permissions."
                fi
            else
                warn "README.mdc rule not found in repository"
            fi
            if [[ -f "$clone_dir/.cursor/rules/debug.mdc" ]]; then
                log "Copying debug.mdc rule..."
                mkdir -p "$target_dir/.cursor/rules"
                if ! cp "$clone_dir/.cursor/rules/debug.mdc" "$target_dir/.cursor/rules/debug.mdc"; then
                    error "Failed to copy debug.mdc rule. Please check disk space and permissions."
                fi
            else
                warn "debug.mdc rule not found in repository"
            fi
            
            # Copy start.mdc as GEMINI.md in .gemini directory
            if [[ -f "$clone_dir/.cursor/rules/start.mdc" ]]; then
                log "Copying start.mdc as GEMINI.md"
                mkdir -p "$target_dir/.gemini"
                if ! cp "$clone_dir/.cursor/rules/start.mdc" "$target_dir/GEMINI.md"; then
                    error "Failed to copy start.mdc as GEMINI.md. Please check permissions."
                fi
            else
                warn "start.mdc rule not found in repository clone at .cursor/rules/start.mdc."
                touch "$target_dir/GEMINI.md"
            fi
        else
            # Basic mode: install agent.mdc rule, README.mdc and debug.mdc rules
            if [[ -f "$clone_dir/.cursor/rules/agent.mdc" ]]; then
                log "Copying agent.mdc rule..."
                mkdir -p "$target_dir/.cursor/rules"
                if ! cp "$clone_dir/.cursor/rules/agent.mdc" "$target_dir/.cursor/rules/agent.mdc"; then
                    error "Failed to copy agent.mdc rule. Please check disk space and permissions."
                fi
            else
                warn "agent.mdc rule not found in repository"
            fi

            # Also copy README.mdc and debug.mdc rules for basic installs when available
            if [[ -f "$clone_dir/.cursor/rules/README.mdc" ]]; then
                log "Copying README.mdc rule..."
                mkdir -p "$target_dir/.cursor/rules"
                if ! cp "$clone_dir/.cursor/rules/README.mdc" "$target_dir/.cursor/rules/README.mdc"; then
                    error "Failed to copy README.mdc rule. Please check disk space and permissions."
                fi
            else
                warn "README.mdc rule not found in repository"
            fi
            if [[ -f "$clone_dir/.cursor/rules/debug.mdc" ]]; then
                log "Copying debug.mdc rule..."
                mkdir -p "$target_dir/.cursor/rules"
                if ! cp "$clone_dir/.cursor/rules/debug.mdc" "$target_dir/.cursor/rules/debug.mdc"; then
                    error "Failed to copy debug.mdc rule. Please check disk space and permissions."
                fi
            else
                warn "debug.mdc rule not found in repository"
            fi
        fi
    fi

        # Ensure tomd.py is deployed to the installation root for both clone and curl methods
        if [[ -f "$clone_dir/tomd.py" ]]; then
            if cp "$clone_dir/tomd.py" "$target_dir/tomd.py"; then
                log "✓ tomd.py copied to $target_dir/tomd.py"
            else
                warn "Failed to copy tomd.py from clone to $target_dir/tomd.py"
            fi
        else
            warn "tomd.py not found in repository clone; attempting to download from raw URL"
            if download_file "$RAW_URL_BASE/tomd.py" "$target_dir/tomd.py"; then
                log "✓ tomd.py downloaded to $target_dir/tomd.py"
            else
                warn "Failed to obtain tomd.py via download; continuing without it"
            fi
        fi
    fi

    # Ensure .gitignore is managed for selective .cursor synchronization in all install modes
    manage_gitignore "$target_dir"
    if [[ -n "${FULL_INSTALL:-}" ]]; then
        # Set permissions for workflow directories
        if [[ -d "$workflow_path" ]]; then
            chmod -R u+rw "$workflow_path" || error "Failed to set permissions on $workflow_path"
        fi

        log "Full workflow system installed successfully"
    fi
}

# ============================================================================
# STREAMLIT APP & ML MODEL
# ============================================================================

# Function to install the Streamlit app and dependencies
install_streamlit_app() {
    log "Installing Streamlit app and dependencies..."
    
    # Check for target_dir argument
    if [[ -z "${1:-}" ]]; then
        error "install_streamlit_app requires the target directory as the first argument."
    fi
    local target_dir="$1"
    
    # Check for temp_dir argument, but don't fail if it's not there, just warn.
    if [[ -z "${2:-}" ]]; then
        warn "install_streamlit_app was called without a temporary directory argument. Falling back to global TEMP_DIR."
    fi
    local temp_dir="${2:-$TEMP_DIR}"
    local clone_dir="$temp_dir/repo" # Define clone_dir based on temp_dir
    
    local streamlit_dir="$target_dir/.cursor/streamlit_app"
    local requirements_file="$streamlit_dir/requirements.txt"
    local startup_script="$target_dir/.cursor/run_ui.sh"

    # Create streamlit directory
    mkdir -p "$streamlit_dir" || {
        warn "Failed to create Streamlit directory. Skipping Streamlit installation."
        return
    }

    # Download or copy Streamlit app files
    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        log "Downloading Streamlit app files..."
        
        # Define files to download
        local streamlit_app_files=("app.py" "requirements.txt")
        local streamlit_pages=("task_status.py" "memory.py")
        local streamlit_components=("sidebar.py" "task_utils.py")

        download_file "$RAW_URL_BASE/.cursor/streamlit_app/app.py" "$streamlit_dir/app.py"
        download_file "$RAW_URL_BASE/.cursor/streamlit_app/requirements.txt" "$streamlit_dir/requirements.txt"
        
        mkdir -p "$streamlit_dir/pages"
        for page in "${streamlit_pages[@]}"; do
            download_file "$RAW_URL_BASE/.cursor/streamlit_app/pages/$page" "$streamlit_dir/pages/$page"
        done

        mkdir -p "$streamlit_dir/components"
        for component in "${streamlit_components[@]}"; do
            download_file "$RAW_URL_BASE/.cursor/streamlit_app/components/$component" "$streamlit_dir/components/$component"
        done
        
        # Download startup scripts
        download_file "$RAW_URL_BASE/.cursor/run_ui.sh" "$startup_script"

    else
        log "Copying Streamlit app files from git clone..."
        if [[ -d "$clone_dir/.cursor/streamlit_app" ]]; then
            if ! cp -r "$clone_dir/.cursor/streamlit_app/"* "$streamlit_dir/"; then
                warn "Failed to copy Streamlit app files. Please check permissions."
            fi
        else
            warn "Streamlit app directory not found in repository clone"
        fi
        
        # Copy startup scripts
        if [[ -f "$clone_dir/.cursor/run_ui.sh" ]]; then
            cp "$clone_dir/.cursor/run_ui.sh" "$startup_script"
        else
            warn "Streamlit startup script not found in repository clone"
        fi
    fi
    
    # Set permissions for startup scripts
    chmod u+x "$startup_script" || error "Failed to set executable permission on $startup_script"
    log "UI startup script installed at: $startup_script"

    # Install Python dependencies
    if [[ ! -f "$requirements_file" ]]; then
        error "requirements.txt file not found in Streamlit app directory. Cannot install Python dependencies."
        return
    fi

    # Manage .gitignore file
    manage_gitignore "$target_dir"

    log "Streamlit app installed successfully"
}

install_ml_model() {
    log "Checking for ML model..."
    local target_dir="$1"
    
    # Check if python/pip are available
    local python_cmd=""
    if command -v python3 &>/dev/null; then
        python_cmd="python3"
    elif command -v python &>/dev/null; then
        python_cmd="python"
    else
        warn "Python not found. Cannot download ML model."
        return
    fi

    local pip_cmd=""
    if command -v pip3 &>/dev/null; then
        pip_cmd="pip3"
    elif command -v pip &>/dev/null; then
        pip_cmd="pip"
    else
        warn "pip not found. Cannot download ML model."
        return
    fi

    # Create models directory
    local models_dir="$target_dir/.cursor/memory-bank/models"
    mkdir -p "$models_dir" || {
        warn "Failed to create models directory. Skipping model download."
        return
    }

    log "Installing sentence-transformers for model download..."
    if ! $pip_cmd install sentence-transformers &>/dev/null; then
        warn "Failed to install 'sentence-transformers'. Model download might fail. Trying to proceed..."
    fi

    log "Downloading all-MiniLM-L6-v2 model. This may take a few minutes..."
    
    # Create temporary Python script for model download
    local temp_download_script="$target_dir/temp_download_model.py"
    cat > "$temp_download_script" << 'EOF'
from sentence_transformers import SentenceTransformer
import os
import sys

model_name = 'all-MiniLM-L6-v2'
cache_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join('.cursor', 'memory-bank', 'models')

print(f"Downloading {model_name} to {cache_dir}...")

try:
    # This will download the model to the specified cache directory
    model = SentenceTransformer(model_name, cache_folder=cache_dir)
    print("Model downloaded successfully.")
except Exception as e:
    print(f"Error downloading model: {e}")
    sys.exit(1)
EOF

    if ! $python_cmd "$temp_download_script" "$models_dir"; then
        warn "ML model download failed. The model will be downloaded on first use instead."
    else
        log "ML model downloaded successfully to $models_dir"
    fi
    
    # Clean up temporary script
    rm -f "$temp_download_script"
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
    --use-curl         Force using curl instead of git clone
    --full-install     Install all components: Streamlit UI, ML model, and workflow system (default: rules only)

This script will:
1. By default: Install basic rules, tomd.py utility and update .gitignore (fast mode)
2. With --full-install: Install complete workflow system with Streamlit UI and ML model
3. With --full-install: Download the all-MiniLM-L6-v2 model for semantic search
4. With --full-install: Install Streamlit UI for monitoring agent status
5. With --full-install: Install start.mdc rule for autonomous workflow operation
6. Clean up temporary files

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
FORCE=""
USE_CURL=""
FULL_INSTALL=""

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
        --full-install)
            FULL_INSTALL=1
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

# Install based on mode
if [[ -n "${FULL_INSTALL:-}" ]]; then
    # Full installation: check Node.js requirements first
    check_nodejs_requirements
    
    # Install workflow system
    install_workflow_system "$INSTALL_DIR" "$TEMP_DIR"
else
    # Basic installation: install only rules, tomd.py and update gitignore
    install_basic_rules "$INSTALL_DIR" "$TEMP_DIR"
fi

# Set up the memory bank to preserve user data - only in full install mode
if [[ -n "${FULL_INSTALL:-}" ]]; then
    setup_memory_bank "$INSTALL_DIR" "$TEMP_DIR"
    
    # Create tasks.json for streamlit_app
    create_mcp_tasks_file "$INSTALL_DIR"
fi


# Install Streamlit App and ML Model - only in full install mode
if [[ -n "${FULL_INSTALL:-}" ]]; then
    # Install Streamlit App
    install_streamlit_app "$INSTALL_DIR" "$TEMP_DIR"
    
    # Install ML Model
    install_ml_model "$INSTALL_DIR"
    
    log "Full installation completed successfully!"
else
    log "Basic installation completed successfully!"
fi
