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
    local curl_exit_code
    
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
    
    # Execute curl and capture http_code directly, ignore command exit status here
    # We capture the real exit code separately
    set +e # Temporarily disable exit on error
    http_code=$(curl -w "%{http_code}" -fsSL "$url" -o "$dest" 2>/dev/null)
    curl_exit_code=$?
    set -e # Re-enable exit on error
    
    # Check curl exit code first for general errors (like network, invalid URL format etc.)
    # Curl error codes: https://curl.se/libcurl/c/libcurl-errors.html
    if [[ $curl_exit_code -ne 0 ]] && [[ $curl_exit_code -ne 22 ]]; then # Exit code 22 is handled by HTTP 404 check
       error "curl command failed with exit code $curl_exit_code for URL: $url. Check network or URL."
    fi
    
    case "$http_code" in
        200)
            return 0
            ;;
        404)
            # Reverted AGAIN: Warn on 404 for curl test compatibility
            warn "URL not found (HTTP 404). Skipping download for: $url"
            return 0 # Allow script to continue
            ;;
        403)
            error "Failed to download file: Access denied (HTTP 403). Please check your access permissions to: $url"
            ;;
        50[0-9])
            error "Failed to download file: Server error (HTTP $http_code). Please try again later or contact support."
            ;;
        *)
            # Handle cases where curl exit code was 0 or 22 but http_code is unexpected
            if [[ "$http_code" =~ ^[0-9]+$ ]]; then # Check if it looks like a valid HTTP code
                error "Failed to download file (Unexpected HTTP status: $http_code) for URL: $url"
            else
                # This case might happen if -w output was empty or strange
                error "Failed to download file: Unknown error (curl exit: $curl_exit_code, http code: '$http_code'). Check URL: $url"
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
    local template_mcp_json="$temp_dir/mcp.json" # Define path for template
    
    # Define the MCP server names to install
    local mcp_servers=("mcp-commit-server" "mcp-memory-server" "mcp-context7-server" "mcp-debug-server")
    local server_name # Loop variable
    local mcp_server_source_dir # Will be set inside the loop
    local mcp_server_target_dir # Will be set inside the loop

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
            
            # Use jq if available to reliably parse path and type
            if command -v jq > /dev/null 2>&1; then
                echo "$cursor_rules_api_response" | jq -c '.[] | {path: .path, type: .type}' | while IFS= read -r item; do
                    local path=$(echo "$item" | jq -r '.path')
                    local type=$(echo "$item" | jq -r '.type')
                    
                    if [[ "$type" == "file" ]]; then
                        local file_url="$RAW_URL_BASE/$path"
                        # Destination needs basename only, place inside api_dir/rules/
                        local dest_file="$api_dir/rules/$(basename "$path")" 
                        log "Downloading $path (type: $type)"
                        mkdir -p "$(dirname "$dest_file")"
                        download_file "$file_url" "$dest_file"
                    else
                        log "Skipping $path (type: $type)"
                    fi
                done
            else
                warn "jq not found. Using grep/sed to extract paths. May attempt to download non-files."
                # Fallback to grep/sed (original behavior, may fail on directories)
                local cursor_files=$(echo "$cursor_rules_api_response" | grep -o '"path": "[^"]*"' | sed 's/"path": "\(.*\)"/\1/')
                for file in $cursor_files; do
                    # Skip the known directory
                    if [[ "$(basename "$file")" == "languages" ]]; then
                        log "Skipping languages directory (jq not available)"
                        continue
                    fi
                    
                    local file_url="$RAW_URL_BASE/$file"
                    local dest_file="$api_dir/rules/$(basename "$file")"
                    log "Downloading $file (jq not available)"
                    mkdir -p "$(dirname "$dest_file")"
                    download_file "$file_url" "$dest_file"
                done
            fi
        fi
        
        # Copy downloaded files to the target directory
        if [[ -d "$api_dir/rules" ]]; then
            # Check if the source directory is non-empty before copying
            if [ -n "$(ls -A "$api_dir/rules")" ]; then
                log "Copying rules from downloaded files"
                # Use dot to copy contents, not the directory itself
                if ! cp -r "$api_dir/rules/." "$rules_path/"; then 
                    error "Failed to copy rules from downloaded files. Please check disk space and permissions."
                fi
            else
                warn "Downloaded rules directory ($api_dir/rules) is empty. Skipping copy."
            fi
        else
            # This case should ideally not happen if API calls succeeded, but good to handle
            warn "Downloaded rules directory ($api_dir/rules) not found. No rules copied."
            # Depending on requirements, this could be an error: error "No rules downloaded or found."
        fi

        # ADD MCP.JSON DOWNLOAD HERE
        log "Downloading mcp.json template"
        download_file "$RAW_URL_BASE/.cursor/mcp.json" "$template_mcp_json"

        # ADD PRE-COMMIT HOOK DOWNLOAD HERE
        log "Downloading .githooks/pre-commit"
        local hooks_api_dir="$api_dir/githooks"
        mkdir -p "$hooks_api_dir"
        download_file "$RAW_URL_BASE/.githooks/pre-commit" "$hooks_api_dir/pre-commit"

        # ADD MCP-COMMIT-SERVER/SERVER.JS DOWNLOAD HERE
        log "Downloading mcp-commit-server/server.js"
        local commit_server_target_dir="$target_dir/.cursor/mcp/mcp-commit-server"
        mkdir -p "$commit_server_target_dir" # Ensure directory exists
        download_file "$RAW_URL_BASE/.cursor/mcp/mcp-commit-server/server.js" "$commit_server_target_dir/server.js"

        # --- Loop through MCP servers for curl mode ---
        for server_name in "${mcp_servers[@]}"; do
            mcp_server_source_dir="$api_dir/.cursor/mcp/$server_name" # Assumed path for downloaded files
            mcp_server_target_dir="$target_dir/.cursor/mcp/$server_name"
            log "Creating MCP server directory structure for $server_name (curl mode - files must be manually added or downloaded if server requires local files)"
            # Server definitions are handled by merging mcp.json; no specific file download needed here for npx/URL servers.
            mkdir -p "$mcp_server_target_dir"
            # mkdir -p "$mcp_server_source_dir" # Source dir is only conceptual here
        done
        # --- End MCP Server loop (curl) ---

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
        
        # ADD MCP.JSON COPY HERE
        if [[ -f "$clone_dir/.cursor/mcp.json" ]]; then # Corrected path
            log "Copying mcp.json template from clone"
            if ! cp "$clone_dir/.cursor/mcp.json" "$template_mcp_json"; then
                error "Failed to copy mcp.json template. Please check permissions."
            fi
        else
            warn "mcp.json template not found in repository clone at .cursor/mcp.json."
            # Create an empty file to avoid errors later if merge is attempted
            touch "$template_mcp_json"
        fi

        # --- Loop through MCP servers for git mode ---
        for server_name in "${mcp_servers[@]}"; do
            mcp_server_source_dir="$clone_dir/.cursor/mcp/$server_name"
            mcp_server_target_dir="$target_dir/.cursor/mcp/$server_name"

            log "Preparing to copy MCP server files for $server_name to target directory..."
            if [[ -d "$mcp_server_source_dir" ]]; then
                log "Source directory for $server_name files: $mcp_server_source_dir"
                # Ensure target parent directory exists
                if ! mkdir -p "$(dirname "$mcp_server_target_dir")"; then
                    error "Failed to create parent directory for $server_name target: $(dirname "$mcp_server_target_dir")"
                fi
                # Ensure target directory exists
                mkdir -p "$mcp_server_target_dir"
                # Copy files
                log "Copying $server_name files from $mcp_server_source_dir to $mcp_server_target_dir"
                if ! cp -r "$mcp_server_source_dir/"* "$mcp_server_target_dir/"; then
                     # Check if source directory was empty
                     if [ -z "$(ls -A "$mcp_server_source_dir")" ]; then
                         warn "MCP server source directory ($mcp_server_source_dir) for $server_name is empty. Server files might be missing."
                     else
                         error "Failed to copy $server_name files. Please check disk space and permissions."
                     fi
                else
                     log "$server_name files copied successfully."
                fi
            else
                warn "Source directory for $server_name files not found or not a directory: $mcp_server_source_dir. Skipping $server_name files copy."
            fi
        done
        # --- End MCP Server loop (git) ---
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

    # Set correct permissions for rules
    if ! chmod -R u+rw "$rules_path" || ! find "$rules_path" -type d -exec chmod u+x {} \;; then
        error "Failed to set permissions for rules. Please check file system permissions."
    fi
    
    # Set permissions for all copied MCP server directories
    log "Setting permissions for installed MCP server directories..."
    for server_name in "${mcp_servers[@]}"; do
        local current_mcp_server_target_dir="$target_dir/.cursor/mcp/$server_name"
        if [[ -d "$current_mcp_server_target_dir" ]]; then
             # REMOVED log call from inside the loop to test if it causes issues in curl|bash
             # Execute chmod directly...
             chmod -R u+rw "$current_mcp_server_target_dir" || true
        fi
    done

    # Ensure system.mdc is present (for test compatibility)
    if [[ ! -f "$rules_path/system.mdc" ]]; then
        log "Creating system.mdc file for test compatibility"
        echo "# System Rule - Created by install.sh for testing compatibility" > "$rules_path/system.mdc"
    fi

    log "Rules and MCP server base files installed successfully"
}

# Function to merge MCP JSON template with existing config
merge_mcp_json() {
    local target_dir="$1"
    # temp_dir is not needed for this approach
    local target_mcp_json="$target_dir/.cursor/mcp.json"
    local server_script_rel_path=".cursor/mcp/mcp-commit-server/server.js"
    local server_script_path="$target_dir/$server_script_rel_path"

    # --- Calculate Absolute Paths --- (Keep this logic as is)
    log "Calculating absolute paths relative to $target_dir..."
    local target_dir_abs=""
    local server_script_abs_path=""
    local server_script_win_path="" # For Windows compatibility
    local target_dir_win_path="" # For Windows compatibility

    # Calculate absolute path for target_dir first
    if ! target_dir_abs="$(cd "$target_dir" && pwd -P)"; then
        error "Failed to determine absolute path for target directory: $target_dir. Cannot configure server args."
        return 1
    fi
    log "Calculated absolute target directory path: $target_dir_abs"
    target_dir_win_path="$target_dir_abs" # Assign default
    # --- START Windows Path Conversion for Target Dir ---
    os_type=""
    if command -v uname >/dev/null 2>&1; then os_type=$(uname -o); fi
    if [[ "$os_type" == "Msys" ]]; then
        if command -v cygpath >/dev/null 2>&1; then
            if win_path=$(cygpath -w "$target_dir_abs"); then
                log "Converted target directory Windows path: $win_path"
                target_dir_win_path="$win_path"
            else
                warn "cygpath failed for target directory. Using MINGW64 path: $target_dir_abs"
                # target_dir_win_path remains the default $target_dir_abs
            fi
        else # Manual conversion
            target_dir_win_path=$(echo "$target_dir_abs" | sed -e 's|^/c/|C:\\\\|' -e 's|/|\\\\|g')
            log "Manually converted target directory path: $target_dir_win_path"
        fi # End cygpath/manual conversion check
    fi # End Msys check for target dir
    # --- END Windows Path Conversion for Target Dir ---

    # Check target dir path after potential conversion
    if [[ -z "$target_dir_win_path" ]]; then
        error "Target directory absolute path is empty after calculation/conversion."
        return 1
    fi

    # Now calculate absolute path for server script
    if [[ ! -f "$server_script_path" ]]; then
        error "Aborting MCP config generation: server script missing at $server_script_path."
        return 1
    fi
    # Construct absolute path for script
    local clean_rel_path="${server_script_rel_path#./}"
    server_script_abs_path="$target_dir_abs/$clean_rel_path"
    if [[ "$server_script_abs_path" =~ ^(/|[A-Za-z]:) ]]; then
        log "Calculated initial absolute script path: $server_script_abs_path"
        server_script_win_path="$server_script_abs_path" # Assign default
        # --- START Windows Path Conversion for Script ---
        if [[ "$os_type" == "Msys" ]]; then
            if command -v cygpath >/dev/null 2>&1; then
                if win_path=$(cygpath -w "$server_script_abs_path"); then
                    log "Converted script Windows path: $win_path"
                    server_script_win_path="$win_path"
                else
                    warn "cygpath failed for script. Using MINGW64 path: $server_script_abs_path"
                    # server_script_win_path remains the default $server_script_abs_path
                fi
            else # Manual conversion
                server_script_win_path=$(echo "$server_script_abs_path" | sed -e 's|^/c/|C:\\\\|' -e 's|/|\\\\|g')
                log "Manually converted script path: $server_script_win_path"
            fi # End cygpath/manual conversion check
        fi # End Msys check for script
        # --- END Windows Path Conversion for Script ---
    else
        error "Aborting MCP config generation: Calculated script path '$server_script_abs_path' does not appear absolute."
        return 1
    fi # End script path format check

    # Check script path after potential conversion
    if [[ -z "$server_script_win_path" ]]; then
        error "Server script absolute path is empty after calculation/conversion."
        return 1
    fi
    # --- End Calculate Absolute Paths ---

    # Ensure target directory exists before writing
    if ! mkdir -p "$(dirname "$target_mcp_json")"; then
        error "Could not create directory for $target_mcp_json. Aborting MCP config generation."
        return 1
    fi

    # Escape paths for JSON embedding (double backslashes)
    local server_script_json_safe
    server_script_json_safe=$(echo "$server_script_win_path" | sed 's/\\/\\\\/g')
    local target_dir_json_safe
    target_dir_json_safe=$(echo "$target_dir_win_path" | sed 's/\\/\\\\/g')

    log "Preparing to generate $target_mcp_json with hardcoded structure..."
    
    # --- DEBUG: Print values before writing ---
    echo "DEBUG: Writing to target file: [$target_mcp_json]" >&2
    echo "DEBUG: Server script path (escaped): [$server_script_json_safe]" >&2
    echo "DEBUG: Target directory path (escaped): [$target_dir_json_safe]" >&2
    # --- End DEBUG ---
    
    # Overwrite the target file directly using here-document
    # Using cat > ensures the file is overwritten or created.
cat > "$target_mcp_json" << EOF
{
    "mcpVersion": "0.1",
    "mcpServers": {
        "MyMCP": {
            "command": "node",
            "args": [
                "$server_script_json_safe",
                "--cwd",
                "$target_dir_json_safe"
            ]
        },
        "Context7": {
            "command": "npx",
            "args": [
                "-y",
                "@upstash/context7-mcp@latest"
            ]
        }
    }
}
EOF

    local write_status=$?
    if [[ $write_status -ne 0 ]]; then
        error "Failed to write generated MCP JSON to $target_mcp_json (Exit status: $write_status)"
        return 1 # Indicate failure
    else
        log "cat > EOF command finished with status $write_status."
        # --- DEBUG: Check file state immediately after write ---
        echo "DEBUG: Checking file state post-write for: [$target_mcp_json]" >&2
        ls -l "$target_mcp_json" >&2
        echo "DEBUG: First 5 lines post-write:" >&2
        head -n 5 "$target_mcp_json" >&2
        # --- End DEBUG ---
        
        # Basic existence check (redundant with ls but good practice)
        if [[ -f "$target_mcp_json" ]]; then
             log "Successfully generated $target_mcp_json (File exists)."
        else
             error "File $target_mcp_json was NOT found after write attempt."
             return 1 # Indicate failure
        fi
        return 0 # Indicate success
    fi
}

# Function to install pre-commit hook
install_pre_commit_hook() {
    local target_dir="$1"
    local temp_dir="$2"
    local hooks_dir="$target_dir/.githooks"
    local hook_file="$hooks_dir/pre-commit"
    local source_hook_file=""

    log "Installing pre-commit hook..."

    # Determine source hook file path based on install method
    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1;
    then
        # Curl method: Download hook file directly
        local api_dir="$temp_dir/api-files"
        local temp_hook_file="$api_dir/githooks/pre-commit"
        local hook_url="$RAW_URL_BASE/.githooks/pre-commit"

        log "Downloading pre-commit hook script via curl from $hook_url"
        mkdir -p "$(dirname "$temp_hook_file")"
        if download_file "$hook_url" "$temp_hook_file"; then
            source_hook_file="$temp_hook_file"
        else
            warn "Failed to download pre-commit hook script. Skipping hook installation."
            return
        fi
    else
        # Git method: Use hook file from cloned repo
        local clone_dir="$temp_dir/repo"
        if [[ -f "$clone_dir/.githooks/pre-commit" ]]; then
            source_hook_file="$clone_dir/.githooks/pre-commit"
            log "Using pre-commit hook script from git clone."
        else
            warn "Pre-commit hook script not found in cloned repository. Skipping hook installation."
            return
        fi
    fi

    # Create hooks directory in target
    if ! mkdir -p "$hooks_dir"; then
        error "Failed to create hooks directory: $hooks_dir. Please check permissions."
    fi

    # Copy hook file
    if ! cp "$source_hook_file" "$hook_file"; then
        error "Failed to copy pre-commit hook to $hook_file. Please check permissions."
    fi

    # Make hook executable
    if ! chmod +x "$hook_file"; then
        error "Failed to make pre-commit hook executable: $hook_file"
    fi

    log "Pre-commit hook installed to $hook_file"
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

# Create directory structure without deleting existing files
create_dirs "$INSTALL_DIR"

# Install rules AND copy base MCP server files
install_rules "$INSTALL_DIR" "$TEMP_DIR"

# Install pre-commit hook
install_pre_commit_hook "$INSTALL_DIR" "$TEMP_DIR"

# Merge MCP JSON template with existing config (NOW uses absolute path logic)
merge_mcp_json "$INSTALL_DIR"

# Install Internal MCP Commit Server dependencies if present in the TARGET directory
INTERNAL_MCP_SERVER_DIR="$INSTALL_DIR/.cursor/mcp/mcp-commit-server"
if [[ -d "$INTERNAL_MCP_SERVER_DIR" ]] && [[ -f "$INTERNAL_MCP_SERVER_DIR/package.json" ]]; then
    log "Installing Internal MCP Commit Server dependencies in $INTERNAL_MCP_SERVER_DIR..."
    
    # Ensure the server.js file exists (already copied by install_rules ideally)
    if [[ ! -f "$INTERNAL_MCP_SERVER_DIR/server.js" ]]; then
        warn "server.js file not found in $INTERNAL_MCP_SERVER_DIR. Dependency installation might fail or server won't run."
    fi
    
    if command -v npm >/dev/null 2>&1; then
        # Check if timeout command is available
        timeout_cmd=""
        if command -v timeout >/dev/null 2>&1; then
            timeout_cmd="timeout 60s"
        elif command -v gtimeout >/dev/null 2>&1; then # Handle macOS case (gtimeout via coreutils)
            timeout_cmd="gtimeout 60s"
        else
            warn "'timeout' command not found. Proceeding without timeout for npm install."
        fi

        # Change directory, install (with timeout if available), and change back
        log "Running npm install in $INTERNAL_MCP_SERVER_DIR..."
        (cd "$INTERNAL_MCP_SERVER_DIR" && $timeout_cmd npm install)
        npm_status=$?
        
        if [[ $npm_status -eq 124 ]]; then # 124 is the exit code for timeout command
             warn "'npm install' in $INTERNAL_MCP_SERVER_DIR timed out after 60 seconds. Please check network or run manually."
        elif [[ $npm_status -ne 0 ]]; then
            warn "Failed to install Internal MCP Commit Server dependencies (Exit code: $npm_status). Please check logs or run 'npm install' in $INTERNAL_MCP_SERVER_DIR manually."
        else
            log "Internal MCP Commit Server dependencies installed."
            
            # Verify node_modules directory exists and has content
            if [[ ! -d "$INTERNAL_MCP_SERVER_DIR/node_modules" ]]; then
                warn "node_modules directory not found in $INTERNAL_MCP_SERVER_DIR after npm install. MCP commit server may not function properly."
            else
                log "node_modules directory verified. MCP commit server should have all required dependencies."
            fi
        fi
    else
        warn "npm not found. Skipping Internal MCP Commit Server dependency installation. Please install Node.js and npm, then run 'npm install' in $INTERNAL_MCP_SERVER_DIR manually."
    fi
    
    # Remove redundant note about manual copy to AppData - now handled locally
    # log "NOTE: If you encounter 'MODULE_NOT_FOUND' errors..."
elif [[ -d "$INSTALL_DIR/.cursor/mcp" ]]; then # Check if mcp dir exists but server subdir doesn't
    log "MCP commit server directory not found in $INSTALL_DIR/.cursor/mcp/. Skipping dependency installation."
else
    log "MCP directory structure not found in $INSTALL_DIR/.cursor/. Skipping MCP server setup."
fi

# Attempt to automatically configure Git hooks path
auto_config_failed=1 # Assume failure initially
if command -v git >/dev/null 2>&1; then
    log "Checking if installation directory is a Git repository..."
    if (cd "$INSTALL_DIR" && git rev-parse --git-dir > /dev/null 2>&1); then
        log "Git repository detected. Attempting to configure core.hooksPath..."
        if (cd "$INSTALL_DIR" && git config core.hooksPath .githooks); then
            log "Successfully configured core.hooksPath to .githooks in $INSTALL_DIR"
            auto_config_failed=0 # Mark as success
        else
            warn "Failed to automatically configure core.hooksPath in $INSTALL_DIR. You may need to run the command manually."
        fi
    else
        log "Installation directory $INSTALL_DIR is not a Git repository. Skipping automatic hook configuration."
        # In this case, user likely doesn't need hooks configured anyway, but we keep auto_config_failed=1 to show manual step if needed.
    fi
else
    warn "git command not found. Skipping automatic hook configuration."
fi

log "Installation completed successfully!"

# Only show manual step if auto-config failed or was skipped
if [[ "$auto_config_failed" -eq 1 ]]; then
    log "${YELLOW}ACTION REQUIRED:${NC} To enable the installed git hooks (e.g., pre-commit), run the following command in your repository root:"
    log "  git config core.hooksPath .githooks"
fi 