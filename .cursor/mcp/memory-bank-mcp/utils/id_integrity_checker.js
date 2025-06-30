#!/usr/bin/env node

/**
 * ID Integrity Checker and Repair Tool for MCP Memory Bank
 * 
 * This tool validates and repairs duplicate ID issues in:
 * - tasks.json (task IDs)
 * - userbrief.json (request IDs)
 * 
 * Features:
 * - Detects duplicate IDs
 * - Repairs corrupted ID sequences
 * - Creates backups before making changes
 * - Validates data integrity
 * - Provides detailed reports
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// File paths - corrected for the actual project structure
const TASKS_FILE_PATH = path.join(__dirname, '..', '..', '..', 'memory-bank', 'streamlit_app', 'tasks.json');
const USERBRIEF_FILE_PATH = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'userbrief.json');

console.log('🔧 Debug: File paths:');
console.log(`Tasks: ${TASKS_FILE_PATH}`);
console.log(`Userbrief: ${USERBRIEF_FILE_PATH}`);

/**
 * Create a backup of a file with timestamp
 */
async function createBackup(filePath) {
    try {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const backupPath = `${filePath}.backup-${timestamp}`;
        await fs.copyFile(filePath, backupPath);
        console.log(`✅ Backup created: ${backupPath}`);
        return backupPath;
    } catch (error) {
        console.error(`❌ Failed to create backup for ${filePath}: ${error.message}`);
        throw error;
    }
}

/**
 * Validate and repair task IDs
 */
async function validateAndRepairTasks() {
    console.log('\n🔍 Checking tasks.json for ID integrity...');

    try {
        const data = await fs.readFile(TASKS_FILE_PATH, 'utf8');
        const tasks = JSON.parse(data);

        console.log(`📊 Found ${tasks.length} tasks`);

        // Extract IDs and find duplicates
        const ids = tasks.map(t => t.id);
        const uniqueIds = [...new Set(ids)];

        if (ids.length === uniqueIds.size) {
            console.log('✅ No duplicate task IDs found');
            return { needsRepair: false, report: 'Tasks are clean' };
        }

        // Find duplicates
        const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
        const uniqueDuplicates = [...new Set(duplicates)];

        console.log(`❌ Found ${duplicates.length} duplicate task IDs: ${uniqueDuplicates.join(', ')}`);

        // Create backup before repair
        await createBackup(TASKS_FILE_PATH);

        // Repair strategy: reassign IDs to duplicated tasks
        let maxId = Math.max(...ids);
        const repairedTasks = [];
        const seenIds = new Set();

        for (const task of tasks) {
            if (seenIds.has(task.id)) {
                // This is a duplicate, assign new ID
                maxId++;
                const oldId = task.id;
                task.id = maxId;
                console.log(`🔧 Reassigned task ID: ${oldId} → ${maxId} (Title: "${task.title}")`);
            }
            seenIds.add(task.id);
            repairedTasks.push(task);
        }

        // Write repaired data
        await fs.writeFile(TASKS_FILE_PATH, JSON.stringify(repairedTasks, null, 2), 'utf8');

        const report = `Repaired ${duplicates.length} duplicate task IDs. New max ID: ${maxId}`;
        console.log(`✅ ${report}`);

        return { needsRepair: true, report, duplicatesFound: uniqueDuplicates.length };

    } catch (error) {
        console.error(`❌ Error processing tasks.json: ${error.message}`);
        throw error;
    }
}

/**
 * Validate and repair userbrief request IDs
 */
async function validateAndRepairUserbrief() {
    console.log('\n🔍 Checking userbrief.json for ID integrity...');

    try {
        const data = await fs.readFile(USERBRIEF_FILE_PATH, 'utf8');
        const userbrief = JSON.parse(data);

        console.log(`📊 Found ${userbrief.requests.length} requests, last_id: ${userbrief.last_id}`);

        // Extract IDs and find duplicates
        const ids = userbrief.requests.map(r => r.id);
        const uniqueIds = [...new Set(ids)];

        if (ids.length === uniqueIds.size) {
            // Check last_id consistency
            const maxId = ids.length > 0 ? Math.max(...ids) : 0;
            if (userbrief.last_id >= maxId) {
                console.log('✅ No duplicate request IDs found, last_id is consistent');
                return { needsRepair: false, report: 'Userbrief is clean' };
            } else {
                console.log(`⚠️  last_id (${userbrief.last_id}) is inconsistent with max ID (${maxId})`);
                // Repair last_id
                await createBackup(USERBRIEF_FILE_PATH);
                userbrief.last_id = maxId;
                await fs.writeFile(USERBRIEF_FILE_PATH, JSON.stringify(userbrief, null, 2), 'utf8');
                console.log(`🔧 Corrected last_id from ${userbrief.last_id} to ${maxId}`);
                return { needsRepair: true, report: `Corrected last_id to ${maxId}` };
            }
        }

        // Find duplicates
        const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
        const uniqueDuplicates = [...new Set(duplicates)];

        console.log(`❌ Found ${duplicates.length} duplicate request IDs: ${uniqueDuplicates.join(', ')}`);

        // Create backup before repair
        await createBackup(USERBRIEF_FILE_PATH);

        // Repair strategy: reassign IDs to duplicated requests
        let maxId = Math.max(...ids);
        const repairedRequests = [];
        const seenIds = new Set();

        for (const request of userbrief.requests) {
            if (seenIds.has(request.id)) {
                // This is a duplicate, assign new ID
                maxId++;
                const oldId = request.id;
                request.id = maxId;
                console.log(`🔧 Reassigned request ID: ${oldId} → ${maxId} (Content preview: "${request.content.substring(0, 50)}...")`);
            }
            seenIds.add(request.id);
            repairedRequests.push(request);
        }

        // Update userbrief data
        userbrief.requests = repairedRequests;
        userbrief.last_id = maxId;

        // Write repaired data
        await fs.writeFile(USERBRIEF_FILE_PATH, JSON.stringify(userbrief, null, 2), 'utf8');

        const report = `Repaired ${duplicates.length} duplicate request IDs. New last_id: ${maxId}`;
        console.log(`✅ ${report}`);

        return { needsRepair: true, report, duplicatesFound: uniqueDuplicates.length };

    } catch (error) {
        console.error(`❌ Error processing userbrief.json: ${error.message}`);
        throw error;
    }
}

/**
 * Run comprehensive ID integrity check and repair
 */
async function runIntegrityCheck() {
    console.log('🚀 Starting MCP Memory Bank ID Integrity Check...');

    try {
        const taskResult = await validateAndRepairTasks();
        const userbriefResult = await validateAndRepairUserbrief();

        console.log('\n📋 INTEGRITY CHECK SUMMARY:');
        console.log('='.repeat(50));
        console.log(`Tasks: ${taskResult.report}`);
        console.log(`Userbrief: ${userbriefResult.report}`);

        if (taskResult.needsRepair || userbriefResult.needsRepair) {
            console.log('\n⚠️  REPAIRS MADE - Please restart the MCP server for changes to take effect');
            console.log('🔄 Restart command: Stop and start your MCP server');
        } else {
            console.log('\n✅ ALL SYSTEMS CLEAN - No repairs needed');
        }

        return {
            success: true,
            tasksRepaired: taskResult.needsRepair,
            userbriefRepaired: userbriefResult.needsRepair,
            summary: {
                tasks: taskResult.report,
                userbrief: userbriefResult.report
            }
        };

    } catch (error) {
        console.error('\n💥 INTEGRITY CHECK FAILED:', error.message);
        return {
            success: false,
            error: error.message
        };
    }
}

// Run if called directly
if (process.argv[1] && process.argv[1].endsWith('id_integrity_checker.js')) {
    runIntegrityCheck()
        .then(result => {
            process.exit(result.success ? 0 : 1);
        })
        .catch(error => {
            console.error('Fatal error:', error);
            process.exit(1);
        });
}

export { runIntegrityCheck, validateAndRepairTasks, validateAndRepairUserbrief }; 