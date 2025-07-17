import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Test version of scanCodeFiles function
 */
function scanCodeFiles(dirPath, rootPath = dirPath) {
    const results = [];
    const MAX_LINES = 500;

    // Supported file extensions (matching the requirements)
    const SUPPORTED_EXTENSIONS = ['.py', '.js', '.tex', '.html', '.css', '.sh'];

    try {
        const entries = fs.readdirSync(dirPath, { withFileTypes: true });

        for (const entry of entries) {
            const fullPath = path.join(dirPath, entry.name);

            if (entry.isDirectory()) {
                // Skip common directories that shouldn't be scanned
                const skipDirs = ['node_modules', '.git', '__pycache__', '.venv', 'venv', '.env'];
                if (!skipDirs.includes(entry.name)) {
                    results.push(...scanCodeFiles(fullPath, rootPath));
                }
            } else if (entry.isFile()) {
                // Check if file has a supported extension
                const hasValidExtension = SUPPORTED_EXTENSIONS.some(ext => entry.name.endsWith(ext));

                if (hasValidExtension) {
                    const relativePath = path.relative(rootPath, fullPath);

                    // CRITICAL EXCEPTION: Never scan install.sh from this repository
                    if (relativePath === 'install.sh' || relativePath.endsWith('/install.sh')) {
                        console.log(`⚠️  SKIPPED: ${relativePath} (install.sh exception)`);
                        continue;
                    }

                    try {
                        const content = fs.readFileSync(fullPath, 'utf8');
                        const lineCount = content.split('\n').length;

                        const fileInfo = {
                            file: relativePath,
                            lines: lineCount,
                            oversized: lineCount > MAX_LINES,
                            extension: path.extname(entry.name).toLowerCase()
                        };

                        results.push(fileInfo);

                        // Log for testing
                        const status = fileInfo.oversized ? '🔴 OVERSIZED' : '✅ OK';
                        console.log(`${status}: ${relativePath} (${lineCount} lines, ${fileInfo.extension})`);
                    } catch (fileError) {
                        console.error(`❌ Error reading file ${fullPath}:`, fileError.message);
                    }
                }
            }
        }
    } catch (dirError) {
        console.error(`❌ Error reading directory ${dirPath}:`, dirError.message);
    }

    return results;
}

// Test the function
console.log('🧪 Testing enhanced file scanner...\n');

const projectRoot = process.cwd();
console.log(`📁 Scanning directory: ${projectRoot}\n`);

const results = scanCodeFiles(projectRoot);

console.log('\n📊 SCAN RESULTS:');
console.log(`Total files scanned: ${results.length}`);
console.log(`Oversized files (>500 lines): ${results.filter(f => f.oversized).length}`);

// Group by extension
const byExtension = results.reduce((acc, file) => {
    const ext = file.extension;
    if (!acc[ext]) acc[ext] = [];
    acc[ext].push(file);
    return acc;
}, {});

console.log('\n📋 Files by extension:');
Object.entries(byExtension).forEach(([ext, files]) => {
    const oversized = files.filter(f => f.oversized).length;
    console.log(`  ${ext}: ${files.length} files (${oversized} oversized)`);
});

if (results.filter(f => f.oversized).length > 0) {
    console.log('\n🔴 Oversized files detected:');
    results.filter(f => f.oversized).forEach(file => {
        console.log(`  • ${file.file}: ${file.lines} lines (${file.extension})`);
    });
}

console.log('\n✅ Test completed!'); 