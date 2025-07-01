#!/bin/bash

# Test script pour valider la correction du bug de data loss
echo "=== TEST DE VALIDATION DE LA CORRECTION configure_gemini_cli_mcp() ==="

# Variables de test
INSTALL_DIR="$(pwd)"
export INSTALL_DIR

# 1. Vérifier la configuration existante
echo ""
echo "1. Configuration existante AVANT l'exécution :"
if [ -f ".gemini/settings.json" ]; then
    echo "✅ Fichier .gemini/settings.json existe"
    echo "Contenu:"
    cat .gemini/settings.json | jq . || cat .gemini/settings.json
else
    echo "❌ Fichier .gemini/settings.json n'existe pas"
fi

# 2. Extraire et exécuter la fonction configure_gemini_cli_mcp
echo ""
echo "2. Extraction et test de la fonction configure_gemini_cli_mcp..."

# Créer un script temporaire avec juste la fonction
cat > temp_test_function.sh << 'EOF'
#!/bin/bash

INSTALL_DIR="${INSTALL_DIR:-$(pwd)}"

configure_gemini_cli_mcp() {
    local gemini_settings_file="$INSTALL_DIR/.gemini/settings.json"
    
    echo "Configuration des serveurs MCP pour Gemini CLI..."
    
    # Créer le répertoire .gemini s'il n'existe pas
    mkdir -p "$INSTALL_DIR/.gemini"
    
    # Vérifier que les serveurs MCP existent
    local mcp_commit_server="$INSTALL_DIR/.cursor/mcp/mcp-commit-server/server.js"
    local memory_bank_server="$INSTALL_DIR/.cursor/mcp/memory-bank-mcp/server.js"
    
    if [ ! -f "$mcp_commit_server" ]; then
        echo "⚠️  AVERTISSEMENT: $mcp_commit_server non trouvé"
        echo "   Le serveur MCP Commit pourrait ne pas fonctionner"
    fi
    
    if [ ! -f "$memory_bank_server" ]; then
        echo "⚠️  AVERTISSEMENT: $memory_bank_server non trouvé"
        echo "   Le serveur MCP Memory Bank pourrait ne pas fonctionner"
    fi
    
    # Convertir les chemins Windows si nécessaire
    local mcp_commit_server_win
    local memory_bank_server_win
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        mcp_commit_server_win=$(echo "$mcp_commit_server" | sed 's|/c/|C:/|g' | sed 's|/|\\|g')
        memory_bank_server_win=$(echo "$memory_bank_server" | sed 's|/c/|C:/|g' | sed 's|/|\\|g')
    else
        mcp_commit_server_win="$mcp_commit_server"
        memory_bank_server_win="$memory_bank_server"
    fi
    
    # Créer la configuration MCP
    local new_mcp_config='{
        "MyMCP": {
            "command": "node",
            "args": ["'"$mcp_commit_server_win"'"]
        },
        "MemoryBankMCP": {
            "command": "node", 
            "args": ["'"$memory_bank_server_win"'"]
        },
        "Context7": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp@latest"]
        }
    }'
    
    # Lire la configuration existante
    local existing_config=""
    if [ -f "$gemini_settings_file" ]; then
        existing_config=$(cat "$gemini_settings_file" 2>/dev/null || echo "{}")
    else
        existing_config="{}"
    fi
    
    # Fusion intelligente avec jq si disponible
    if command -v jq >/dev/null 2>&1; then
        echo "Utilisation de jq pour fusion sécurisée..."
        echo "$existing_config" | jq --argjson mcpServers "$new_mcp_config" '. + {mcpServers: $mcpServers}' > "$gemini_settings_file"
    else
        echo "jq non disponible, utilisation du fallback manuel..."
        
        # Fallback manuel : préserver les propriétés existantes et ajouter mcpServers
        if echo "$existing_config" | grep -q '"mcpServers"'; then
            # Remplacer la section mcpServers existante
            echo "$existing_config" | sed 's/"mcpServers"[^}]*}[^}]*}/"mcpServers": '"$(echo "$new_mcp_config" | sed 's/"/\\"/g')"'/' > "$gemini_settings_file"
        else
            # Ajouter mcpServers à la configuration existante
            if [ "$existing_config" = "{}" ]; then
                echo '{"mcpServers": '"$new_mcp_config"'}' > "$gemini_settings_file"
            else
                # Insérer mcpServers avant la dernière accolade
                echo "$existing_config" | sed 's/}$/, "mcpServers": '"$(echo "$new_mcp_config" | sed 's/"/\\"/g')"'}/' > "$gemini_settings_file"
            fi
        fi
    fi
    
    echo "✅ Configuration Gemini CLI mise à jour dans $gemini_settings_file"
    
    echo ""
    echo "⚠️  IMPORTANT: Cette configuration est locale au projet ($INSTALL_DIR/.gemini/settings.json)"
    echo "   Assurez-vous que Gemini CLI est configuré pour utiliser les configurations locales"
    echo "   ou copiez manuellement cette configuration vers ~/.gemini/settings.json si nécessaire"
}

# Exécuter la fonction
configure_gemini_cli_mcp
EOF

# Rendre le script exécutable et l'exécuter
chmod +x temp_test_function.sh
./temp_test_function.sh

# 3. Vérifier le résultat
echo ""
echo "3. Configuration APRÈS l'exécution :"
if [ -f ".gemini/settings.json" ]; then
    echo "✅ Fichier .gemini/settings.json existe"
    echo "Contenu:"
    cat .gemini/settings.json | jq . || cat .gemini/settings.json
    
    echo ""
    echo "4. VALIDATION CRITIQUE:"
    
    # Vérifier que les données utilisateur sont préservées
    if grep -q "apiKey" .gemini/settings.json; then
        echo "✅ SUCCÈS: apiKey préservée"
    else
        echo "❌ ÉCHEC: apiKey perdue"
    fi
    
    if grep -q "theme" .gemini/settings.json; then
        echo "✅ SUCCÈS: theme préservé"
    else
        echo "❌ ÉCHEC: theme perdu"
    fi
    
    if grep -q "customSettings" .gemini/settings.json; then
        echo "✅ SUCCÈS: customSettings préservées"
    else
        echo "❌ ÉCHEC: customSettings perdues"
    fi
    
    if grep -q "existingMcpServers" .gemini/settings.json; then
        echo "✅ SUCCÈS: existingMcpServers préservés"
    else
        echo "❌ ÉCHEC: existingMcpServers perdus"
    fi
    
    if grep -q "MyMCP" .gemini/settings.json; then
        echo "✅ SUCCÈS: Nouveaux serveurs MCP ajoutés"
    else
        echo "❌ ÉCHEC: Nouveaux serveurs MCP non ajoutés"
    fi
    
    # Vérifier la validité JSON
    if cat .gemini/settings.json | jq . >/dev/null 2>&1; then
        echo "✅ SUCCÈS: JSON valide"
    else
        echo "❌ ÉCHEC: JSON invalide"
    fi
    
else
    echo "❌ ÉCHEC: Fichier .gemini/settings.json n'existe pas après exécution"
fi

# Nettoyage
rm -f temp_test_function.sh

echo ""
echo "=== FIN DU TEST ===" 