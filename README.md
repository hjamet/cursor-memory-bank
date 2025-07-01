# Cursor Memory Bank 🧠

## Installation 🚀

### Method 1: Using curl (Recommended)

You can install using this one-liner:

```bash
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master/install.sh | bash
```

**Note for MINGW64/Git Bash users on Windows:** If you encounter `: command not found` errors during installation, it's likely due to line ending issues when piping directly. Use this modified command instead:

```bash
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master/install.sh | tr -d '\r' | bash
```

For better security, you can also:
1. Download the script first:
```bash
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master/install.sh -o install.sh
```

2. Review it:
```bash
less install.sh
```

3. Then run it with any desired options:
```bash
bash install.sh [options]
```

Available options:
- `--dir <path>` : Install to a specific directory (default: current directory)
- `--backup` : Create a backup of existing rules
- `--force` : Overwrite existing files
- `--help` : Show help information
- `--version` : Show version information

Examples:
```bash
# Install to current directory
bash install.sh

# Install to a specific directory
bash install.sh --dir /path/to/install

# Create a backup of existing rules
bash install.sh --backup

# Show help information
bash install.sh --help
```

### Method 2: Using git clone

If you prefer, you can also install Cursor Memory Bank by cloning the repository:

```bash
git clone https://github.com/hjamet/cursor-memory-bank.git
cd cursor-memory-bank
bash install.sh [options]
```

The installation script will:
- Install the rules to your `.cursor/rules` directory
- Always preserve any existing custom rules
- Create a backup of existing rules (only if --backup is used)
- Update only the core rules that need updating
- Preserve any unrelated files that might be in the .cursor directory
- Work even if the .cursor directory already exists
- **Configure Gemini CLI MCP servers** automatically in `~/.gemini/settings.json`

## Gemini CLI Integration 🤖

The installation script automatically configures MCP (Model Context Protocol) servers for Google's Gemini CLI, enabling you to use the same powerful tools in both Cursor and Gemini CLI environments.

### What Gets Configured
- **MyMCP**: Git operations and automated commit messages
- **MemoryBankMCP**: Task management and persistent memory
- **Context7**: Real-time library documentation access

### Usage with Gemini CLI
After installation, you can use Gemini CLI with the configured MCP servers:

```bash
# Start interactive chat with MCP tools
gemini chat

# List available MCP servers
gemini mcp list

# Get tool descriptions
gemini mcp desc
```

For detailed information about Gemini CLI integration, see [GEMINI_CLI_INTEGRATION.md](GEMINI_CLI_INTEGRATION.md).

## What is Cursor Memory Bank? 🤔

Cursor Memory Bank is a system that helps maintain context between coding sessions by storing and organizing information in a coherent file structure. It's designed to work with Cursor, enhancing its capabilities with structured rules and workflows.

### Features
- 📁 Organized file structure for storing context
- 🔄 Automatic backup of custom rules
- 🛠️ Flexible installation options
- 🔒 Safe updates with rule preservation
- 📝 Structured workflows and rules
- 🤖 **Gemini CLI Integration**: Automatic MCP server configuration for Google Gemini CLI

## Agent Workflow Logic 🧠⚙️

The autonomous agent operates on a sophisticated, rule-based workflow designed for robustness and intelligent decision-making. The goal is to systematically process tasks, handle exceptions, and ensure quality through a mandatory testing cycle. The logic is primarily controlled by the script at `.cursor/mcp/memory-bank-mcp/lib/workflow_recommendation.js`.

Here is a diagram representing the core decision-making flow:

```mermaid
graph TD
    subgraph Legend
        direction LR
        Dev[Dev Task]:::devStyle
        Exec[Execution Task]:::execStyle
        Fix[Fix Task]:::fixStyle
        Decomp[Decomposition]:::decompStyle
    end

    subgraph "Main Loop"
        direction TB
        A(Start) --> B{Get Next Task};
        B -- No Tasks --> Z[Context Update / Idle];
        B -- Task Available --> C{Evaluate Task Type};
        C -- Development Req. --> D[1. Implementation];
        C -- Execution Only --> E[2. Experience Execution];
        
        D -- Code Complete --> F[Remember];
        F --> E;

        E -- Testing Complete --> G[Remember];
        G --> H{Test Passed?};
        H -- Yes --> I[3. Context Update / Commit];
        H -- No --> D;
        
        I --> B;
    end

    subgraph "Interrupts"
        direction TB
        J[New User Request] --> K[4. Task Decomposition];
        K --> D;
        L[Blocked Task Detected] --> M[5. Fix];
        M --> D;
    end

    classDef devStyle fill:#cde4ff,stroke:#333,stroke-width:2px;
    classDef execStyle fill:#d5e8d4,stroke:#333,stroke-width:2px;
    classDef fixStyle fill:#f8cecc,stroke:#333,stroke-width:2px;
    classDef decompStyle fill:#dae8fc,stroke:#333,stroke-width:2px;

    class Dev,D devStyle;
    class Exec,E execStyle;
    class Fix,M fixStyle;
    class Decomp,K decompStyle;
```

### Explanation of the Workflow Steps:

The agent's workflow is not a simple linear process but a state machine that intelligently routes tasks based on their nature and the overall system status.

1.  **Implementation (`implementation`)**:
    *   **Trigger**: A task is available in the `TODO` queue.
    *   **Action**: This is the core development step. The agent analyzes the task, writes or modifies code, and prepares the changes. The focus is on completing a single task thoroughly.
    *   **Next Step**: Upon completion, it's **mandatory** for the agent to transition to `Experience Execution` to ensure all changes are tested.

2.  **Experience Execution (`experience-execution`)**:
    *   **Trigger**: Automatically follows `Implementation`. Can also be triggered directly for tasks that only require running commands or tests without code changes.
    *   **Action**: The agent validates the changes made in the previous step. This can involve running automated tests, linters, or performing a dry-run of a feature.
    *   **Next Step**:
        *   If validation **fails** or reveals more work is needed, the agent transitions back to `Implementation`.
        *   If validation **passes**, the agent moves to `Context Update`.

3.  **Context Update (`context-update`)**:
    *   **Trigger**: Follows a successful `Experience Execution`.
    *   **Action**: The agent finalizes the work by committing the changes to version control with a descriptive message. It then updates its own context and prepares for the next cycle.
    *   **Next Step**: The agent returns to the start of the loop to check for new tasks.

4.  **Task Decomposition (`task-decomposition`)**:
    *   **Trigger**: A new user request is detected. This step has high priority and can interrupt the main loop.
    *   **Action**: The agent analyzes the user's request and breaks it down into one or more concrete, actionable tasks that are added to the `TODO` queue.
    *   **Next Step**: The agent enters the `Implementation` step to begin working on the newly created tasks.

5.  **Fix (`fix`)**:
    *   **Trigger**: A task is found in the `BLOCKED` state. This is treated as a high-priority interrupt.
    *   **Action**: The agent's sole focus is to resolve the issue that is blocking the task. This could involve fixing a dependency, correcting a faulty implementation, or other troubleshooting steps.
    *   **Next Step**: Once the issue is resolved, the agent moves to `Implementation` to continue the task.

## Contributing 🤝

While this is primarily a personal project, contributions are welcome! Just note that most of the documentation and rules are in French. If you'd like to help translate the project to English or improve its general-purpose usage, that would be especially appreciated!

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Pre-commit Hook Verification (Manual)

The installation script installs a pre-commit hook in `.githooks/pre-commit` to check for code files exceeding 500 lines. To manually verify this hook blocks commits correctly:

1. Ensure the rules have been installed using `bash install.sh`.
2. Initialize a temporary git repository: `mkdir temp_repo && cd temp_repo && git init`
3. Configure git to use the installed hooks: `git config core.hooksPath ../.githooks`
4. Create a file longer than 500 lines: `seq 510 > long_file.txt`
5. Stage the file: `git add long_file.txt`
6. Attempt to commit:
   - Using the MCP tool: Call `mcp_MyMCP_commit` via Cursor with appropriate arguments (e.g., title, type).
   - OR Using standard git: `git commit -m "Test long file"`
7. Observe the output. The commit should fail, and you should see the error message from the hook script: `COMMIT FAILED: Files exceed maximum line count (500). ... The following files are too long...: long_file.txt`.
8. Clean up: `cd .. && rm -rf temp_repo`

## Troubleshooting 🔧

### MCP Commit Server Issues

If you encounter an error like `Error: Cannot find module '.cursor/mcp/mcp-commit-server/server.js'` when using Cursor, it means the MCP commit server files were not properly installed in your Cursor installation directory. To fix this issue:

1. Make sure the MCP commit server files exist in your project:
```bash
ls -la .cursor/mcp/mcp-commit-server/
```

2. Copy the MCP commit server files to your Cursor installation directory:
```bash
# For Windows (adjust the path as needed):
mkdir -p "C:/Users/<YourUsername>/AppData/Local/Programs/cursor/.cursor/mcp/mcp-commit-server"
cp -r .cursor/mcp/mcp-commit-server/* "C:/Users/<YourUsername>/AppData/Local/Programs/cursor/.cursor/mcp/mcp-commit-server/"

# For macOS (adjust the path as needed):
mkdir -p ~/Library/Application\ Support/cursor/.cursor/mcp/mcp-commit-server
cp -r .cursor/mcp/mcp-commit-server/* ~/Library/Application\ Support/cursor/.cursor/mcp/mcp-commit-server/

# For Linux (adjust the path as needed):
mkdir -p ~/.config/cursor/.cursor/mcp/mcp-commit-server
cp -r .cursor/mcp/mcp-commit-server/* ~/.config/cursor/.cursor/mcp/mcp-commit-server/
```

3. Install the dependencies:
```bash
# Navigate to the MCP commit server directory in your Cursor installation:
cd "C:/Users/<YourUsername>/AppData/Local/Programs/cursor/.cursor/mcp/mcp-commit-server/" # Windows
cd ~/Library/Application\ Support/cursor/.cursor/mcp/mcp-commit-server/ # macOS
cd ~/.config/cursor/.cursor/mcp/mcp-commit-server/ # Linux

# Install dependencies:
npm install
```

4. Create or update the mcp.json file in your Cursor installation directory:
```json
// For Windows - Save this to C:/Users/<YourUsername>/AppData/Local/Programs/cursor/.cursor/mcp.json
{
    "mcpServers": {
        "Git Commit (Internal)": {
            "command": "cmd",
            "args": [
                "/c",
                "node",
                ".cursor/mcp/mcp-commit-server/server.js"
            ],
            "cwd": "."
        }
    }
}

// For macOS/Linux - Save this to ~/Library/Application Support/cursor/.cursor/mcp.json (macOS) or ~/.config/cursor/.cursor/mcp.json (Linux)
{
    "mcpServers": {
        "Git Commit (Internal)": {
            "command": "node",
            "args": [
                ".cursor/mcp/mcp-commit-server/server.js"
            ],
            "cwd": "."
        }
    }
}
```

5. Restart Cursor and the MCP commit server should now be available as a tool.

### MCP Tool Discovery Issues

If you've successfully installed MCP servers but new tools aren't appearing in Cursor's available tools list:

**Quick Solution: Restart Cursor completely**

1. **Close Cursor**: Exit the application entirely
2. **Restart Cursor**: Launch the application again  
3. **Open Workspace**: Navigate back to your project
4. **Verify**: Check if the tool now appears in the available tools list

**Why This Happens:** Cursor caches MCP tool lists for performance. When tools are added to existing servers, the cache isn't automatically refreshed until the application restarts.

**Note:** As of the latest updates, the commit tool has been migrated from MyMCP to MemoryBank MCP server. After updating, you'll need to restart Cursor to see the new `mcp_MemoryBank_commit` tool replace the old `mcp_MyMCP_commit` tool.