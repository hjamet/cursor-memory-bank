import puppeteer from 'puppeteer';

/**
 * MCP Tool handler for taking a full webpage screenshot.
 * @param {object} params - Parameters object.
 * @param {string} params.url - URL of the webpage to screenshot.
 * @returns {Promise<{ content: Array<{type: string, text?: string, data?: string, mimeType?: string}>> }>} - MCP response object.
 */
export async function handleWebpageScreenshot(params) {
    const { url } = params;

    if (!url || typeof url !== 'string') {
        return { content: [{ type: 'text', text: 'Error: Missing or invalid \'url\' parameter.' }] };
    }

    let browser;
    try {
        // Launch Puppeteer
        // Note: In some environments (like Docker), you might need to pass { args: ['--no-sandbox', '--disable-setuid-sandbox'] } to launch
        browser = await puppeteer.launch();
        const page = await browser.newPage();

        // Set a reasonable viewport for a full page screenshot, though fullPage overrides this for height.
        await page.setViewport({ width: 1920, height: 1080 });

        // Navigate to the URL
        await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 }); // Wait until network is idle, 60s timeout

        // Take screenshot as base64
        const base64Data = await page.screenshot({ encoding: 'base64', fullPage: true });

        await browser.close();

        return {
            content: [
                {
                    type: "image",
                    data: base64Data,
                    mimeType: "image/png", // Puppeteer defaults to png for screenshots
                },
            ]
        };
    } catch (error) {
        if (browser) {
            await browser.close();
        }
        console.error(`[webpage_screenshot] Error processing URL ${url}:`, error);
        return {
            content: [{
                type: 'text',
                text: `Error taking screenshot for URL '${url}'. Details: ${error.message}`
            }]
        };
    }
} 