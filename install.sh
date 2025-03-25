#!/bin/bash

# Memory Bank - Script d'installation
# Ce script télécharge et installe le système Memory Bank pour Cursor

echo "Téléchargement de Memory Bank..."

# Vérification des prérequis
if ! command -v curl &> /dev/null; then
    echo "Erreur: curl est requis pour l'installation."
    exit 1
fi

if ! command -v unzip &> /dev/null; then
    echo "Erreur: unzip est requis pour l'installation."
    exit 1
fi

# Variables
TEMP_DIR=$(mktemp -d)
REPO="votreusername/cursor-memory-bank"
BRANCH="master"
ZIP_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.zip"
CURSOR_DIR=".cursor"

# Téléchargement du contenu
curl -L ${ZIP_URL} -o "${TEMP_DIR}/memory-bank.zip"

if [ $? -ne 0 ]; then
    echo "Erreur: Impossible de télécharger Memory Bank."
    rm -rf ${TEMP_DIR}
    exit 1
fi

# Extraction du contenu
unzip -q "${TEMP_DIR}/memory-bank.zip" -d "${TEMP_DIR}"
EXTRACTED_DIR=$(ls -d ${TEMP_DIR}/*/ | head -1)

# Vérification de l'existence du dossier .cursor
if [ -d "${CURSOR_DIR}" ]; then
    echo "Attention: Le dossier ${CURSOR_DIR} existe déjà."
    read -p "Voulez-vous le remplacer? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation annulée."
        rm -rf ${TEMP_DIR}
        exit 0
    fi
    
    # Sauvegarde du dossier existant
    BACKUP_DIR="${CURSOR_DIR}_backup_$(date +%Y%m%d%H%M%S)"
    echo "Sauvegarde du dossier existant vers ${BACKUP_DIR}..."
    mv "${CURSOR_DIR}" "${BACKUP_DIR}"
fi

# Copie du dossier .cursor
echo "Installation de Memory Bank..."
cp -r "${EXTRACTED_DIR}/${CURSOR_DIR}" ./

# Nettoyage
rm -rf ${TEMP_DIR}

echo "Memory Bank a été installé avec succès!"
echo "Utilisation: Ouvrez simplement ce projet dans Cursor IDE et commencez à interagir avec l'agent." 