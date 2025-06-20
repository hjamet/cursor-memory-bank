# MCP Tool Argument Visibility Issue

This document outlines the investigation and resolution of an issue where MCP tool arguments were not visible in the Cursor UI.

## Analysis
The investigation revealed that while the `remember` and `next_rule` tools correctly exported their Zod schemas, the `server.js` file was not importing or using them correctly. The server was defining its own schemas inline, which were incomplete.

## Resolution
The `server.js` file was updated to import and use the exported Zod schemas from the respective tool files. This ensures that the full schemas, including all arguments and descriptions, are registered with the MCP server.

Additionally, a number of other tools were not being registered correctly, or at all. The `server.js` file was updated to correctly register all tools.

## Conclusion
The issue was resolved by correcting the `server.js` file to properly use the exported Zod schemas. This should fix the argument visibility issue in the Cursor UI. 