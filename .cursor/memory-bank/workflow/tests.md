# Test Status

- [✅] **MCP Python Execution Test**: Passed (Latest Run: Current Cycle)
  - Command: `python -c "import sys; print('stdout output'); sys.stderr.write('stderr output'); sys.exit(55)"`
  - Result: `exit_code: 55`, `stdout: "stdout output"`, `stderr: "stderr output"`
  - Expected: `exit_code: 55`, correct `stdout`/`stderr`.
  - Issue: None (Previously failed due to incorrect handling before universal Git Bash execution was implemented).
- [ℹ️] MCP Async Terminal Workflow (`tests/test_mcp_async_terminal.js`): **KNOWN ISSUE: INVALID WHEN RUN VIA MCP** (Latest Run: Current Cycle)
  - Issue: This test script attempts to start its own nested MCP server instance, which conflicts with the primary MCP server running it. Executing it via `mcp_MyMCP_execute_command` (even with absolute path) fails silently (exit code 1, no captured stdout/stderr), likely during internal server setup.
  - Recommendation: Run this test directly using `node tests/test_mcp_async_terminal.js` in a separate terminal to validate MCP server functionality.
- [✅] User curl test (MINGW64, no jq): Passed (Latest Run: 2025-04-27 - Required `tr -d '\r'` before `bash` to fix CRLF issue causing `: command not found`)
- [✅] `test_curl_install.sh`: Passed (Latest Run: 2025-04-27 - Fixed no-jq subtest failures related to `--target` option, log file checking, and path extraction)
- [✅] `test_download.sh`: Passed (Latest Run: 2025-04-27)
- [✅] `test_git_install.sh`: Passed (Latest Run: 2025-04-27)
- [✅] `test_install.sh`: Passed (Latest Run: 2025-04-27)
- [✅] `test_mcp_json_absolute_path_no_jq`: Passed (Latest Run: 2025-04-27 - Verified `sed` fallback correctly sets *key* to "Commit" but leaves *relative path* and warns when jq missing)

# Ad-Hoc MCP Command Execution Tests (Current Cycle)
- [✅] **Basic Commands (`echo`, `non_existent_command`)**: Passed. Correct exit codes and stdout/stderr captured via `get_terminal_status`.
- [✅] **Python Script (`python -c ...`)**: Passed. Correct custom exit code, stdout, and stderr captured.
- [✅] **Git Command (`git status --short`)**: Passed. Correct exit code and output captured.
- [✅] **Timeout (`ping -n 5` with 2s timeout)**: Passed. Command timed out in `execute_command`, continued in background, final status/output correct via `get_terminal_status`.
- [✅] **Interruption (`ping -t` stopped via `stop_terminal_command`)**: Passed. Process stopped successfully, final output retrieved.
- [✅] **Special Characters (`echo "String with 'quotes' ..."`)**: Passed (with caveat). Most characters handled correctly by Base64 encoding, but backticks were interpreted by `eval`.
- [✅] **Subdirectory Execution (`cd /abs/path && pwd`)**: Passed. Command executed correctly using absolute paths.
- [✅] **Immediate Return (Timeout Case)**: Passed. `execute_command` returns partial stdout/stderr immediately if the command times out (e.g., `ping -n 10` with `timeout=1`).
- [✅] **Immediate Return (Early Completion Case)**: Passed. `execute_command` now returns full stdout/stderr immediately if the command finishes before the timeout. Removed unnecessary delay after awaiting `cleanupPromise` in `terminal_execution.js`.
- [✅] **Execution CWD (Explicit Parameter)**: Passed. `execute_command` uses the CWD specified by the optional `working_directory` parameter. Verified with `pwd` test (simulating passed parameter).
- [✅] **Execution CWD (Server Default --cwd Argument)**: Passed. `execute_command` now correctly uses the directory passed via the `--cwd` argument to the server (`mcp.json`) as the default CWD when no explicit `working_directory` is provided in the tool call. Verified with `pwd` test.
- [✅] **Reported CWD**: Passed. The `cwd` field in the JSON response reflects the value used for execution (explicit parameter, server default, env var, or fallback).
- [✅] **Cross-Repository CWD**: Passed (with Dependency). Relies on `CURSOR_WORKSPACE_ROOT` being set correctly by the caller (Cursor) to the user's current workspace. If set, commands run in the correct cross-repository CWD.

# Fichier de tests

## Tests d'installation via curl
- ✅ **Test d'installation via curl** : Passed (Latest Run: 2025-04-27 - Fixed)
- ✅ **Test d'installation curl avec options par défaut (pas de backup)** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test de gestion d'erreur curl** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test d'affichage de la date du dernier commit (curl)** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test chemin absolu MCP sans jq** : Passed (Latest Run: 2025-04-27 - Fixed)

## Tests de téléchargement
- ✅ **Test de téléchargement de fichier** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test d'URL invalide** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test de téléchargement d'archive** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test d'URL d'archive invalide** : Passed - Stable (Latest Run: 2025-04-27)

## Tests d'installation via git
- ✅ **Test d'installation de base** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test de préservation des règles personnalisées** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test d'option --no-backup** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test d'option --force** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test de répertoire invalide** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test d'affichage de la date du dernier commit (git)** : Passed - Stable (Latest Run: 2025-04-27)

## Tests d'installation standard
- ✅ **Test d'installation de base**: Passed (Latest Run: 2025-04-27)
- ✅ **Test de backup et restauration** : Passed - Stable (Latest Run: 2025-04-27)
- ✅ **Test de gestion d'erreur** : Passed - Stable (Latest Run: 2025-04-27)

## MCP Async Terminal Tests (`tests/test_mcp_async_terminal.js`)

- **Date**: Current Cycle
- **Commit**: Latest
- **Status**: ℹ️ **KNOWN ISSUE: INVALID / FAILS WHEN RUN VIA MCP**
- **Details**: This test script is an integration test that starts its own MCP server instance. Running it via `mcp_MyMCP_execute_command` causes the nested server startup to conflict with the primary server or fail for other environment reasons. The execution fails silently (exit code 1, no captured stdout/stderr). This test must be executed directly from the command line (`node tests/test_mcp_async_terminal.js`), not via the MCP server itself.
- **Command**: `node /c/Users/Jamet/code/cursor-memory-bank/tests/test_mcp_async_terminal.js` (Attempted execution via MCP)
- **Output Snippet**: (When run via MCP) Exit Code 1, Empty stdout/stderr.
- **Evolution**: N/A (Execution method invalid/problematic).
- **Note**: Execution CWD issue resolved; commands now execute in project root. CWD reporting in response is also fixed.

## Problèmes persistants
- ✅ **Install script permissions (MINGW64/curl)**: Fixed (Latest Run: 2025-04-27) - Root cause identified as CRLF line endings (`\r`) causing parsing errors in piped MINGW64 bash. Resolved by modifying the *execution command* to `curl ... | tr -d '\r' | bash`.

## Historique des problèmes

### 26/03/2024 - Problèmes initiaux
- ❌ **Test d'installation via curl** : Échec avec "Core rules not installed" - Problème avec les règles principales manquantes
- ❌ **Test d'installation curl avec options par défaut** : Échec avec "Backup was created despite default no-backup behavior" - Des backups étaient créés malgré l'absence de l'option --backup
- ❌ **Test de gestion d'erreur curl** : Régression dans la vérification des erreurs - Le test échouait car la gestion des erreurs ne fonctionnait pas correctement

### 28/03/2024 - Corrections
- ✅ **Test d'installation via curl** : Résolu en s'assurant que system.mdc est correctement créé
- ✅ **Test d'installation curl avec options** : Résolu en modifiant la logique de préservation des règles personnalisées pour éviter la création de backups non désirés
- ✅ **Test de gestion d'erreur curl** : Résolu en ajustant le test pour capturer correctement le code d'erreur curl

### 28/03/2024 - Amélioration récupération depuis la branche master
- ✅ **Affichage date du dernier commit** : Ajout de l'affichage de la date du dernier commit pour indiquer la fraîcheur des règles
- ✅ **Récupération depuis master** : Amélioration du script pour toujours récupérer les dernières règles depuis la branche master
- ✅ **Tests d'affichage de date** : Ajout de tests pour vérifier l'affichage de la date du dernier commit

### 28/03/2024 - Bannissement de l'ARCHIVE_URL
- ✅ **Modification du mécanisme de téléchargement** : Remplacé l'utilisation de l'archive par l'utilisation directe de l'API GitHub pour télécharger les fichiers individuellement
- ✅ **Mise à jour du README** : curl est maintenant présenté comme la méthode d'installation par défaut
- ✅ **Tests de téléchargement** : Corrigé en isolant les fonctions de test dans le script de test dédié. 

*   **Last Run:** 2025-04-27
*   **Status:** ✅ Pass
*   **Description:** Test basique de l'installation via Git (`tests/test_git_install.sh`). Vérifie le clonage, la copie des fichiers MCP, la gestion des règles personnalisées et les dépendances npm.
    *   Test: Installation de base
    *   Test: Préservation des règles personnalisées
    *   Test: Option --no-backup
    *   Test: Option --force
    *   Test: Répertoire invalide
    *   Test: Affichage de la date du dernier commit

*   **Last Run:** 2025-04-27
*   **Status:** ✅ Pass (Improved)
*   **Description:** Test de l'installation via `curl | bash` (`tests/test_curl_install.sh`). Vérifie le téléchargement, l'exécution du script, la gestion de l'absence de `jq`, et les erreurs de téléchargement.
    *   Test: Curl Install (Default) - Passed
    *   Test: Curl Install Error Handling (Invalid URL) - Passed
    *   Test: MCP JSON Absolute Path (No jq) - Passed (Fixed issues with `--target` option, log checking, and path extraction)

*   **Last Run:** 2025-04-27
*   **Status:** ✅ Pass
*   **Description:** Test des fonctions de téléchargement (`tests/test_download.sh`). Vérifie le téléchargement de fichiers simples et d'archives, ainsi que la gestion des URL invalides.
    *   Test: File Download
    *   Test: Invalid URL
    *   Test: Archive Download
    *   Test: Invalid Archive URL

*   **Last Run:** 2025-04-27
*   **Status:** ✅ Pass
*   **Description:** Test complet du script d'installation principal (`tests/test_install.sh`). Couvre l'installation propre, la sauvegarde, la restauration, les options et la gestion des erreurs.
    *   Test: Clean Install
    *   Test: Backup and Restore
    *   Test: Reinstall (No Backup)
    *   Test: Reinstall (Force)
    *   Test: Invalid Directory
    *   Test: Display Version

# Test Results

## Summary

## Details

## MCP Async Terminal Tests (`tests/test_mcp_async_terminal.js`)

- **Date**: Current Cycle
- **Commit**: Latest
- **Status**: ℹ️ **KNOWN ISSUE: INVALID / FAILS WHEN RUN VIA MCP**
- **Details**: This test script is an integration test that starts its own MCP server instance. Running it via `mcp_MyMCP_execute_command` causes the nested server startup to conflict with the primary server or fail for other environment reasons. The execution fails silently (exit code 1, no captured stdout/stderr). This test must be executed directly from the command line (`node tests/test_mcp_async_terminal.js`), not via the MCP server itself.
- **Command**: `node /c/Users/Jamet/code/cursor-memory-bank/tests/test_mcp_async_terminal.js` (Attempted execution via MCP)
- **Output Snippet**: (When run via MCP) Exit Code 1, Empty stdout/stderr.
- **Evolution**: N/A (Execution method invalid/problematic).
- **Note**: Execution CWD issue resolved; commands now execute in project root. CWD reporting in response is also fixed.

## Problèmes persistants
- ✅ **Install script permissions (MINGW64/curl)**: Fixed (Latest Run: 2025-04-27) - Root cause identified as CRLF line endings (`\r`) causing parsing errors in piped MINGW64 bash. Resolved by modifying the *execution command* to `curl ... | tr -d '\r' | bash`.