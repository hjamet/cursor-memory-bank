import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

const handleRegexEdit = async ({ file_path, regex_pattern, replacement_text }) => {
    try {
        const fullPath = path.resolve(file_path);

        let content;
        try {
            content = await fs.readFile(fullPath, 'utf8');
        } catch (error) {
            return { success: false, error: `File not found at path: ${fullPath}` };
        }

        // Validate regex pattern
        let regex;
        try {
            regex = new RegExp(regex_pattern);
        } catch (regexError) {
            return { success: false, error: `Invalid regex pattern: ${regexError.message}` };
        }

        const match = content.match(regex);

        if (!match) {
            return { success: false, error: `Pattern not found in file: ${regex_pattern}` };
        }

        // Get the match index for more accurate line calculation
        const matchIndex = content.search(regex);
        if (matchIndex === -1) {
            return { success: false, error: `Pattern not found in file: ${regex_pattern}` };
        }

        const updatedContent = content.replace(regex, replacement_text);

        try {
            await fs.writeFile(fullPath, updatedContent, 'utf8');
        } catch (writeError) {
            return { success: false, error: `Failed to write file: ${writeError.message}` };
        }

        // Find the line where the replacement occurred
        const lines = updatedContent.split('\n');
        const beforeReplacement = content.substring(0, matchIndex);
        const linesBefore = beforeReplacement.split('\n');
        const lineIndex = linesBefore.length - 1;

        const start = Math.max(0, lineIndex - 5);
        const end = Math.min(lines.length, lineIndex + 6);

        const contextLines = lines.slice(start, end);

        return {
            success: true,
            message: `File successfully updated at: ${fullPath}`,
            replacement_zone: {
                before: lines.slice(start, lineIndex).join('\n'),
                replacement: replacement_text,
                after: lines.slice(lineIndex + 1, end).join('\n'),
                lines: contextLines.join('\n'),
            },
        };
    } catch (error) {
        return { success: false, error: `An unexpected error occurred: ${error.message}` };
    }
};

export const regexEditTool = {
    name: 'mcp_ToolsMCP_regex_edit',
    description: "Performs a targeted file modification using a regular expression. This tool is a robust, non-model-based alternative to 'edit_file', ideal for precise changes where the exact location can be identified by a regex pattern. It replaces the first occurrence of the pattern with the provided text.",
    args: {
        file_path: z.string().describe('The absolute or relative path to the file that needs to be modified.'),
        regex_pattern: z.string().describe("The JavaScript-compatible regular expression pattern to search for within the file. The first match will be targeted for replacement. Remember to escape special characters, e.g., use '\\\\.' to match a literal dot."),
        replacement_text: z.string().describe("The text that will replace the content matched by the `regex_pattern`. Newlines can be included using '\\n'."),
    },
    run: handleRegexEdit,
}; 