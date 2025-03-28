#!/bin/bash

# Test du script d'installation avec git clone
#
# Ce fichier contient les tests pour l'installation via git clone.
#
# Prérequis:
# - git installé
# - bash 4.0+
# - Accès internet pour cloner le dépôt
#
# Exécution:
# ./test_git_install.sh
#
# Résultats attendus:
# - Installation réussie avec git clone
# - Préservation des règles personnalisées
# - Gestion correcte des erreurs
# - Options de ligne de commande fonctionnelles

set -e
set -u

# Constantes
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_SCRIPT="$SCRIPT_DIR/../install.sh"
TEST_DIR=""  # Sera défini par setup()
CUSTOM_RULE="custom/test-rule.md"

# Fonctions utilitaires
setup() {
    TEST_DIR=$(mktemp -d)
    if [[ ! -d "$TEST_DIR" ]]; then
        echo "Failed to create temporary directory"
        exit 1
    fi
}

cleanup() {
    if [[ -n "$TEST_DIR" && -d "$TEST_DIR" ]]; then
        rm -rf "$TEST_DIR"
    fi
}

assert_success() {
    if [[ $? -ne 0 ]]; then
        echo "Test failed: $1"
        exit 1
    fi
}

assert_failure() {
    if [[ $? -eq 0 ]]; then
        echo "Test failed: $1"
        exit 1
    fi
}

assert_file_exists() {
    if [[ ! -f "$1" ]]; then
        echo "Test failed: File $1 does not exist"
        exit 1
    fi
}

assert_dir_exists() {
    if [[ ! -d "$1" ]]; then
        echo "Test failed: Directory $1 does not exist"
        exit 1
    fi
}

# Tests
test_basic_installation() {
    echo "Test: Installation de base"
    setup
    bash "$INSTALL_SCRIPT" --dir "$TEST_DIR" --force
    assert_success "L'installation de base a échoué"
    assert_dir_exists "$TEST_DIR/.cursor/rules"
    assert_dir_exists "$TEST_DIR/.cursor/rules/custom"
    cleanup
}

test_preserve_custom_rules() {
    echo "Test: Préservation des règles personnalisées"
    setup
    # Créer une règle personnalisée avant l'installation
    mkdir -p "$TEST_DIR/.cursor/rules/custom"
    echo "Test custom rule" > "$TEST_DIR/.cursor/rules/$CUSTOM_RULE"
    # Installer avec --force pour permettre l'installation
    bash "$INSTALL_SCRIPT" --dir "$TEST_DIR" --force
    assert_success "L'installation avec règles personnalisées a échoué"
    assert_file_exists "$TEST_DIR/.cursor/rules/$CUSTOM_RULE"
    cleanup
}

test_no_backup_option() {
    echo "Test: Option --no-backup"
    setup
    # Créer une règle personnalisée avant l'installation
    mkdir -p "$TEST_DIR/.cursor/rules/custom"
    echo "Test custom rule" > "$TEST_DIR/.cursor/rules/$CUSTOM_RULE"
    # Installer avec --force et --no-backup
    bash "$INSTALL_SCRIPT" --dir "$TEST_DIR" --force --no-backup
    assert_success "L'installation avec --no-backup a échoué"
    # Vérifier qu'aucun fichier de backup n'a été créé
    backup_files=$(find "$TEST_DIR/.cursor" -name "rules.bak-*" | wc -l)
    if [[ $backup_files -ne 0 ]]; then
        echo "Test failed: Des fichiers de backup ont été créés malgré --no-backup"
        exit 1
    fi
    cleanup
}

test_force_option() {
    echo "Test: Option --force"
    setup
    # Première installation
    bash "$INSTALL_SCRIPT" --dir "$TEST_DIR"
    assert_success "La première installation a échoué"
    
    # Deuxième installation sans --force (doit réussir maintenant avec notre nouvelle logique)
    bash "$INSTALL_SCRIPT" --dir "$TEST_DIR" 2>/dev/null
    assert_success "L'installation sans --force aurait dû réussir avec la nouvelle logique"
    
    # Vérifier que les règles existent toujours
    assert_dir_exists "$TEST_DIR/.cursor/rules"
    
    # Troisième installation avec --force (doit également réussir)
    bash "$INSTALL_SCRIPT" --dir "$TEST_DIR" --force
    assert_success "L'installation avec --force a échoué"
    cleanup
}

test_invalid_directory() {
    echo "Test: Répertoire invalide"
    # Capture la sortie d'erreur dans une variable
    local error_output
    error_output=$(bash "$INSTALL_SCRIPT" --dir "/nonexistent/directory" 2>&1 || true)
    
    if [[ $? -ne 0 || $error_output == *"ERROR"* ]]; then
        echo "✅ Test répertoire invalide réussi: L'installation dans un répertoire invalide a échoué comme prévu"
        echo "   Message d'erreur capturé: $(echo "$error_output" | grep "ERROR" | head -1)"
    else
        echo "❌ Test failed: L'installation dans un répertoire invalide aurait dû échouer"
        exit 1
    fi
}

test_version_with_date() {
    echo "Test: Affichage de la date du dernier commit"
    setup
    
    # Capture la sortie de la commande version
    local version_output
    version_output=$(bash "$INSTALL_SCRIPT" --version 2>&1)
    
    # Vérifie que la sortie contient une date au format YYYY-MM-DD
    if [[ ! "$version_output" =~ \([0-9]{4}-[0-9]{2}-[0-9]{2}\) ]]; then
        echo "❌ Test failed: La date du dernier commit n'est pas affichée correctement"
        echo "   Output: $version_output"
        exit 1
    fi
    
    echo "✅ Test affichage de la date réussi: $version_output"
    cleanup
}

# Exécution des tests
trap cleanup EXIT

echo "Démarrage des tests d'installation..."
test_basic_installation
test_preserve_custom_rules
test_no_backup_option
test_force_option
test_invalid_directory
test_version_with_date
echo "Tous les tests ont réussi!" 