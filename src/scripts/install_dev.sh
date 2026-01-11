#!/bin/bash

# install_dev.sh
# Installs the current repository into a target project using symlinks.
# Useful for developing the Memory Bank and testing changes immediately.

set -e
set -u

# Default target is the current directory if not specified
TARGET_DIR="${1:-.}"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

log "Installing Memory Bank (DEV MODE) from $SOURCE_DIR to $TARGET_DIR"

if [[ ! -d "$TARGET_DIR" ]]; then
    error "Target directory does not exist: $TARGET_DIR"
fi

# Ensure .cursor structure exists in target
mkdir -p "$TARGET_DIR/.cursor/rules"
mkdir -p "$TARGET_DIR/.cursor/commands"
mkdir -p "$TARGET_DIR/.cursor/mcp"

# Helper for safe symlinking
safe_ln_s() {
    local src="$1"
    local dst="$2"
    
    # Get absolute paths to compare
    local abs_src
    abs_src=$(realpath "$src" 2>/dev/null || readlink -f "$src" 2>/dev/null || echo "$src")
    
    # Ensure parent of dst exists so we can resolve it
    mkdir -p "$(dirname "$dst")"
    local abs_dst
    abs_dst=$(realpath "$dst" 2>/dev/null || readlink -f "$dst" 2>/dev/null || echo "$dst")

    if [[ "$abs_src" == "$abs_dst" ]]; then
        log "  -> Skipping $dst (same as source)"
        return 0
    fi
    
    # If dst exists and is NOT a symlink but a directory, 
    # and we are trying to link something into it with the same name,
    # ln -sfn will usually create a loop.
    if [[ -d "$dst" && ! -L "$dst" ]]; then
        # If it's a directory, we might want to link content inside 
        # OR we might want to error/skip.
        # In our case, .agent/src, .agent/workflows etc should be symlinks, not real dirs in target.
        # If they are real dirs, we skip to avoid creating dst/name -> src
        warn "  -> Skipping $dst (already exists as a directory)"
        return 0
    fi

    ln -sfn "$abs_src" "$abs_dst"
}

# 1. Symlink Source Code
mkdir -p "$TARGET_DIR/.agent"
log "Symlinking src/ to $TARGET_DIR/.agent/src..."
safe_ln_s "$SOURCE_DIR/src" "$TARGET_DIR/.agent/src"

log "Symlinking workflows to $TARGET_DIR/.agent/workflows..."
safe_ln_s "$SOURCE_DIR/.agent/workflows" "$TARGET_DIR/.agent/workflows"

log "Symlinking rules to $TARGET_DIR/.agent/rules..."
safe_ln_s "$SOURCE_DIR/.agent/rules" "$TARGET_DIR/.agent/rules"


# 2. Cursor Adaptation (Symlinking into .cursor)
# Note: Cursor needs rules in .cursor/rules.
# If we symlink, we rely on the source file having "globs:" property if Cursor requires it.
# If not, this might be broken for rules that only have "trigger:".
# But for DEV mode, we assume the dev knows this or files are dual-compatible.

log "Symlinking rules to $TARGET_DIR/.cursor/rules..."
# We iterate and link individual files to allow for mixed content if needed, 
# or just link the dir? Cursor supports subdirs in .cursor/rules? Yes.
# BUT existing .cursor/rules might contain other stuff.
# Let's link the files.
for rule in "$SOURCE_DIR/.agent/rules"/*.md; do
    basename=$(basename "$rule")
    ln -sf "$rule" "$TARGET_DIR/.cursor/rules/$basename"
done

log "Symlinking commands to $TARGET_DIR/.cursor/commands..."
# Workflows from .agent/workflows -> .cursor/commands
for cmd in "$SOURCE_DIR/.agent/workflows"/*.md; do
    basename=$(basename "$cmd")
    ln -sf "$cmd" "$TARGET_DIR/.cursor/commands/$basename"
done

# 3. generate mcp.json (Dev version pointing to source)
# We need to generate a .cursor/mcp.json that points to the ABSOLUTE path of the source server.
log "Generating $TARGET_DIR/.cursor/mcp.json..."
cat > "$TARGET_DIR/.cursor/mcp.json" <<EOF
{
  "mcpServers": {
    "memory-bank": {
      "command": "node",
      "args": [
        "$SOURCE_DIR/src/server/memory-bank/server.js"
      ],
      "env": {
        "NODE_ENV": "development"
      }
    }
  }
}
EOF


# 3.5 Install Dependencies for MCP Server
log "Installing dependencies for Memory Bank MCP Server..."
if [[ -d "$SOURCE_DIR/src/server/memory-bank" ]]; then
    (cd "$SOURCE_DIR/src/server/memory-bank" && npm install)
else
    warn "MCP Server directory not found at $SOURCE_DIR/src/server/memory-bank. Skipping npm install."
fi

# 4. Generate Universal MCP Config (~/.gemini/antigravity/mcp_config.json)
MCP_CONFIG_DIR="$HOME/.gemini/antigravity"
MCP_CONFIG_FILE="$MCP_CONFIG_DIR/mcp_config.json"

if [[ ! -d "$MCP_CONFIG_DIR" ]]; then
    log "Creating MCP config directory: $MCP_CONFIG_DIR"
    mkdir -p "$MCP_CONFIG_DIR"
fi


log "Generating Universal MCP Config at $MCP_CONFIG_FILE..."

# Define the new server config as a JSON string
SERVER_CONFIG_JSON=$(cat <<EOF
{
  "memory-bank": {
    "command": "node",
    "args": [
      "$SOURCE_DIR/src/server/memory-bank/server.js"
    ],
    "env": {
      "NODE_ENV": "development"
    }
  }
}
EOF
)


# Use Node.js to safely merge config
SERVER_CONFIG_JSON="$SERVER_CONFIG_JSON" node -e "
const fs = require('fs');
const targetFile = '$MCP_CONFIG_FILE';
const newServerConfig = JSON.parse(process.env.SERVER_CONFIG_JSON);

let config = { mcpServers: {} };

if (fs.existsSync(targetFile)) {
    try {
        const content = fs.readFileSync(targetFile, 'utf8');
        config = JSON.parse(content);
        if (!config.mcpServers) config.mcpServers = {};
    } catch (e) {
        console.error('Warning: Could not parse existing config, creating new one.');
    }
}

// Merge new server config
Object.assign(config.mcpServers, newServerConfig);

fs.writeFileSync(targetFile, JSON.stringify(config, null, 2));
console.log('Updated config successfully.');
"



log "✅ Dev Installation Complete."
log "Memory Bank code is linked from: $SOURCE_DIR"
log "Rules and Commands are linked."
log "MCP Config points to source server."
