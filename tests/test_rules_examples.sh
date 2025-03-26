#!/bin/bash

# Test pour vérifier la présence de la section Exemple dans les règles
test_rule_has_example() {
    local rule_file=".cursor/rules/$1.mdc"
    if [ ! -f "$rule_file" ]; then
        echo "❌ Le fichier de règle $rule_file n'existe pas"
        return 1
    fi

    if grep -q "^## Exemple" "$rule_file" || grep -q "^## Exemple$" "$rule_file"; then
        echo "✅ La règle $1 contient une section Exemple"
        return 0
    else
        echo "❌ La règle $1 ne contient pas de section Exemple"
        return 1
    fi
}

# Test des règles spécifiques
test_rule_has_example "request-analysis"
test_rule_has_example "context-update" 