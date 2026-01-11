import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const USER_MESSAGES_PATH = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'to_user.json');
const MAX_MESSAGES = 100; // Limit to prevent file from growing indefinitely

class UserMessageManager {
    constructor() {
        this.messagesPath = USER_MESSAGES_PATH;
    }

    async ensureDirectoryExists() {
        try {
            await fs.mkdir(path.dirname(this.messagesPath), { recursive: true });
        } catch (error) {
            throw new Error(`Failed to create directory: ${error.message}`);
        }
    }

    async readMessages() {
        try {
            const data = await fs.readFile(this.messagesPath, 'utf8');
            const parsed = JSON.parse(data);

            // Ensure we have the expected structure
            if (!parsed.version || !Array.isArray(parsed.messages)) {
                return {
                    version: "1.0.0",
                    messages: [],
                    last_id: 0
                };
            }

            return parsed;
        } catch (error) {
            if (error.code === 'ENOENT') {
                // File doesn't exist, return empty structure
                return {
                    version: "1.0.0",
                    messages: [],
                    last_id: 0
                };
            }
            throw new Error(`Failed to read user messages file: ${error.message}`);
        }
    }

    async writeMessages(data) {
        try {
            await this.ensureDirectoryExists();
            await fs.writeFile(this.messagesPath, JSON.stringify(data, null, 2), 'utf8');
        } catch (error) {
            throw new Error(`Failed to write user messages file: ${error.message}`);
        }
    }

    async addMessage(content, context = {}) {
        if (!content || typeof content !== 'string' || content.trim().length === 0) {
            throw new Error('Message content is required and must be a non-empty string');
        }

        // Limit message length (1-2 sentences as specified)
        if (content.length > 500) {
            throw new Error('Message content is too long (max 500 characters for 1-2 sentences)');
        }

        const data = await this.readMessages();

        const newMessage = {
            id: data.last_id + 1,
            content: content.trim(),
            timestamp: new Date().toISOString(),
            context: {
                workflow_rule: context.workflow_rule || 'unknown',
                active_task: context.active_task || null,
                agent_state: context.agent_state || 'unknown',
                ...context
            },
            status: 'unread'
        };

        data.messages.push(newMessage);
        data.last_id = newMessage.id;

        // Limit the number of messages to prevent infinite growth
        if (data.messages.length > MAX_MESSAGES) {
            data.messages = data.messages.slice(-MAX_MESSAGES);
        }

        await this.writeMessages(data);

        return {
            success: true,
            message_id: newMessage.id,
            message: `User message recorded successfully (ID: ${newMessage.id})`
        };
    }

    async getMessages(limit = 50) {
        const data = await this.readMessages();

        // Return messages sorted by most recent first
        const sortedMessages = data.messages
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, limit);

        return {
            messages: sortedMessages,
            total_count: data.messages.length,
            unread_count: data.messages.filter(m => m.status === 'unread').length
        };
    }

    async markAsRead(messageId) {
        const data = await this.readMessages();
        const message = data.messages.find(m => m.id === messageId);

        if (!message) {
            throw new Error(`Message with ID ${messageId} not found`);
        }

        message.status = 'read';
        message.read_at = new Date().toISOString();

        await this.writeMessages(data);

        return {
            success: true,
            message: `Message ${messageId} marked as read`
        };
    }

    async deleteMessage(messageId) {
        const data = await this.readMessages();
        const messageIndex = data.messages.findIndex(m => m.id === messageId);

        if (messageIndex === -1) {
            throw new Error(`Message with ID ${messageId} not found`);
        }

        const deletedMessage = data.messages.splice(messageIndex, 1)[0];
        await this.writeMessages(data);

        return {
            success: true,
            message: `Message ${messageId} deleted successfully`,
            deleted_message: deletedMessage
        };
    }
}

export { UserMessageManager }; 