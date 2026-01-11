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

# 1. Symlink Source Code
# specialized "src" folder in target .cursor isn't standard, but we might need it for MCP
# Actually, for MCP, valid config needs to point to the absolute path of the SOURCE
# So we don't necessarily need to symlink 'src' into the target if we configure MCP correctly.
# BUT, if we want to simulate a "production install" where code is inside .agent (or .cursor), 
# we should symlink `src` to `$TARGET_DIR/.agent/src` (or similar).
# Let's match the production structure:
# Prod: .agent/src, .agent/rules
# Cursor Adapter: .cursor/rules (copies), .cursor/mcp.json (points to .agent/src)

mkdir -p "$TARGET_DIR/.agent"
log "Symlinking src/ to $TARGET_DIR/.agent/src..."
ln -sfn "$SOURCE_DIR/src" "$TARGET_DIR/.agent/src"

mkdir -p "$TARGET_DIR/.agent/workflows"
log "Symlinking workflows to $TARGET_DIR/.agent/workflows..."
# We symlink the directory content or the directory itself?
# Directory itself is better for adding new files.
ln -sfn "$SOURCE_DIR/.agent/workflows" "$TARGET_DIR/.agent/workflows"

log "Symlinking rules to $TARGET_DIR/.agent/rules..."
ln -sfn "$SOURCE_DIR/.agent/rules" "$TARGET_DIR/.agent/rules"


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
      ]
    }
  }
}
EOF

log "✅ Dev Installation Complete."
log "Memory Bank code is linked from: $SOURCE_DIR"
log "Rules and Commands are linked."
log "MCP Config points to source server."
