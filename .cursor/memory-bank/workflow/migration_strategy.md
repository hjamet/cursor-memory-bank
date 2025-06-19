# Task Migration Strategy: Markdown to JSON

## Overview
This document outlines the strategy for migrating the existing `tasks.md` file to the new JSON-based task management system while preserving all existing information and relationships.

## Current Format Analysis

### Emoji Status Mapping
- ⚪️ TODO → "TODO"
- 🟡 IN_PROGRESS → "IN_PROGRESS"  
- 🟢 DONE → "DONE"
- 🔴 BLOCKED → "BLOCKED"
- 🔵 REVIEW → "REVIEW"

### Task Structure Patterns
1. **Main Tasks**: `🟢 **1. Task Title**`
2. **Sub-Tasks**: `    *   🟢 **1.1. Sub-Task Title**`
3. **Fields**: Description, Impacted Rules/Files, Dependencies, Validation

## Migration Process

### Phase 1: Parsing
1. **Line-by-line Analysis**: Parse markdown to identify task boundaries
2. **Hierarchy Detection**: Identify main tasks vs sub-tasks based on indentation
3. **Field Extraction**: Extract Description, Impacted Rules/Files, Dependencies, Validation
4. **Status Recognition**: Map emoji status to JSON status enum

### Phase 2: ID Assignment
1. **Sequential IDs**: Assign incrementing integer IDs starting from 1
2. **Parent-Child Relationships**: Link sub-tasks to parent tasks via parent_id
3. **Dependency Mapping**: Convert textual dependencies to ID references

### Phase 3: Data Transformation
1. **Title Extraction**: Extract clean title from markdown bold formatting
2. **Description Processing**: 
   - Short description: First sentence or summary
   - Detailed description: Full description content
3. **File Lists**: Convert "Impacted Rules/Files" to impacted_files array
4. **Validation**: Map validation criteria to validation_criteria field

### Phase 4: Dependency Resolution
1. **Reference Analysis**: Identify dependency patterns (e.g., "Task 12", "12.1", etc.)
2. **ID Mapping**: Convert textual references to actual task IDs
3. **Validation**: Ensure all dependency IDs exist and are valid
4. **Circular Detection**: Check for and report circular dependencies

## Data Preservation Strategy

### Information Mapping
- **Task Number** → `id`
- **Task Title** → `title`
- **Description first sentence** → `short_description`
- **Full Description** → `detailed_description`
- **Emoji Status** → `status`
- **Dependencies text** → `dependencies` array
- **Impacted Rules/Files** → `impacted_files` array
- **Validation** → `validation_criteria`

### Metadata Generation
- **created_date**: Use current timestamp for migration
- **updated_date**: Use current timestamp for migration
- **priority**: Default to 3 (medium) for all tasks
- **parent_id**: Set for sub-tasks based on hierarchy

## Backward Compatibility

### Dual Format Support
1. **Primary Format**: JSON for programmatic access
2. **Generated Markdown**: Auto-generate tasks.md from JSON for human readability
3. **Rule Updates**: Gradually migrate rules to use MCP tools instead of direct file reading

### Migration Validation
1. **Data Integrity**: Verify all original information is preserved
2. **Relationship Integrity**: Ensure all dependencies are correctly mapped
3. **Status Consistency**: Confirm emoji-to-status mapping is accurate
4. **Completeness**: Verify no tasks are lost during migration

## Risk Mitigation
1. **Backup**: Create backup of original tasks.md before migration
2. **Validation**: Comprehensive validation of migrated data
3. **Rollback Plan**: Ability to restore from backup if migration fails
4. **Testing**: Thorough testing of all task management operations post-migration 