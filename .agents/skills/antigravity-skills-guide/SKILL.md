---
name: antigravity-skills-guide
description: Guide complet d'explication et de référence pour la création, la structure, le formatage et l'installation des compétences (skills) Google Antigravity. Activez ou consultez ce skill pour concevoir, structurer, documenter et installer des compétences globales ou locales d'agent.
---

# Guide des Compétences Google Antigravity (Skills Guide)

Les compétences (**Skills**) de Google Antigravity (AGY) sont des extensions modulaires basées sur des fichiers. Elles permettent de doter les agents IA de connaissances spécialisées, de contextes précis et de flux de travail opérationnels sans surcharger le prompt système global de l'agent.

Ce document sert de guide de référence pour concevoir, structurer, documenter et installer des compétences de qualité professionnelle pour Antigravity.

---

## 1. Qu'est-ce qu'une Compétence (Skill) Antigravity ?

Une compétence est un ensemble cohérent d'instructions de haut niveau et de ressources complémentaires. Elle fournit à l'agent :
*   **Des directives contextuelles** : Pour orienter ses décisions sur des sujets complexes ou techniques.
*   **Des exemples de référence (Goldens)** : Pour appliquer des techniques d'apprentissage par l'exemple (*Few-Shot Learning*).
*   **Des scripts d'automatisation** : Pour exécuter des tâches déterministes.
*   **Des documentations hors-ligne** : Pour servir de base de connaissances rapide sans requérir d'accès réseau.

L'agent Antigravity CLI analyse dynamiquement les descriptions des compétences à sa disposition. Si une requête utilisateur correspond au domaine de compétence défini, l'agent active et consulte la compétence correspondante.

---

## 2. Structure Standardisée d'une Compétence

Un dossier de compétence doit suivre une structure claire et prévisible :

```text
nom-du-skill/
├── SKILL.md          # Fichier d'instructions principal et métadonnées (Requis)
├── scripts/          # Scripts utilitaires exécutables (Optionnel : Python, Bash, Node.js)
├── examples/         # Exemples d'implémentation, cas de test, goldens (Optionnel)
└── references/       # Fichiers de documentation, guides, schémas ou templates (Optionnel)
```

### Description des dossiers d'assets :
*   `SKILL.md` : Contient le frontmatter YAML (identifiant, description de déclenchement) et les instructions d'orchestration pour l'agent.
*   `scripts/` : Contient des scripts d'aide. L'agent peut les exécuter pour valider, formater ou extraire des données complexes (ex: `validate_json.py`, `parse_pdf.sh`).
*   `examples/` : Fournit des exemples concrets pour le Few-Shot Learning, aidant l'agent à comprendre le format ou le comportement attendu.
*   `references/` : Contient de la documentation technique dense ou des fichiers de spécification (Markdown, JSON) vers lesquels l'agent est orienté depuis le `SKILL.md`.

---

## 3. Format de `SKILL.md` et Métadonnées (Frontmatter)

Le fichier `SKILL.md` doit impérativement débuter par un **frontmatter YAML** délimité par des triples tirets `---`, suivi du corps au format Markdown.

### Structure du Frontmatter YAML

```yaml
---
name: nom-du-skill
description: Description concise à la troisième personne indiquant quand et pourquoi l'agent doit activer cette compétence.
---
```

> [!IMPORTANT]
> La `description` du frontmatter est l'élément le plus critique. C'est elle que l'agent lit pour décider si la compétence est pertinente pour la tâche demandée. Elle doit utiliser des termes clés précis (ex: *"Activez ce skill lorsque l'utilisateur demande de concevoir des déploiements Kubernetes..."*).

### Structure Recommandée pour le Corps du Fichier
Le corps du document doit être structuré de manière à guider efficacement l'agent :
1.  **# Titre de la compétence**
2.  **## Quand utiliser cette compétence** : Liste à puces décrivant les cas d'activation et les scénarios types.
3.  **## Comment l'utiliser** : Directives pas à pas, règles de décision, et instructions de lecture des fichiers dans `references/` ou `examples/`.
4.  **## Outils et Scripts disponibles** : Description des programmes du dossier `scripts/` et de la manière de les appeler.

---

## 4. Emplacements d'Installation (Globaux vs Locaux)

Antigravity prend en charge deux scopes d'installation pour les compétences :

### A. Scope Global (Global Skills)
Ces compétences sont disponibles pour l'agent sur l'ensemble de la machine, peu importe le projet ou le répertoire de travail actuel. Elles conviennent aux utilitaires personnels ou administratifs transverses.
*   **Dossier d'installation moderne** : `~/.gemini/antigravity-cli/skills/`
*   **Dossier historique (compatibilité)** : `~/.gemini/skills/`

### B. Scope Local / Projet (Workspace Skills)
Ces compétences sont spécifiques à un projet ou à un espace de travail particulier. Elles sont committées dans le système de contrôle de version (Git) du projet pour être partagées avec toute l'équipe.
*   **Dossiers d'installation locaux** :
    *   `<workspace_root>/.agents/skills/`
    *   `<workspace_root>/.agent/skills/`

---

## 5. Bonnes Pratiques de Conception

Pour garantir une efficacité maximale et une consommation minimale de tokens de l'agent :

*   **Principe de Divulgation Progressive (*Progressive Disclosure*)** : Ne surchargez pas `SKILL.md` avec de longues lignes de code ou des documentations complètes. Gardez les instructions de haut niveau dans `SKILL.md` et renvoyez l'agent vers des fichiers dédiés dans `references/` ou `examples/` si le besoin s'en fait sentir.
*   **Liens de Fichiers Robustes** : Utilisez des chemins relatifs depuis la racine du skill pour renvoyer vers les sous-dossiers (ex: `[Spécification API](references/api_spec.md)`).
*   **Qualité des Exemples** : Dans le dossier `examples/`, fournissez des paires "Input / Output" claires. Les agents apprennent extrêmement vite par imitation de structures de haute qualité.
*   **Modularité** : Séparez les responsabilités. Un skill doit traiter d'un sujet fonctionnel ou technique unique. Si un sujet devient trop vaste, divisez-le en plusieurs compétences.
