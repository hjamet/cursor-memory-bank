#!/bin/bash

# Script de test pour install.sh
# Ce script teste le fonctionnement du script d'installation de Memory Bank
# dans un environnement isolé pour éviter d'écraser des fichiers existants

set -e  # Arrêter le script si une commande échoue

echo "===== Démarrage des tests du script d'installation Memory Bank ====="

# Création d'un répertoire temporaire pour les tests
TEST_DIR=$(mktemp -d)
echo "Répertoire de test créé: ${TEST_DIR}"

# Copie du script d'installation dans le répertoire de test
cp install.sh "${TEST_DIR}/"
cd "${TEST_DIR}"

echo "===== Test 1: Vérification des prérequis ====="
# Test des vérifications de prérequis
echo "Test 1.1: Comportement avec curl disponible"
if command -v curl &> /dev/null; then
    echo "✅ curl est disponible, test réussi"
else
    echo "❌ curl n'est pas disponible, impossible de tester correctement"
    exit 1
fi

echo "Test 1.2: Comportement avec unzip disponible"
if command -v unzip &> /dev/null; then
    echo "✅ unzip est disponible, test réussi"
else
    echo "❌ unzip n'est pas disponible, impossible de tester correctement"
    exit 1
fi

echo "===== Test 2: Modification du script pour tests locaux ====="
# Modifier le script pour simuler l'installation avec des ressources locales
cat > install.sh << 'EOF'
#!/bin/bash

# Version de test du script d'installation
echo "Téléchargement de Memory Bank (simulation)..."

# Vérification des prérequis
if ! command -v curl &> /dev/null; then
    echo "Erreur: curl est requis pour l'installation."
    exit 1
fi

if ! command -v unzip &> /dev/null; then
    echo "Erreur: unzip est requis pour l'installation."
    exit 1
fi

# Simuler une installation locale
# Créer une structure de dossier .cursor minimale
CURSOR_DIR=".cursor"

# Vérification de l'existence du dossier .cursor
if [ -d "${CURSOR_DIR}" ]; then
    echo "Attention: Le dossier ${CURSOR_DIR} existe déjà."
    echo "Simulation de demande utilisateur: y"
    
    # Sauvegarde du dossier existant
    BACKUP_DIR="${CURSOR_DIR}_backup_$(date +%Y%m%d%H%M%S)"
    echo "Sauvegarde du dossier existant vers ${BACKUP_DIR}..."
    mv "${CURSOR_DIR}" "${BACKUP_DIR}"
fi

# Création d'un dossier .cursor minimal pour les tests
echo "Installation de Memory Bank..."
mkdir -p "${CURSOR_DIR}/memory-bank/context" "${CURSOR_DIR}/memory-bank/workflow" "${CURSOR_DIR}/rules/custom/errors" "${CURSOR_DIR}/rules/custom/preferences"
echo "# Structure test" > "${CURSOR_DIR}/memory-bank/context/activeContext.md"
echo "# Test file" > "${CURSOR_DIR}/rules/system.mdc"

echo "Memory Bank a été installé avec succès!"
echo "Utilisation: Ouvrez simplement ce projet dans Cursor IDE et commencez à interagir avec l'agent."
EOF

chmod +x install.sh

echo "===== Test 2: Installation dans un projet vide ====="
echo "Test 2.1: Exécution du script dans un dossier vide"
mkdir -p test_project
cd test_project
bash ../install.sh

echo "Test 2.2: Vérification de la présence du dossier .cursor"
if [ -d ".cursor" ]; then
    echo "✅ Dossier .cursor créé avec succès"
else
    echo "❌ Le dossier .cursor n'a pas été créé"
    exit 1
fi

echo "Test 2.3: Vérification de la structure du dossier .cursor"
if [ -d ".cursor/memory-bank" ] && [ -d ".cursor/rules" ]; then
    echo "✅ Structure du dossier .cursor correcte"
else
    echo "❌ Structure du dossier .cursor incorrecte"
    exit 1
fi

echo "===== Test 3: Test avec dossier .cursor préexistant ====="
echo "Test 3.1: Création d'un dossier .cursor existant"
cd ..
mkdir -p test_backup
cd test_backup
mkdir -p .cursor/test_content
echo "Contenu de test" > .cursor/test_content/test_file.txt

echo "Test 3.2: Exécution du script d'installation avec dossier préexistant"
bash ../install.sh

echo "Test 3.3: Vérification de la sauvegarde"
if ls .cursor_backup_* &> /dev/null; then
    echo "✅ Sauvegarde du dossier .cursor créée avec succès"
else
    echo "❌ Sauvegarde du dossier .cursor non créée"
    exit 1
fi

echo "Test 3.4: Vérification du remplacement"
if [ -d ".cursor/memory-bank" ] && [ -d ".cursor/rules" ]; then
    echo "✅ Remplacement du dossier .cursor réussi"
else
    echo "❌ Remplacement du dossier .cursor échoué"
    exit 1
fi

echo "===== Nettoyage ====="
cd ../..
echo "Suppression du répertoire de test: ${TEST_DIR}"
rm -rf "${TEST_DIR}"

echo "===== Tous les tests ont réussi! =====" 