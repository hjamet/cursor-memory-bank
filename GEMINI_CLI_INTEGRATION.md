# Gemini CLI MCP Integration

This document describes the automatic Gemini CLI MCP server configuration feature implemented in the Cursor Memory Bank installation script.

## Overview

The installation script now automatically configures MCP (Model Context Protocol) servers for Google's Gemini CLI, enabling seamless integration between the Cursor Memory Bank system and Gemini CLI's AI agent capabilities.

## What It Does

When running `install.sh`, the script automatically:

1. **Configures MCP Servers**: Creates or updates `~/.gemini/settings.json` with three MCP servers:
   - **MyMCP**: The commit automation server (`mcp-commit-server`)
   - **MemoryBankMCP**: The persistent memory and task management server (`memory-bank-mcp`)
   - **Context7**: The Upstash Context7 server for enhanced context management

2. **Cross-Platform Path Handling**: Automatically handles Windows/Unix path differences and JSON escaping

3. **Safe Configuration**: Warns users about existing configurations before overwriting

## Generated Configuration

The script creates a `~/.gemini/settings.json` file with the following structure:

```json
{
    "mcpServers": {
        "MyMCP": {
            "command": "node",
            "args": ["<absolute-path-to-mcp-commit-server>/server.js"]
        },
        "MemoryBankMCP": {
            "command": "node", 
            "args": ["<absolute-path-to-memory-bank-mcp>/server.js"]
        },
        "Context7": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp@latest"]
        }
    }
}
```

## Usage After Installation

Once configured, you can use Gemini CLI with the MCP servers:

```bash
# Start an interactive chat session with MCP servers
gemini chat

# List available MCP servers
gemini mcp list

# Get descriptions of MCP server tools
gemini mcp desc
```

## Available MCP Tools in Gemini CLI

### MyMCP (mcp-commit-server)
- **Git operations**: Commit creation, branch management, repository status
- **Automated commit messages**: AI-generated commit messages based on changes
- **Repository analysis**: File change analysis, diff generation

### MemoryBankMCP (memory-bank-mcp)
- **Task management**: Create, update, and track development tasks
- **Persistent memory**: Store and retrieve project context and decisions
- **Workflow automation**: Autonomous workflow execution and management
- **Commit management**: Advanced commit creation with structured descriptions

### Context7
- **Documentation access**: Real-time access to library documentation
- **Code examples**: Context-aware code snippets and examples
- **API reference**: Up-to-date API documentation for popular libraries

## Prerequisites

### Required Software
- **Node.js**: Required to run the MCP servers
- **Gemini CLI**: Install from [Google's Gemini CLI repository](https://github.com/google-gemini/gemini-cli)
- **Git**: Required for repository operations (MyMCP server)

### Gemini CLI Installation
```bash
# Install Gemini CLI (follow official instructions)
npm install -g @google-labs/gemini-cli

# Or using other installation methods as per official documentation
```

## Configuration Details

### Automatic Path Resolution
The script automatically:
- Calculates absolute paths to MCP server scripts
- Handles Windows path conversion (C:\\ format)
- Escapes paths properly for JSON embedding
- Validates server script existence before configuration

### Error Handling
- **Missing Scripts**: Warns and skips configuration if MCP server scripts are missing
- **Permission Issues**: Reports directory creation failures
- **Existing Configuration**: Warns before overwriting existing MCP server configurations

### Debug Information
When running the installation, you'll see debug output including:
- Calculated absolute paths
- JSON-escaped paths
- File creation status
- Configuration validation results

## Troubleshooting

### Common Issues

1. **"MCP server not found" errors**
   - Ensure the installation completed successfully
   - Verify MCP server scripts exist in `.cursor/mcp/` directories
   - Check file permissions

2. **Path-related errors on Windows**
   - The script automatically handles Windows path conversion
   - If issues persist, check that paths in `~/.gemini/settings.json` use proper escaping

3. **Gemini CLI doesn't recognize servers**
   - Verify Gemini CLI is properly installed
   - Check that `~/.gemini/settings.json` exists and has correct JSON syntax
   - Restart Gemini CLI after configuration changes

### Manual Configuration

If automatic configuration fails, you can manually edit `~/.gemini/settings.json`:

```json
{
    "mcpServers": {
        "MyMCP": {
            "command": "node",
            "args": ["/path/to/your/project/.cursor/mcp/mcp-commit-server/server.js"]
        },
        "MemoryBankMCP": {
            "command": "node",
            "args": ["/path/to/your/project/.cursor/mcp/memory-bank-mcp/server.js"]
        },
        "Context7": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp@latest"]
        }
    }
}
```

## Integration Benefits

### Enhanced Development Workflow
- **Unified AI Interface**: Access both Cursor and Gemini CLI capabilities
- **Consistent Context**: Shared memory and task management across tools
- **Automated Documentation**: Real-time access to library documentation
- **Intelligent Commits**: AI-powered commit message generation

### Cross-Platform Compatibility
- **Windows Support**: Automatic path conversion and escaping
- **Unix/Linux Support**: Native path handling
- **macOS Support**: Full compatibility with macOS development environments

## Security Considerations

- **Local Configuration**: All MCP servers run locally on your machine
- **No External Dependencies**: Memory and task data stays on your system
- **Configurable Access**: You control which MCP servers are enabled
- **Standard Permissions**: Uses standard file system permissions

## Future Enhancements

Planned improvements include:
- **Selective Server Configuration**: Choose which MCP servers to install
- **Configuration Backup**: Automatic backup of existing settings
- **Server Health Monitoring**: Automatic validation of MCP server status
- **Custom Server Integration**: Support for user-defined MCP servers

## Support

For issues related to:
- **Installation**: Check the main installation script logs
- **Gemini CLI**: Refer to [Google's Gemini CLI documentation](https://github.com/google-gemini/gemini-cli)
- **MCP Protocol**: See [Model Context Protocol documentation](https://github.com/modelcontextprotocol)
- **Cursor Memory Bank**: Check project documentation and issues

## Technical Implementation

The feature is implemented in the `configure_gemini_cli_mcp()` function in `install.sh`:
- **Path Calculation**: Uses `pwd -P` for absolute path resolution
- **Cross-Platform Support**: Detects OS type and applies appropriate path conversion
- **JSON Generation**: Uses here-document for clean JSON generation
- **Error Handling**: Comprehensive validation and user feedback
- **Debug Support**: Extensive logging for troubleshooting 