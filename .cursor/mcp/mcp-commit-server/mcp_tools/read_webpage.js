import puppeteer from 'puppeteer';
import TurndownService from 'turndown';

const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
    bulletListMarker: '-',
    emDelimiter: '_'
});

/**
 * Reads and converts a webpage URL to Markdown format for content analysis
 * @param {Object} args - Tool arguments
 * @param {string} args.url - URL of the webpage to convert
 * @returns {Promise<Object>} Response object with content array
 */
export async function handleReadWebpage(args) {
    const { url } = args;

    let browser;

    try {
        // Launch Puppeteer browser
        browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]
        });

        const page = await browser.newPage();

        // Set user agent to avoid bot detection
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');

        // Navigate to URL with timeout
        await page.goto(url, {
            waitUntil: 'networkidle2',
            timeout: 30000
        });

        // Extract the page content
        const content = await page.evaluate(() => {
            // Remove script and style elements
            const scripts = document.querySelectorAll('script, style, noscript');
            scripts.forEach(el => el.remove());

            // Get the main content or body
            const main = document.querySelector('main, article, .content, .post, .entry') || document.body;

            return {
                title: document.title || '',
                html: main.innerHTML || ''
            };
        });

        // Convert HTML to Markdown
        const markdown = turndownService.turndown(content.html);

        // Format the final output
        const formattedMarkdown = `# ${content.title}\n\nSource: ${url}\n\n${markdown}`;

        return {
            content: [
                {
                    type: 'text',
                    text: formattedMarkdown
                }
            ]
        };

    } catch (error) {
        const errorMessage = `Failed to convert URL to Markdown: ${error.message}`;

        return {
            content: [
                {
                    type: 'text',
                    text: errorMessage
                }
            ]
        };

    } finally {
        // Always close browser if it was opened
        if (browser) {
            try {
                await browser.close();
            } catch (closeError) {
                console.error('Error closing browser:', closeError);
            }
        }
    }
} 