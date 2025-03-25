#!/bin/bash

# Script de test pour vérifier la structure des dossiers
# Ce script teste que la nouvelle organisation avec src/ et tests/ est correctement mise en place

set -e  # Arrêter le script si une commande échoue

echo "===== Démarrage des tests de structure ====="

# Vérification de l'existence des dossiers src/ et tests/
echo "Test 1: Vérification de l'existence du dossier src/"
if [ -d "src" ]; then
    echo "✅ Le dossier src/ existe"
else
    echo "❌ Le dossier src/ n'existe pas"
    exit 1
fi

echo "Test 2: Vérification de l'existence du dossier tests/"
if [ -d "tests" ]; then
    echo "✅ Le dossier tests/ existe"
else
    echo "❌ Le dossier tests/ n'existe pas"
    exit 1
fi

# Vérification de la présence des scripts dans les bons dossiers
echo "Test 3: Vérification de la présence du script install.sh dans src/"
if [ -f "src/install.sh" ]; then
    echo "✅ Le script install.sh est bien dans le dossier src/"
else
    echo "❌ Le script install.sh n'est pas dans le dossier src/"
    exit 1
fi

echo "Test 4: Vérification de la présence du script test_install.sh dans tests/"
if [ -f "tests/test_install.sh" ]; then
    echo "✅ Le script test_install.sh est bien dans le dossier tests/"
else
    echo "❌ Le script test_install.sh n'est pas dans le dossier tests/"
    exit 1
fi

# Vérification des permissions d'exécution
echo "Test 5: Vérification des permissions d'exécution de src/install.sh"
if [ -x "src/install.sh" ]; then
    echo "✅ Le script src/install.sh est exécutable"
else
    echo "❌ Le script src/install.sh n'est pas exécutable"
    exit 1
fi

echo "Test 6: Vérification des permissions d'exécution de tests/test_install.sh"
if [ -x "tests/test_install.sh" ]; then
    echo "✅ Le script tests/test_install.sh est exécutable"
else
    echo "❌ Le script tests/test_install.sh n'est pas exécutable"
    exit 1
fi

# Vérification des règles mises à jour
echo "Test 7: Vérification de la mise à jour de system.mdc"
if grep -q "APPEL OBLIGATOIRE DE LA RÈGLE SUIVANTE" .cursor/rules/system.mdc; then
    echo "✅ Le fichier system.mdc a été correctement mis à jour"
else
    echo "❌ Le fichier system.mdc n'a pas été correctement mis à jour"
    exit 1
fi

echo "Test 8: Vérification de la mise à jour de implementation.mdc"
if grep -q "4. Appeler obligatoirement la règle suivante:" .cursor/rules/implementation.mdc; then
    echo "✅ Le fichier implementation.mdc a été correctement mis à jour"
else
    echo "❌ Le fichier implementation.mdc n'a pas été correctement mis à jour"
    exit 1
fi

# Vérification de context-update.mdc et tests.mdc
echo "Test 9: Vérification de la mise à jour de context-update.mdc"
if grep -q "6. Appeler obligatoirement la règle suivante si le workflow n'est pas terminé:" .cursor/rules/context-update.mdc; then
    echo "✅ Le fichier context-update.mdc a été correctement mis à jour"
else
    echo "❌ Le fichier context-update.mdc n'a pas été correctement mis à jour"
    exit 1
fi

echo "Test 10: Vérification de la mise à jour de tests.mdc"
if grep -q "5. Appeler obligatoirement la règle suivante:" .cursor/rules/tests.mdc; then
    echo "✅ Le fichier tests.mdc a été correctement mis à jour"
else
    echo "❌ Le fichier tests.mdc n'a pas été correctement mis à jour"
    exit 1
fi

echo "===== Tous les tests de structure ont réussi! =====" 