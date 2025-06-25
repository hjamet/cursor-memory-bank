import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

const handleRegexEdit = async ({ file_path, regex_pattern, replacement_text }) => {
    try {
        const fullPath = path.resolve(file_path);
        const originalFilePath = file_path; // Keep original for response

        let content;
        try {
            content = await fs.readFile(fullPath, 'utf8');
        } catch (error) {
            const errorResponse = {
                status: "error",
                message: "File not found",
                error: `File not found at path: ${fullPath}`,
                operation: "regex_edit",
                file_path: originalFilePath,
                resolved_path: fullPath,
                regex_pattern: regex_pattern,
                replacement_text: replacement_text,
                success: false
            };

            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(errorResponse, null, 2)
                }]
            };
        }

        // Validate regex pattern
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

        const match = content.match(regex);

        if (!match) {
            const errorResponse = {
                status: "error",
                message: "Pattern not found in file",
                error: `Pattern not found in file: ${regex_pattern}`,
                operation: "regex_edit",
                file_path: originalFilePath,
                resolved_path: fullPath,
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

        // Get the match index for more accurate line calculation
        const matchIndex = content.search(regex);
        if (matchIndex === -1) {
            const errorResponse = {
                status: "error",
                message: "Pattern search failed",
                error: `Pattern not found in file: ${regex_pattern}`,
                operation: "regex_edit",
                file_path: originalFilePath,
                resolved_path: fullPath,
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

        const updatedContent = content.replace(regex, replacement_text);

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
            error_stack: error.stack
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
    description: "Performs a targeted file modification using a regular expression. This tool is a robust, non-model-based alternative to 'edit_file', ideal for precise changes where the exact location can be identified by a regex pattern. It replaces the first occurrence of the pattern with the provided text.",
    args: {
        file_path: z.string().describe('The absolute or relative path to the file that needs to be modified.'),
        regex_pattern: z.string().describe("The JavaScript-compatible regular expression pattern to search for within the file. The first match will be targeted for replacement. Remember to escape special characters, e.g., use '\\\\.' to match a literal dot."),
        replacement_text: z.string().describe("The text that will replace the content matched by the `regex_pattern`. Newlines can be included using '\\n'."),
    },
    run: handleRegexEdit,
}; 