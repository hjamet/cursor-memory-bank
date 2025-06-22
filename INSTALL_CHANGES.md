# Installation System Updates

## Summary of Changes

This document outlines the major changes made to the Cursor Memory Bank installation and monitoring system.

## 1. Installation Script Modernization

### What Changed
- **Removed legacy `.mdc` rules system** - No longer installs outdated rule files
- **Simplified to workflow-based system** - Now installs modern `.cursor/workflow-steps/` instead
- **Updated MCP server list** - Now installs: `mcp-commit-server`, `memory-bank-mcp`, `tools-mcp`
- **Integrated model download** - Automatically downloads `all-MiniLM-L6-v2` for semantic search

### Technical Details
- Renamed `install_rules()` → `install_workflow_system()`
- Removed `backup_rules()` and `create_dirs()` functions
- Updated directory structure from `.cursor/rules/` → `.cursor/workflow-steps/`
- Simplified installation logic for both git clone and curl methods

### Benefits
- ✅ Faster installation (no unnecessary file copying)
- ✅ Modern workflow system ready out-of-the-box
- ✅ Semantic search capabilities enabled
- ✅ Cleaner, more maintainable codebase

## 2. Streamlit UI Reorganization

### What Changed
- **Moved location**: `.cursor/memory-bank/streamlit_app/` → `.cursor/streamlit_app/`
- **Updated script**: `run_ui.sh` moved to `.cursor/run_ui.sh` with corrected paths
- **Added new monitoring page**: `agent_status.py` for comprehensive agent monitoring

### New Agent Status Page Features
- 📋 **Current Workflow Step** - Shows active workflow rule and details
- 🧠 **Memory Status** - Working memory and long-term memory status
- 📝 **User Requests & Preferences** - Active requests from userbrief
- ✅ **Current Tasks** - Task status summary with metrics
- ⚙️ **System Status** - MCP servers and workflow system health
- 🔄 **Auto-refresh** - Optional 30-second auto-refresh for live monitoring

### Benefits
- ✅ Real-time agent monitoring
- ✅ Better organization of UI components
- ✅ Comprehensive system health overview
- ✅ User-friendly status visualization

## 3. Model Download Integration

### What Changed
- **Embedded download script** - No longer relies on external `download_model.py`
- **Automatic model setup** - Creates proper directory structure
- **Error handling** - Graceful fallback if model download fails

### Technical Implementation
```bash
# Creates temporary Python script for model download
cat > "$temp_download_script" << 'EOF'
from sentence_transformers import SentenceTransformer
import os
import sys

model_name = 'all-MiniLM-L6-v2'
cache_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join('.cursor', 'memory-bank', 'models')

print(f"Downloading {model_name} to {cache_dir}...")

try:
    model = SentenceTransformer(model_name, cache_folder=cache_dir)
    print("Model downloaded successfully.")
except Exception as e:
    print(f"Error downloading model: {e}")
    sys.exit(1)
EOF
```

### Benefits
- ✅ Self-contained installation
- ✅ Proper model directory structure
- ✅ Better error handling and logging
- ✅ No external dependencies

## Usage Instructions

### Running the Installation
```bash
# Standard installation
bash install.sh

# With model download (recommended)
bash install.sh  # Model download is now automatic

# Force curl method
bash install.sh --use-curl
```

### Launching the UI
```bash
# From project root
cd .cursor
bash run_ui.sh

# Or directly
streamlit run .cursor/streamlit_app/app.py
```

### Accessing Agent Status
1. Launch the Streamlit UI
2. Navigate to "Agent Status" page in the sidebar
3. View real-time agent state and system health
4. Enable auto-refresh for live monitoring

## File Structure Changes

### Before
```
.cursor/
├── rules/                    # Legacy rules system
├── memory-bank/
│   ├── streamlit_app/       # Old location
│   └── download_model.py    # External script
└── mcp.json

run_ui.sh                    # Root level
```

### After
```
.cursor/
├── workflow-steps/          # Modern workflow system
├── streamlit_app/           # New location
│   ├── app.py
│   ├── pages/
│   │   ├── task_status.py
│   │   └── agent_status.py  # New monitoring page
│   └── requirements.txt
├── run_ui.sh               # Moved here
├── memory-bank/
│   └── models/             # Model storage
└── mcp.json
```

## Compatibility Notes

- ✅ **Backward compatible** - Existing MCP configurations work unchanged
- ✅ **Workflow system** - All existing workflow steps preserved
- ✅ **Memory system** - Userbrief and memory context unchanged
- ⚠️ **Legacy rules** - Old `.mdc` files no longer supported (use workflow-steps)

## Troubleshooting

### Model Download Issues
```bash
# Manual model download if automatic fails
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', cache_folder='.cursor/memory-bank/models')"
```

### Streamlit Issues
```bash
# Install dependencies
pip install streamlit

# Check file paths
ls -la .cursor/streamlit_app/
```

### Installation Issues
```bash
# Use curl method if git fails
bash install.sh --use-curl

# Check permissions
chmod +x install.sh
chmod +x .cursor/run_ui.sh
``` 