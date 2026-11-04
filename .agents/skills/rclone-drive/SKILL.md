---
name: rclone-drive
description: "Accès, recherche et téléchargement de fichiers sur Google Drive 30 To via Rclone."
---
# Skill Rclone Google Drive (`rclone-drive`)

Ce skill permet d'accéder, rechercher, lire et télécharger à la demande des fichiers stockés sur le Google Drive de 30 To via le CLI Rclone.

## Remote configuré
- Nom du remote : `gdrive`
- Portée (scope) : `drive.readonly` (lecture seule)

## Commandes principales

### 1. Rechercher des fichiers
Pour rechercher un fichier ou dossier par motif/nom :
```bash
rclone lsjson gdrive: --include "*query*"
```

### 2. Lire le contenu d'un fichier en flux (stream)
Pour lire directement le texte d'un fichier sans le télécharger sur disque :
```bash
rclone cat gdrive:"path/file.txt"
```

### 3. Télécharger un fichier unique
Pour copier un fichier spécifique vers le système local :
```bash
rclone copyto gdrive:"path/file.pdf" "./local_file.pdf"
```

### 4. Lister le contenu d'un dossier
```bash
rclone lsf gdrive:"path/to/folder"
```
