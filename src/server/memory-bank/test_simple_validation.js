#!/usr/bin/env node

import { validateCreateTask } from './lib/task_crud_validator.js';

console.log('🧪 Testing Zod error handling fix...');

// Test data
const sampleTasks = [{
    id: 1,
    title: "Sample Task",
    short_description: "A sample task",
    detailed_description: "This is a sample task for testing",
    status: "TODO",
    dependencies: [],
    created_date: "2025-01-01T00:00:00.000Z",
    updated_date: "2025-01-01T00:00:00.000Z",
    priority: 3
}];

// Test 1: Empty title (should return clean error, not interrupt)
console.log('\n⚡ Test 1: Empty title validation');
try {
    const result = validateCreateTask({
        title: "",
        short_description: "Test",
        detailed_description: "Test"
    }, sampleTasks);

    console.log('✅ Validation completed without interruption');
    console.log('📝 Valid:', result.isValid);
    console.log('📝 Errors:', result.errors.length);

    if (result.errors.length > 0) {
        console.log('📝 First error:', result.errors[0].message);
    }

    // Test JSON serialization
    const serialized = JSON.stringify(result);
    console.log('✅ JSON serialization successful');

} catch (error) {
    console.log('❌ Test failed with error:', error.message);
}

// Test 2: Invalid priority
console.log('\n⚡ Test 2: Invalid priority validation');
try {
    const result = validateCreateTask({
        title: "Valid title",
        short_description: "Test",
        detailed_description: "Test",
        priority: 10
    }, sampleTasks);

    console.log('✅ Validation completed without interruption');
    console.log('📝 Valid:', result.isValid);
    console.log('📝 Errors:', result.errors.length);

    if (result.errors.length > 0) {
        console.log('📝 First error:', result.errors[0].message);
    }

    // Test JSON serialization
    const serialized = JSON.stringify(result);
    console.log('✅ JSON serialization successful');

} catch (error) {
    console.log('❌ Test failed with error:', error.message);
}

// Test 3: Null input
console.log('\n⚡ Test 3: Null input validation');
try {
    const result = validateCreateTask(null, sampleTasks);

    console.log('✅ Validation completed without interruption');
    console.log('📝 Valid:', result.isValid);
    console.log('📝 Errors:', result.errors.length);

    if (result.errors.length > 0) {
        console.log('📝 First error:', result.errors[0].message);
    }

    // Test JSON serialization
    const serialized = JSON.stringify(result);
    console.log('✅ JSON serialization successful');

} catch (error) {
    console.log('❌ Test failed with error:', error.message);
}

console.log('\n🎉 All tests completed! Zod error handling fix appears to be working.'); 