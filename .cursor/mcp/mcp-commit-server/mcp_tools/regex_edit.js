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

        const regex = new RegExp(regex_pattern);
        const match = content.match(regex);

        if (!match) {
            return { success: false, error: `Pattern not found in file: ${regex_pattern}` };
        }

        const updatedContent = content.replace(regex, replacement_text);
        await fs.writeFile(fullPath, updatedContent, 'utf8');

        const lines = updatedContent.split('\n');
        const replacementIndex = updatedContent.indexOf(replacement_text);
        let charCount = 0;
        let lineIndex = 0;
        for (let i = 0; i < lines.length; i++) {
            charCount += lines[i].length + 1;
            if (charCount >= replacementIndex) {
                lineIndex = i;
                break;
            }
        }

        const start = Math.max(0, lineIndex - 15);
        const end = Math.min(lines.length, lineIndex + 16);

        const contextLines = lines.slice(start, end);

        return {
            success: true,
            message: `File successfully updated at: ${fullPath}`,
            replacement_zone: {
                before: lines.slice(start, lineIndex).join('\\n'),
                replacement: replacement_text,
                after: lines.slice(lineIndex + 1, end).join('\\n'),
                lines: contextLines.join('\\n'),
            },
        };
    } catch (error) {
        return { success: false, error: `An unexpected error occurred: ${error.message}` };
    }
};

export const regexEditTool = {
    name: 'regex_edit',
    args: z.object({
        file_path: z.string().describe('The path to the file to edit.'),
        regex_pattern: z.string().describe('The regex pattern to find.'),
        replacement_text: z.string().describe('The text to replace the found pattern with.'),
    }),
    run: handleRegexEdit,
}; 