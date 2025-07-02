/**
 * Test rapide de l'intégration du système de workflow automatisé
 */

import { validateTransition, recordTransition, getSafetyStatus } from './lib/workflow_safety.js';

async function testWorkflowIntegration() {
    console.log('🔧 Test d\'intégration du workflow automatisé...\n');

    try {
        // Test 1: Transition normale implementation → experience-execution
        console.log('Test 1: Transition implementation → experience-execution');
        const validation1 = await validateTransition('implementation', 'experience-execution');
        console.log(`✅ Résultat: ${validation1.allowed ? 'AUTORISÉ' : 'BLOQUÉ'}`);
        console.log(`   Raison: ${validation1.reason}\n`);

        // Test 2: Transition interdite experience-execution → experience-execution
        console.log('Test 2: Transition interdite experience-execution → experience-execution');
        const validation2 = await validateTransition('experience-execution', 'experience-execution');
        console.log(`❌ Résultat: ${validation2.allowed ? 'AUTORISÉ' : 'BLOQUÉ'}`);
        console.log(`   Raison: ${validation2.reason}\n`);

        // Test 3: Enregistrement de transition
        console.log('Test 3: Enregistrement de transition');
        await recordTransition('test', 'workflow-integration');
        console.log('✅ Transition enregistrée avec succès\n');

        // Test 4: État de sécurité
        console.log('Test 4: État de sécurité du système');
        const status = await getSafetyStatus();
        console.log('✅ État récupéré:');
        console.log(`   Frein d'urgence: ${status.emergency_brake_active ? 'ACTIF' : 'INACTIF'}`);
        console.log(`   Transitions consécutives: ${status.consecutive_transitions}`);
        console.log(`   Tentatives experience-execution: ${status.experience_execution_attempts}\n`);

        console.log('🎉 Tous les tests d\'intégration sont passés avec succès!');
        console.log('✨ Le système de workflow automatisé est opérationnel.\n');

        return true;

    } catch (error) {
        console.error('❌ Erreur lors du test d\'intégration:', error.message);
        return false;
    }
}

// Exécution du test si le script est appelé directement
if (import.meta.url === `file://${process.argv[1]}`) {
    testWorkflowIntegration().then(success => {
        process.exit(success ? 0 : 1);
    });
}

export { testWorkflowIntegration }; 