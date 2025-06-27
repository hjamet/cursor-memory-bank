import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

// Helper function to get the correct working directory
// This should match the getWorkingDirectory function from server.js
function getWorkingDirectory() {
    // Access serverDefaultCwd from parent scope or use fallback
    const serverDefaultCwd = process.env.MCP_SERVER_CWD || null;
    return serverDefaultCwd || process.env.CURSOR_WORKSPACE_ROOT || process.cwd();
}

// Helper function to normalize path separators
function normalizePath(filePath) {
    // Convert Windows-style backslashes to forward slashes for consistency
    return filePath.replace(/\\/g, '/');
}

// Helper function to resolve file path with multiple strategies
async function resolveFilePath(originalPath) {
    const workingDir = getWorkingDirectory();
    const normalizedPath = normalizePath(originalPath);

    // Strategy 1: Try the path as provided (absolute or relative to current process.cwd())
    const strategies = [
        {
            name: 'original_path',
            path: originalPath,
            description: 'Path as provided'
        },
        {
            name: 'normalized_path',
            path: normalizedPath,
            description: 'Path with normalized separators'
        },
        {
            name: 'relative_to_working_dir',
            path: path.resolve(workingDir, originalPath),
            description: `Relative to working directory: ${workingDir}`
        },
        {
            name: 'relative_to_working_dir_normalized',
            path: path.resolve(workingDir, normalizedPath),
            description: `Relative to working directory with normalized path: ${workingDir}`
        }
    ];

    // If the original path looks like a Windows absolute path, try Unix-style conversion
    if (/^[A-Za-z]:[\\\/]/.test(originalPath)) {
        strategies.push({
            name: 'windows_to_unix',
            path: originalPath.replace(/^([A-Za-z]):/, '/$1').replace(/\\/g, '/'),
            description: 'Windows path converted to Unix-style'
        });
    }

    // If the original path looks like a Unix absolute path, try Windows-style conversion
    if (originalPath.startsWith('/')) {
        const windowsPath = originalPath.replace(/^\/([A-Za-z])\//, '$1:/').replace(/\//g, '\\');
        strategies.push({
            name: 'unix_to_windows',
            path: windowsPath,
            description: 'Unix path converted to Windows-style'
        });
    }

    const attemptedPaths = [];

    for (const strategy of strategies) {
        try {
            const resolvedPath = path.resolve(strategy.path);
            await fs.access(resolvedPath, fs.constants.F_OK);

            return {
                success: true,
                resolvedPath,
                strategy: strategy.name,
                description: strategy.description,
                attemptedPaths
            };
        } catch (error) {
            attemptedPaths.push({
                strategy: strategy.name,
                path: strategy.path,
                resolvedPath: path.resolve(strategy.path),
                error: error.code || error.message,
                description: strategy.description
            });
        }
    }

    return {
        success: false,
        resolvedPath: null,
        strategy: null,
        description: 'All path resolution strategies failed',
        attemptedPaths
    };
}

const handleRegexEdit = async ({ file_path, regex_pattern, replacement_text }) => {
    try {
        const originalFilePath = file_path; // Keep original for response

        // Step 1: Resolve the file path using multiple strategies
        const pathResolution = await resolveFilePath(file_path);

        if (!pathResolution.success) {
            const errorResponse = {
                status: "error",
                message: "File not found using any path resolution strategy",
                error: `File not found at path: ${file_path}`,
                operation: "regex_edit",
                file_path: originalFilePath,
                regex_pattern: regex_pattern,
                replacement_text: replacement_text,
                success: false,
                path_resolution_failed: true,
                working_directory: getWorkingDirectory(),
                attempted_paths: pathResolution.attemptedPaths,
                troubleshooting: {
                    suggestions: [
                        "Verify the file exists at the specified location",
                        "Check if the path is relative to the correct working directory",
                        "Ensure proper path separators for your operating system",
                        "Try using an absolute path if relative path fails"
                    ],
                    working_directory_info: `Current working directory: ${getWorkingDirectory()}`
                }
            };

            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(errorResponse, null, 2)
                }]
            };
        }

        const fullPath = pathResolution.resolvedPath;

        // Step 2: Read the file content
        let content;
        try {
            content = await fs.readFile(fullPath, 'utf8');
        } catch (error) {
            const errorResponse = {
                status: "error",
                message: "File found but could not be read",
                error: `Failed to read file: ${error.message}`,
                operation: "regex_edit",
                file_path: originalFilePath,
                resolved_path: fullPath,
                path_resolution_strategy: pathResolution.strategy,
                regex_pattern: regex_pattern,
                replacement_text: replacement_text,
                success: false,
                read_failed: true
            };

            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(errorResponse, null, 2)
                }]
            };
        }

        // Step 3: Validate regex pattern
        let regex;
        try {
            regex = new RegExp(regex_pattern);
        } catch (regexError) {
            const errorResponse = {
                status: "error",
                message: "Invalid regex pattern",
                error: `Invalid regex pattern: ${regexError.message}`,
                operation: "regex_edit",
                file_path: originalFilePath,
                resolved_path: fullPath,
                path_resolution_strategy: pathResolution.strategy,
                regex_pattern: regex_pattern,
                replacement_text: replacement_text,
                success: false,
                regex_validation_failed: true
            };

            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(errorResponse, null, 2)
                }]
            };
        }

        // Step 4: Check if pattern exists in file
        const match = content.match(regex);

        if (!match) {
            const errorResponse = {
                status: "error",
                message: "Pattern not found in file",
                error: `Pattern not found in file: ${regex_pattern}`,
                operation: "regex_edit",
                file_path: originalFilePath,
                resolved_path: fullPath,
                path_resolution_strategy: pathResolution.strategy,
                regex_pattern: regex_pattern,
                replacement_text: replacement_text,
                success: false,
                pattern_not_found: true,
                file_stats: {
                    total_lines: content.split('\n').length,
                    total_characters: content.length
                }
            };

            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(errorResponse, null, 2)
                }]
            };
        }

        // Step 5: Get the match index for more accurate line calculation
        const matchIndex = content.search(regex);
        if (matchIndex === -1) {
            const errorResponse = {
                status: "error",
                message: "Pattern search failed",
                error: `Pattern not found in file: ${regex_pattern}`,
                operation: "regex_edit",
                file_path: originalFilePath,
                resolved_path: fullPath,
                path_resolution_strategy: pathResolution.strategy,
                regex_pattern: regex_pattern,
                replacement_text: replacement_text,
                success: false,
                search_failed: true
            };

            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(errorResponse, null, 2)
                }]
            };
        }

        // Step 6: Apply the replacement
        const updatedContent = content.replace(regex, replacement_text);

        // Step 7: Write the updated content back to file
        try {
            await fs.writeFile(fullPath, updatedContent, 'utf8');
        } catch (writeError) {
            const errorResponse = {
                status: "error",
                message: "Failed to write file",
                error: `Failed to write file: ${writeError.message}`,
                operation: "regex_edit",
                file_path: originalFilePath,
                resolved_path: fullPath,
                path_resolution_strategy: pathResolution.strategy,
                regex_pattern: regex_pattern,
                replacement_text: replacement_text,
                success: false,
                write_failed: true
            };

            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(errorResponse, null, 2)
                }]
            };
        }

        // Step 8: Calculate statistics and prepare success response
        // Find the line where the replacement occurred
        const lines = updatedContent.split('\n');
        const beforeReplacement = content.substring(0, matchIndex);
        const linesBefore = beforeReplacement.split('\n');
        const lineIndex = linesBefore.length - 1;

        const start = Math.max(0, lineIndex - 5);
        const end = Math.min(lines.length, lineIndex + 6);

        const contextLines = lines.slice(start, end);
        const originalMatch = match[0];

        // Calculate statistics
        const originalLines = content.split('\n');
        const changeStats = {
            original_line_count: originalLines.length,
            new_line_count: lines.length,
            lines_changed: Math.abs(lines.length - originalLines.length),
            characters_before: content.length,
            characters_after: updatedContent.length,
            characters_changed: updatedContent.length - content.length,
            match_line_number: lineIndex + 1,
            match_character_position: matchIndex
        };

        const successResponse = {
            status: "success",
            message: `File successfully updated using regex pattern`,
            operation: "regex_edit",
            file_path: originalFilePath,
            resolved_path: fullPath,
            path_resolution_strategy: pathResolution.strategy,
            path_resolution_description: pathResolution.description,
            working_directory: getWorkingDirectory(),
            regex_pattern: regex_pattern,
            replacement_text: replacement_text,
            success: true,
            match_details: {
                original_match: originalMatch,
                match_line: lineIndex + 1,
                match_character_position: matchIndex,
                replacement_applied: replacement_text
            },
            change_statistics: changeStats,
            context_preview: {
                lines_shown: contextLines.length,
                start_line: start + 1,
                end_line: end,
                context_lines: contextLines.join('\n')
            },
            file_info: {
                absolute_path: fullPath,
                relative_path: originalFilePath,
                modification_timestamp: new Date().toISOString()
            }
        };

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(successResponse, null, 2)
            }]
        };
    } catch (error) {
        const errorResponse = {
            status: "error",
            message: "Unexpected error occurred",
            error: `An unexpected error occurred: ${error.message}`,
            operation: "regex_edit",
            file_path: file_path,
            regex_pattern: regex_pattern,
            replacement_text: replacement_text,
            success: false,
            unexpected_error: true,
            error_stack: error.stack,
            working_directory: getWorkingDirectory()
        };

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(errorResponse, null, 2)
            }]
        };
    }
};

export const regexEditTool = {
    name: 'regex_edit',
    description: "Performs a targeted file modification using a regular expression. This tool features robust path resolution that supports multiple path formats (relative/absolute, Windows/Unix) and automatically tries different resolution strategies. It replaces the first occurrence of the pattern with the provided text.",
    args: {
        file_path: z.string().describe('The absolute or relative path to the file that needs to be modified. Supports multiple formats: relative paths (./file.txt, ../dir/file.txt), absolute paths (/full/path, C:\\full\\path), Windows format (C:\\Users\\file.txt), and Unix format (/home/user/file.txt). The tool will automatically try different path resolution strategies.'),
        regex_pattern: z.string().describe("The JavaScript-compatible regular expression pattern to search for within the file. The first match will be targeted for replacement. Remember to escape special characters, e.g., use '\\\\.' to match a literal dot."),
        replacement_text: z.string().describe("The text that will replace the content matched by the `regex_pattern`. Newlines can be included using '\\n'."),
    },
    run: handleRegexEdit,
}; 