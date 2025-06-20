import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const workflowDirPath = path.join(__dirname, '..', '..', '..', 'workflow');

async function next_rule(args) {
    const { rule_name } = args;
    const ruleFilePath = path.join(workflowDirPath, `${rule_name}.md`);

    try {
        const data = await fs.readFile(ruleFilePath, 'utf8');
        return {
            rule_name: rule_name,
            instructions: data,
        };
    } catch (error) {
        if (error.code === 'ENOENT') {
            throw new Error(`Rule file not found: ${rule_name}.md`);
        }
        throw new Error(`Failed to read rule file: ${error.message}`);
    }
}

const nextRuleTool = {
    name: "next_rule",
    description: "Takes a selected next rule name, reads the corresponding markdown file from the workflow directory, and returns its instructions.",
    args: z.object({
        rule_name: z.string().describe("The name of the rule to execute next (without the .md extension)."),
    }),
    run: next_rule,
};

export const nextRuleSchema = z.object({
    rule_name: z.string().describe("The name of the rule to execute next (without the .md extension)."),
});

export { next_rule as handleNextRule }; 