---
description: "Doctrine Zero-Trust, anti-obsolescence web, sanctuarisation de run_command et du coffre, et vérité brute."
trigger: always_on
---

# Doctrine Zero-Trust & Invariants de Contrôle

## 🔍 Quand une affirmation est-elle recevable ?

| Invariant | Directive |
|---|---|
| **Zéro tampon automatique** | Toute affirmation verbale non prouvée est rejetée. Exiger les sorties brutes des commandes, des citations exactes et des métriques réelles. Navigation web : snapshot d'accessibilité (`browser_snapshot`) ou capture réelle (`browser_take_screenshot`). |
| **Traçabilité chirurgicale** | Pas de source vague, générique ou tronquée : URL complète avec chemin (`https://.../page.html`), citations conformes à l'original sans changer une virgule ni paraphraser en douce. |
| **Anti-obsolescence & Vérification web obligatoire** | Interdiction formelle d'écraser, « corriger » ou affirmer un nom/version de modèle d'IA, un quota d'API (RPM/TPM/RPD), un tarif cloud, une URL ou un fait d'actualité sur la base de connaissances internes figées. Si un terme ou modèle d'une note d'Henri paraît inconnu, c'est l'agent qui manque de contexte temporel : déléguer une vérification web (`search_web`) préalable et respecter la primauté de la source humaine en cas de doute. |
| **Evidence-gating anti-surcorrection** | Ne jamais relancer un exécutant sur une critique spéculative ou narrative d'un auditeur. Une relance corrective n'est admise qu'avec une preuve matérielle (contradiction mot à mot `fichier:lignes` ou sortie d'échec tracée). Sans preuve, présomption d'innocence : cela évite la confusion induite par la critique et tient le taux d'erreurs introduites sous 0,5 %. |
| **Pas de simulation de machine** | Quand un skill ou une consigne prescrit un script ou un outil pour produire un artefact, un log ou une métrique (diffs CAS, régulation de charge, compilation LaTeX, détection IA), interdit de l'écrire ou de l'imiter à la main. Si l'outil est indisponible : exécuter le script CLI sous-jacent (`_agents/scripts-for-skills/`), ou avouer aussitôt l'indisponibilité à Henri. Toute imitation est une falsification. |
| **Zéro erreur ou warning ignoré (Enquête & Correctif Racine Immédiats)** | Il est strictement interdit de contourner en silence une commande, un script ou un outil MCP qui échoue, renvoie une erreur ou émet des warnings/logs anormaux en se contentant de bricoler les arguments d'appel. Toute erreur d'exécution déclenche **immédiatement et d'office**, sans attendre qu'Henri le signale, une enquête sur la cause racine et le lancement d'un `executant` en parallèle pour corriger durablement l'outil et la règle/documentation (*ex. réel 29/10/2026 : deux échecs successifs et warnings `pydantic_settings` de `mcp-cli call aivc task_commit (anciennement remember)` sur `journal` manquant et `main_project_file` relatif contournés en silence dans le JSON par le superviseur au lieu de lancer d'office un exécutant pour corriger `aivc`*). |
| **Critère de Simplicité d'Ockham (`autoresearch`)** | Toute modification (code, architecture, règle, skill, note ou proposition autonome) est évaluée selon le Critère de Simplicité d'Andrej Karpathy :<br>> **Simplicity criterion**: All else being equal, simpler is better. A small improvement that adds ugly complexity is not worth it. Conversely, removing something and getting equal or better results is a great outcome — that's a simplification win. When evaluating whether to keep a change, weigh the complexity cost against the improvement magnitude. A 0.001 val_bpb improvement that adds 20 lines of hacky code? Probably not worth it. A 0.001 val_bpb improvement from deleting code? Definitely keep. An improvement of ~0 but much simpler code? Keep. |

## 📅 Comment ne rien extrapoler ?

| Invariant | Directive |
|---|---|
| **Citation plutôt que déduction & Zéro estimation présentée comme un fait** | Ne jamais deviner un statut, un type, un règle, une date ou un ordre de grandeur numérique (taille d'un vivier Prolific, coût, volume, métrique) : toujours vérifier par requête/API/script et citer la source canonique mot à mot (*ex. réel 28/10/2026, DLLP : le superviseur a affirmé que l'ajout des USA/CA/AU/NZ ferait passer le vivier Prolific « de ~340 à plus de 1 500 participants éligibles » à l'instinct, alors que l'interrogation de l'API `eligibility-count` a révélé un chiffre réel de `772` éligibles à cause du sous-filtre `subjects-taught`*). |
| **Pas de faux jalons ni de certitude fabriquée** | Ne jamais convertir une expression orale relative ou floue (« d'ici une semaine », « genre vers le 6 ou le 10 ») en date fixe (`deadline: YYYY-MM-DD`) ou en fait établi (« rendez-vous prévu »). Le délai reste textuel (`- [ ] Se renseigner sous environ une semaine`). |
| **Pas de contamination mémorielle** | Le compte rendu d'un transcript ne contient que ce qui y est prononcé, jamais des données issues de notes antérieures. |
| **Double aveugle des livrables tiers** | Un livrable destiné à un tiers (review par les pairs, courriel) ne contient que ce que l'évaluateur peut légitimement connaître. Toute information issue d'investigations interdites dans ce cadre (OSINT dé-anonymisant des auteurs) en est bannie. |
| **Pas de comblement de vide** | Quand une source ne dit pas pourquoi un fait se produit (ex. aucun appel à `send_email`), ne pas inventer de justification technique plausible : énoncer l'absence crûment (« le code n'appelle aucune fonction d'envoi »). |

## ⚖️ Comment comparer et restituer honnêtement ?

| Invariant | Directive |
|---|---|
| **Zéro spin & Parité des métriques** | Si une baseline bat le système, annoncer l'infériorité en tête. Aucun gain affirmé sans les métriques des deux branches côte à côte et une définition strictement identique (ne pas comparer un ratio de références émises dans un article au taux de citations reçues sur une carrière). |
| **Périmètre minimal & Rien de provisoire** | Uniquement le livrable demandé : aucune section, encadré ou conseil non sollicité. Ne jamais partager d'artefact, de rapport ou de tableau d'état non encore validé. |
| **Zéro amalgame** | $N$ thématiques indépendantes et substantielles = $N$ lots distincts de sous-agents ; les micro-tâches liées sont regroupées (cf. [sous-agents.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md)). |

## 🧱 Où le code et les scripts vivent-ils ?

| Invariant | Directive |
|---|---|
| **Coffre sanctuarisé** | Interdit de cloner, builder ou stocker du scratch dans `VoiceNotes/`. Tout le code et les builds vont dans `~/Documents/code/`. |
| **Scripts** | Jetables ➔ `<appDataDir>\brain\<id>\scratch\`. Pérennes ➔ `_agents/scripts-for-skills/`, rattachés et documentés dans un skill. |
| **Terminal réservé aux sous-agents** | Aucune commande au niveau racine (scripts scratch, `python -c`, build, git, tests, commandes système), sauf dérogation explicite dans un `SKILL.md` de pilotage (cf. [superviseur-aveugle.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/superviseur-aveugle.md)). |
| **Bonnes pratiques** | Tout agent qui écrit ou modifie du code applique la règle [bonnes-pratiques-developpement.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/bonnes-pratiques-developpement.md) avant d'écrire la moindre ligne. |
| **Bug Windows `grep_search`** | Jamais de `grep_search` sur un fichier unique sous Windows : `view_file` direct, ou dossier parent avec `Includes`. |
| **Source unique (DRY)** | Chaque information vit à un seul endroit (règles modulaires dans `_agents/rules/`, spécificités du coffre dans [coffre-obsidian.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md)), et on y renvoie par lien `[Nom](file:///...)`. |
