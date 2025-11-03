## Legacy UI/ML — Decommission Note

This repository previously contained a Streamlit UI tied to a legacy MCP-based setup. The UI and related ML artifacts added complexity without contributing to the current roadmap-based workflow.

### What was removed
- `.cursor/streamlit_app/` (entire directory: pages, components, utilities, scripts)
- Any remaining ML/model references are not part of the installer or docs anymore

### Rationale
- Simplify installation: single, fail-fast mode via `install.sh`
- Remove unused dependencies and code paths (no Streamlit, no local ML cache)
- Reduce maintenance surface and confusion

### Impact for users
- No action required. The workflow is CLI/agent driven (`/agent`, `/task`).
- If you still need the old UI, refer to repository history (git) to retrieve files.

### Current state
- Installer: single mode, no UI/ML
- Roadmap system: `.cursor/agents/roadmap.yaml` with tasks and reports


