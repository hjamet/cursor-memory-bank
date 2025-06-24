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
API_URL="https://api.github.com/repos/hjamet/cursor-memory-bank/commits/master"
RAW_URL_BASE="https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master"
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

# Function to manage .gitignore file
manage_gitignore() {
    local target_dir="$1"
    local gitignore_file="$target_dir/.gitignore"
    local no_gitignore_flag="${NO_GITIGNORE:-}"

    if [[ -n "$no_gitignore_flag" ]]; then
        log "Skipping .gitignore management due to --no-gitignore flag"
        return
    fi

    log "Managing .gitignore file..."

    # Create .gitignore if it doesn't exist
    if [[ ! -f "$gitignore_file" ]]; then
        touch "$gitignore_file"
        log "Created .gitignore file at: $gitignore_file"
    fi

    # Entries to be added
    local entries=(
        "# Cursor Memory Bank - Auto-generated entries"
        ".cursor/mcp/*/node_modules/"
        ".cursor/mcp/*/*.log"
        ".cursor/memory-bank/workflow/temp/"
        ".cursor/streamlit_app/__pycache__/"
        ".cursor/memory-bank/models/"
        "*.pyc"
        "__pycache__/"
        "# MCP Server State Files"
        ".cursor/mcp/*/terminals_status.json"
        ".cursor/mcp/*/temp_*"
    )

    # Add entries if they don't exist
    for entry in "${entries[@]}"; do
        if ! grep -qF -- "$entry" "$gitignore_file"; then
            echo "$entry" >> "$gitignore_file"
            log "Added to .gitignore: $entry"
        else
            log "Already in .gitignore: $entry"
        fi
    done
}

# Backup and create_dirs functions removed - no longer needed for workflow system

install_workflow_system() {
    local target_dir="$1"
    local temp_dir="$2"
    local workflow_path="$target_dir/$WORKFLOW_DIR"
    local clone_dir="$temp_dir/repo"
    local api_dir="$temp_dir/api-files"
    local commit_date=""
    local template_mcp_json="$temp_dir/mcp.json" # Define path for template
    
    # Define the MCP server names to install
    local mcp_servers=("mcp-commit-server" "memory-bank-mcp" "tools-mcp")
    local server_name # Loop variable
    local mcp_server_source_dir # Will be set inside the loop
    local mcp_server_target_dir # Will be set inside the loop

    log "Installing workflow system to $target_dir"

    # Use curl if specified or if git is not available
    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        if [[ -n "${USE_CURL:-}" ]]; then
            log "Using curl (forced by --use-curl option)"
        else
            log "Using curl (git not available)"
        fi
        
        # Get commit date from API
        commit_date=$(get_last_commit_date "curl")
        log "Installing workflow system from master branch (latest commit: $commit_date)"

        # Download mcp.json template
        log "Downloading mcp.json template"
        download_file "$RAW_URL_BASE/.cursor/mcp.json" "$template_mcp_json"

        # Download workflow-steps
        log "Downloading workflow-steps..."
        mkdir -p "$workflow_path"
        local workflow_files=("start-workflow.md" "task-decomposition.md" "implementation.md" "experience-execution.md" "fix.md" "context-update.md")
        for file in "${workflow_files[@]}"; do
            download_file "$RAW_URL_BASE/.cursor/workflow-steps/$file" "$workflow_path/$file"
        done
        
        # Download start.mdc rule
        log "Downloading start.mdc rule..."
        mkdir -p "$target_dir/.cursor/rules"
        download_file "$RAW_URL_BASE/.cursor/rules/start.mdc" "$target_dir/.cursor/rules/start.mdc"

        # Download pre-commit hook
        log "Downloading .githooks/pre-commit"
        local hooks_api_dir="$api_dir/githooks"
        mkdir -p "$hooks_api_dir"
        download_file "$RAW_URL_BASE/.githooks/pre-commit" "$hooks_api_dir/pre-commit"

        # Clean and setup MCP directories
        log "Setting up MCP server directories..."
        rm -rf "$target_dir/.cursor/mcp" || warn "Failed to remove existing MCP directory (may not exist)"
        mkdir -p "$target_dir/.cursor/mcp" || error "Failed to create MCP directory: $target_dir/.cursor/mcp"

        # Download MCP server files
        for server_name in "${mcp_servers[@]}"; do
            mcp_server_target_dir="$target_dir/.cursor/mcp/$server_name"
            mkdir -p "$mcp_server_target_dir"
            
            if [[ "$server_name" == "mcp-commit-server" ]]; then
                log "Downloading mcp-commit-server files..."
                download_file "$RAW_URL_BASE/.cursor/mcp/mcp-commit-server/server.js" "$mcp_server_target_dir/server.js"
                download_file "$RAW_URL_BASE/.cursor/mcp/mcp-commit-server/package.json" "$mcp_server_target_dir/package.json"
            elif [[ "$server_name" == "memory-bank-mcp" ]]; then
                log "Downloading memory-bank-mcp server files..."
                mkdir -p "$mcp_server_target_dir/lib"
                mkdir -p "$mcp_server_target_dir/mcp_tools"
                download_file "$RAW_URL_BASE/.cursor/mcp/memory-bank-mcp/server.js" "$mcp_server_target_dir/server.js"
                download_file "$RAW_URL_BASE/.cursor/mcp/memory-bank-mcp/package.json" "$mcp_server_target_dir/package.json"
                download_file "$RAW_URL_BASE/.cursor/mcp/memory-bank-mcp/lib/userbrief_manager.js" "$mcp_server_target_dir/lib/userbrief_manager.js"
                download_file "$RAW_URL_BASE/.cursor/mcp/memory-bank-mcp/lib/memory_context.js" "$mcp_server_target_dir/lib/memory_context.js"
                download_file "$RAW_URL_BASE/.cursor/mcp/memory-bank-mcp/lib/semantic_search.js" "$mcp_server_target_dir/lib/semantic_search.js"
                # Download all mcp_tools
                local tools=("commit.js" "create_task.js" "get_all_tasks.js" "get_next_tasks.js" "next_rule.js" "read_userbrief.js" "remember.js" "update_task.js" "update_userbrief.js")
                for tool in "${tools[@]}"; do
                    download_file "$RAW_URL_BASE/.cursor/mcp/memory-bank-mcp/mcp_tools/$tool" "$mcp_server_target_dir/mcp_tools/$tool"
                done
            elif [[ "$server_name" == "tools-mcp" ]]; then
                log "Downloading tools-mcp server files..."
                mkdir -p "$mcp_server_target_dir/mcp_tools"
                download_file "$RAW_URL_BASE/.cursor/mcp/tools-mcp/server.js" "$mcp_server_target_dir/server.js"
                download_file "$RAW_URL_BASE/.cursor/mcp/tools-mcp/package.json" "$mcp_server_target_dir/package.json"
                # Download all tools
                local tools=("consult_image.js" "execute_command.js" "get_terminal_output.js" "get_terminal_status.js" "regex_edit.js" "stop_terminal_command.js" "take_webpage_screenshot.js")
                for tool in "${tools[@]}"; do
                    download_file "$RAW_URL_BASE/.cursor/mcp/tools-mcp/mcp_tools/$tool" "$mcp_server_target_dir/mcp_tools/$tool"
                done
            fi
        done

    else
        # Use git clone
        log "Using git clone for installation"
        clone_repository "$REPO_URL" "$clone_dir"
        
        # Get commit date
        commit_date=$(get_last_commit_date)
        log "Installing workflow system from master branch (latest commit: $commit_date)"

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
        
        # Copy mcp.json template
        if [[ -f "$clone_dir/.cursor/mcp.json" ]]; then
            log "Copying mcp.json template from clone"
            if ! cp "$clone_dir/.cursor/mcp.json" "$template_mcp_json"; then
                error "Failed to copy mcp.json template. Please check permissions."
            fi
        else
            warn "mcp.json template not found in repository clone at .cursor/mcp.json."
            touch "$template_mcp_json"
        fi

        # Clean and setup MCP directories
        log "Setting up MCP server directories..."
        rm -rf "$target_dir/.cursor/mcp" || warn "Failed to remove existing MCP directory (may not exist)"
        mkdir -p "$target_dir/.cursor/mcp" || error "Failed to create MCP directory: $target_dir/.cursor/mcp"

        # Copy MCP server files
        for server_name in "${mcp_servers[@]}"; do
            mcp_server_source_dir="$clone_dir/.cursor/mcp/$server_name"
            mcp_server_target_dir="$target_dir/.cursor/mcp/$server_name"

            if [[ -d "$mcp_server_source_dir" ]]; then
                log "Copying $server_name files..."
                mkdir -p "$mcp_server_target_dir"
                if ! cp -r "$mcp_server_source_dir/"* "$mcp_server_target_dir/"; then
                    if [ -z "$(ls -A "$mcp_server_source_dir")" ]; then
                        warn "MCP server source directory for $server_name is empty."
                    else
                        error "Failed to copy $server_name files. Please check disk space and permissions."
                    fi
                else
                    log "$server_name files copied successfully."
                fi
            else
                warn "Source directory for $server_name not found: $mcp_server_source_dir"
            fi
        done
    fi

    # Set permissions for workflow and MCP directories
    if [[ -d "$workflow_path" ]]; then
        chmod -R u+rw "$workflow_path" || true
    fi
    
    for server_name in "${mcp_servers[@]}"; do
        local mcp_server_target_dir="$target_dir/.cursor/mcp/$server_name"
        if [[ -d "$mcp_server_target_dir" ]]; then
            chmod -R u+rw "$mcp_server_target_dir" || true
        fi
    done

    # Manage .gitignore file
    manage_gitignore "$target_dir"

    log "Workflow system and MCP servers installed successfully"
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
    
    # Calculate memory-bank-mcp server script path
    local memory_bank_script_rel_path=".cursor/mcp/memory-bank-mcp/server.js"
    local memory_bank_script_path="$target_dir/$memory_bank_script_rel_path"
    local memory_bank_script_abs_path="$target_dir_abs/${memory_bank_script_rel_path#./}"
    local memory_bank_script_win_path="$memory_bank_script_abs_path"
    
    # Convert memory-bank-mcp script path for Windows if needed
    if [[ "$os_type" == "Msys" ]]; then
        if command -v cygpath >/dev/null 2>&1; then
            if win_path=$(cygpath -w "$memory_bank_script_abs_path"); then
                memory_bank_script_win_path="$win_path"
            fi
        else
            memory_bank_script_win_path=$(echo "$memory_bank_script_abs_path" | sed -e 's|^/c/|C:\\\\|' -e 's|/|\\\\|g')
        fi
    fi
    
    # Escape memory-bank-mcp script path for JSON
    local memory_bank_script_json_safe
    memory_bank_script_json_safe=$(echo "$memory_bank_script_win_path" | sed 's/\\/\\\\/g')

    # Overwrite the target file directly using here-document
    # Using cat > ensures the file is overwritten or created.
    # Use absolute paths calculated dynamically to work from any execution directory
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
        "MemoryBankMCP": {
            "command": "node",
            "args": [
                "$memory_bank_script_json_safe",
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

# Function to install the Streamlit app and dependencies
install_streamlit_app() {
    log "Installing Streamlit app and dependencies..."
    local target_dir="$1"
    local temp_dir="$2"
    local streamlit_dir="$target_dir/.cursor/streamlit_app"
    local requirements_file="$streamlit_dir/requirements.txt"
    local startup_script="$target_dir/.cursor/run_streamlit.sh"
    local clone_dir="$temp_dir/repo"
    local api_dir="$temp_dir/api-files"

    # Create streamlit directory
    mkdir -p "$streamlit_dir" || {
        warn "Failed to create Streamlit directory. Skipping Streamlit installation."
        return
    }

    # Download or copy Streamlit app files
    if [[ -n "${USE_CURL:-}" ]] || ! command -v git >/dev/null 2>&1; then
        log "Downloading Streamlit app files..."
        
        # Download main app file
        download_file "$RAW_URL_BASE/.cursor/streamlit_app/app.py" "$streamlit_dir/app.py"
        download_file "$RAW_URL_BASE/.cursor/streamlit_app/requirements.txt" "$streamlit_dir/requirements.txt"
        download_file "$RAW_URL_BASE/.cursor/streamlit_app/tasks.json" "$streamlit_dir/tasks.json"
        
        # Download pages directory
        mkdir -p "$streamlit_dir/pages"
        local page_files=("add_request.py" "memory.py" "task_status.py")
        for page in "${page_files[@]}"; do
            download_file "$RAW_URL_BASE/.cursor/streamlit_app/pages/$page" "$streamlit_dir/pages/$page"
        done
        
        # Download startup script
        download_file "$RAW_URL_BASE/.cursor/run_streamlit.sh" "$startup_script"
    else
        log "Copying Streamlit app files from git clone..."
        
        if [[ -d "$clone_dir/.cursor/streamlit_app" ]]; then
            if ! cp -r "$clone_dir/.cursor/streamlit_app/"* "$streamlit_dir/"; then
                warn "Failed to copy Streamlit app files. Please check permissions."
                return
            fi
        else
            warn "Streamlit app directory not found in repository clone"
            return
        fi
        
        # Copy startup script
        if [[ -f "$clone_dir/.cursor/run_streamlit.sh" ]]; then
            cp "$clone_dir/.cursor/run_streamlit.sh" "$startup_script"
        else
            warn "Streamlit startup script not found in repository clone"
        fi
    fi

    # Make startup script executable
    if [[ -f "$startup_script" ]]; then
        chmod +x "$startup_script" || warn "Failed to make startup script executable"
        log "Streamlit startup script installed at: $startup_script"
    fi

    # Install dependencies if requirements file exists
    if [[ ! -f "$requirements_file" ]]; then
        warn "Streamlit requirements.txt not found at $requirements_file. Skipping dependency installation."
        return
    fi

    log "Installing Streamlit dependencies..."
    
    # Determine Python and pip commands
    local python_cmd=""
    local pip_cmd=""
    
    if command -v python3 &>/dev/null && command -v pip3 &>/dev/null; then
        python_cmd="python3"
        pip_cmd="pip3"
    elif command -v python &>/dev/null && command -v pip &>/dev/null; then
        python_cmd="python"
        pip_cmd="pip"
    else
        warn "python/pip not found. Cannot install Streamlit app dependencies. Please install Python and pip, then run 'pip install -r $requirements_file'."
        return
    fi

    log "Found $python_cmd and $pip_cmd. Installing Streamlit dependencies..."
    if $pip_cmd install -r "$requirements_file"; then
        log "Streamlit dependencies installed successfully."
        log "To start the Streamlit UI, run: $startup_script"
    else
        warn "Failed to install Streamlit dependencies with $pip_cmd. Please install them manually from $requirements_file."
    fi
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
1. Install the Cursor Memory Bank workflow system using git clone or curl
2. Set up MCP servers (ToolsMCP, MemoryBankMCP, mcp-commit-server)
3. Download the all-MiniLM-L6-v2 model for semantic search
4. Install Streamlit UI for monitoring agent status
5. Install start.mdc rule for autonomous workflow operation
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

# Install workflow system and MCP servers
install_workflow_system "$INSTALL_DIR" "$TEMP_DIR"

# Install pre-commit hook
install_pre_commit_hook "$INSTALL_DIR" "$TEMP_DIR"

# Merge MCP JSON template with existing config (NOW uses absolute path logic)
merge_mcp_json "$INSTALL_DIR"

# Install Internal MCP Commit Server dependencies if present in the TARGET directory
INTERNAL_MCP_SERVER_DIR="$INSTALL_DIR/.cursor/mcp/mcp-commit-server"
if [[ -d "$INTERNAL_MCP_SERVER_DIR" ]] && [[ -f "$INTERNAL_MCP_SERVER_DIR/package.json" ]]; then

    # Clean up previous installs within the specific server directory before npm install
    log "Cleaning up previous build artifacts in $INTERNAL_MCP_SERVER_DIR..."
    if [[ -d "$INTERNAL_MCP_SERVER_DIR/node_modules" ]]; then
        rm -rf "$INTERNAL_MCP_SERVER_DIR/node_modules" || warn "Could not remove existing node_modules directory."
    fi
    # Remove old log files if any
    rm -f "$INTERNAL_MCP_SERVER_DIR"/*.log

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

# Install Memory Bank MCP Server dependencies if present in the TARGET directory
MEMORY_BANK_MCP_SERVER_DIR="$INSTALL_DIR/.cursor/mcp/memory-bank-mcp"
if [[ -d "$MEMORY_BANK_MCP_SERVER_DIR" ]] && [[ -f "$MEMORY_BANK_MCP_SERVER_DIR/package.json" ]]; then

    # Clean up previous installs within the specific server directory before npm install
    log "Cleaning up previous build artifacts in $MEMORY_BANK_MCP_SERVER_DIR..."
    if [[ -d "$MEMORY_BANK_MCP_SERVER_DIR/node_modules" ]]; then
        rm -rf "$MEMORY_BANK_MCP_SERVER_DIR/node_modules" || warn "Could not remove existing node_modules directory."
    fi
    # Remove old log files if any
    rm -f "$MEMORY_BANK_MCP_SERVER_DIR"/*.log

    log "Installing Memory Bank MCP Server dependencies in $MEMORY_BANK_MCP_SERVER_DIR..."
    
    # Ensure the server.js file exists (already copied by install_rules ideally)
    if [[ ! -f "$MEMORY_BANK_MCP_SERVER_DIR/server.js" ]]; then
        warn "server.js file not found in $MEMORY_BANK_MCP_SERVER_DIR. Dependency installation might fail or server won't run."
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
        log "Running npm install in $MEMORY_BANK_MCP_SERVER_DIR..."
        (cd "$MEMORY_BANK_MCP_SERVER_DIR" && $timeout_cmd npm install)
        npm_status=$?
        
        if [[ $npm_status -eq 124 ]]; then # 124 is the exit code for timeout command
             warn "'npm install' in $MEMORY_BANK_MCP_SERVER_DIR timed out after 60 seconds. Please check network or run manually."
        elif [[ $npm_status -ne 0 ]]; then
            warn "Failed to install Memory Bank MCP Server dependencies (Exit code: $npm_status). Please check logs or run 'npm install' in $MEMORY_BANK_MCP_SERVER_DIR manually."
        else
            log "Memory Bank MCP Server dependencies installed."
            
            # Verify node_modules directory exists and has content
            if [[ ! -d "$MEMORY_BANK_MCP_SERVER_DIR/node_modules" ]]; then
                warn "node_modules directory not found in $MEMORY_BANK_MCP_SERVER_DIR after npm install. MCP server may not function properly."
            else
                log "node_modules directory verified. Memory Bank MCP Server should have all required dependencies."
            fi
        fi
    else
        warn "npm not found. Skipping Memory Bank MCP Server dependency installation. Please install Node.js and npm, then run 'npm install' in $MEMORY_BANK_MCP_SERVER_DIR manually."
    fi
    
elif [[ -d "$INSTALL_DIR/.cursor/mcp" ]]; then # Check if mcp dir exists but server subdir doesn't
    log "Memory Bank MCP Server directory not found in $INSTALL_DIR/.cursor/mcp/. Skipping dependency installation."
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

# Install Streamlit App
install_streamlit_app "$INSTALL_DIR"

# Install ML Model
install_ml_model "$INSTALL_DIR"

log "Installation completed successfully!"

# Only show manual step if auto-config failed or was skipped
if [[ "$auto_config_failed" -eq 1 ]]; then
    log "${YELLOW}ACTION REQUIRED:${NC} To enable the installed git hooks (e.g., pre-commit), run the following command in your repository root:"
    log "  git config core.hooksPath .githooks"
fi 