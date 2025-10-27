You are preparing to hand off your work to another agent. Your task is to generate a structured prompt that will help the next agent understand the current context, what you've accomplished, and transition toward a new vague objective.

## Behavior

When the user types `/prompt` (with or without additional instructions), you must:

1. **Analyze your past context** - Review what you were working on, what you've accomplished, and what discoveries you made during your work
2. **Capture the user's vague idea** - Accept a very general objective without details (e.g., "relancer l'entraînement", "optimiser les performances")
3. **Create a logical link** - Explain how your past work and discoveries have naturally led to this new idea from the user
4. **Generate a structured handoff prompt** following the 4 mandatory sections with strong exploratory collaboration instructions
5. **Present the prompt in a markdown code block** - Wrap the entire prompt in triple backticks (```) to facilitate copy-paste and clearly separate your exploratory work (analysis, tool calls) from the final prompt itself

## Language Requirement

**MANDATORY**: The generated prompt must ALWAYS be written in French. When the agent addresses the user and creates the handoff prompt, it must be entirely in French language. Internal reasoning or tool calls can be in any language, but all user-facing content (the prompt itself) must be in French.

## Format Structure (Mandatory)

Generate a prompt block with exactly these 4 sections:

### **1. Contexte**
Write in French. Explain the narrative of your work: what task you were working on, what you accomplished, and what you discovered during your work. Then explain how these discoveries/accomplishments naturally led to the user's new vague idea. This section should tell a story of progression and logical transition. Use high-level natural language without technical details, focusing on the journey from your work to this new exploration.

### **2. Objectif**  
Write in French. Describe the very vague, general objective that the user has provided (a single line, a broad idea without details). Frame it as an open exploration rather than a precise task. DO NOT ask for details or precision - accept the vagueness. Examples in French: "Explorer la possibilité de relancer l'entraînement" rather than "Configurer et exécuter un pipeline d'entraînement avec paramètres spécifiques".

### **3. Fichiers Concernés**
Write in French. List TWO categories of files/directories:
- **Files from your past work**: Include files you modified or examined, with explanation of what was done/discovered in them
- **Files relevant to the new vague objective**: Include files that might be pertinent for exploration, with explanation of why they could be important

Indicate clearly which files belong to which category in your list.

### **4. Instructions de Collaboration**
Write in French. **MANDATORY AND CRITICAL**: This section must be extremely directive and imperative. You MUST specify that the agent:
- **FORBIDDEN** to start implementing anything immediately
- **MUST** read EXHAUSTIVELY all files listed in "Fichiers Concernés" before any action
- **MUST** perform multiple semantic searches in the codebase to understand existing solutions
- **MUST** read the README and all relevant documentation
- **MUST** achieve a deep understanding of the context and project before any discussion
- **MUST** discuss with the user to clarify precise expectations, ask questions about technical constraints, and establish a detailed action plan together
- Only AFTER exhaustive exploration and collaborative planning, can any implementation begin

Emphasize that exploration is NOT optional - it's mandatory.

## Usage Modes

### Mode 1: With User Instructions
```
/prompt [user instructions]
```

In this mode:
- Generate the standard 4-section prompt with a narrative context showing your work progression
- Incorporate the user's vague idea in the **Objectif** section (accept the vagueness)
- Explain in **Contexte** how your completed work and discoveries led naturally to this vague idea
- The next agent will receive: your work narrative + the vague new objective + strong exploration mandate

### Mode 2: Without User Instructions
```
/prompt
```

In this mode:
- Generate the standard 4-section prompt based solely on your work
- Focus on explaining what you accomplished and obstacles you encountered
- Optionally suggest potential next steps or openings in **Instructions de Collaboration**, but make it clear the user will decide what happens next

## Example Output

Note: When you generate a prompt using this command, present it wrapped in a markdown code block for easy copy-paste and ALWAYS write it in French.

```markdown
---

**Contexte**
Je travaillais sur l'implémentation d'un système d'authentification utilisateur pour l'application. J'ai terminé le flux d'inscription et l'ai rendu fonctionnel, avec toutes les validations nécessaires et les interactions avec la base de données. Lors des tests en charge, j'ai découvert que le système rencontre des problèmes de performance significatifs. Les utilisateurs rapportent des temps de réponse lents aux heures de pointe, et mes tests ont confirmé que les requêtes d'authentification prennent exponentiellement plus de temps avec l'augmentation de l'accès concurrent. Ce goulot d'étranglement de performance impacte directement l'expérience utilisateur. Compte tenu de ces découvertes, tu as suggéré d'explorer des stratégies d'optimisation pour le système d'authentification.

**Objectif**
Explorer la possibilité d'optimiser le système d'authentification pour améliorer les performances sous charge.

**Fichiers Concernés**

*Du travail que je viens de compléter :*
- `src/auth/registration.js` : Contient la logique d'inscription que j'ai implémentée ; découvert des requêtes de base de données lourdes qui pourraient être optimisées
- `src/config/database.js` : Configuration que j'ai examinée ; pourrait nécessiter des ajustements de pool de connexions
- `tests/performance/load_test.js` : Tests de charge que j'ai exécutés qui ont révélé le goulot d'étranglement

*Potentiellement pertinents pour l'exploration :*
- `src/auth/login.js` : Pourrait contenir des patterns similaires à l'inscription qui nécessitent une optimisation
- `src/config/` : Fichiers de configuration pour les limites de ressources qui pourraient être ajustées
- `package.json` : Dépendances qui pourraient être mises à jour ou optimisées pour de meilleures performances

**Instructions de Collaboration**
Tu es INTERDIT de commencer à implémenter quoi que ce soit immédiatement. Ta première et UNIQUE tâche est l'exploration et la compréhension :

1. **LIS EXHAUSTIVEMENT** tous les fichiers listés ci-dessus dans "Fichiers Concernés" - tu dois comprendre ce qui a été fait, ce qui a été découvert, et ce qui pourrait être pertinent
2. **EFFECTUE plusieurs recherches sémantiques** dans le codebase pour identifier des solutions existantes, des patterns, ou du code connexe
3. **LIS le README** et toute documentation pertinente pour comprendre l'architecture du projet et les contraintes
4. **ATTEINS une compréhension approfondie** du contexte, du travail effectué, et de l'espace de problèmes
5. **DISCUTE avec l'utilisateur** pour clarifier ses attentes précises, poser des questions sur les contraintes techniques, comprendre les priorités, et établir ensemble un plan d'action détaillé

Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, tu peux commencer à considérer tout travail d'implémentation. L'exploration est OBLIGATOIRE, pas optionnelle.

---
```

(The prompt above is wrapped in a markdown code block for easy copy-paste)

## Important Notes

- **Always write the prompt in French** - The entire generated prompt must be in French language
- **Always use the exact 4-section structure** - This ensures consistency and clarity
- **Contexte must be narrative** - Tell the story of your work, discoveries, and transition to the new vague idea
- **Objectif must be vague** - Accept the user's general idea without demanding details
- **Fichiers Concernés must list both categories** - Your past work files AND files potentially relevant to the new vague objective
- **Instructions de Collaboration must be extremely strong** - Use imperative, forbidding language to enforce exhaustive exploration before any action
- **Emphasize exploration over execution** - The goal is collaborative planning after thorough understanding, not immediate implementation

