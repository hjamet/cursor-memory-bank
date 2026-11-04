# 🔬 Fiche Recherche : Thèse & Publications (2026)

Cette fiche détaille les travaux de recherche doctorale de Henri Jamet à l'UNIL (DESI/AAIL).

## 🧭 Axes de Recherche & Projets Actuels

### 1. Framework GSET / PathFinderRAG / CLIMB
* **Nom complet** : *GSET: Budget-Constrained Document Selection via Groupwise Successive Elimination for Multi-Hop Evidence Retrieval* (Évolution majeure de PathfinderRAG / CLIMB).
* **Concept** : Reformulation de la sélection de preuves multi-sauts sous contrainte budgétaire via l'identification du meilleur bras (Best-Arm Identification - BAI) et des tests de groupe (Groupwise Elimination Tournament). Remplace le classement ordinal par une utilité d'ensemble (set-wise utility) capturée par un Cross-Encoder ("Mixer").
* **Statut (2026)** : Repositionnement stratégique post-AAAI-26 pour CIKM / EMNLP 2026 (ARR mai 2026). Protocole expérimental consolidé (baselines BM25S, BGE-M3, ColBERT, Listwise LLM Reranker, et évaluation end-to-end Reader/Faithfulness).
* **Fichiers clés** :
  - [Analyse Stratégique et Prospective des Opportunités de Publication pour le Framework GSET.md](file:///C:/Users/hjamet/Documents/VoiceNotes/notes/Analyse%20Strat%C3%A9gique%20et%20Prospective%20des%20Opportunit%C3%A9s%20de%20Publication%20pour%20le%20Framework%20GSET.md)
  - [PhD Research Progress & 2026 Publication Strategy.md](file:///C:/Users/hjamet/Documents/VoiceNotes/notes/PhD%20Research%20Progress%20&%202026%20Publication%20Strategy.md)
  - [Project Dashboard - Henri Jamet.md](file:///C:/Users/hjamet/Documents/VoiceNotes/notes/Project%20Dashboard%20-%20Henri%20Jamet.md)

### 2. LLM as a Recommender (Generative RecSys)
* **Concept** : Comparer les approches classiques de filtrage collaboratif avec le raisonnement génératif des LLM sur des jeux de données pédagogiques épars (ex. Tomplay). 
* **Expérience** : Lancement d'une étude utilisateur en aveugle (A/B testing, N=100) pour tester l'hypothèse "Small Data & Rich Content".
* **Statut (2026)** : En cours. Demande de validation éthique UNIL en cours de traitement.
* **Cibles de Soumission** : RecSys 2026, VLDB, CIKM, EMNLP, ICDM.

### 3. Inverse Turing Test (Social AI)
* **Concept** : Évaluer la capacité des LLM à détecter la tromperie (deception detection) chez d'autres agents. Framework analysant quatre dyades d'interaction (Humain-Humain, Humain-IA, IA-Humain, IA-IA).
* **Source des Données** : Atelier "Mystères de l'UNIL" 2025.
* **Collaborateurs** : Mathis (interface), Yuanjun (analyse qualitative/éthique), prof. Michalis Vlachos.
* **Cibles de Soumission** : CHI 2027 (Septembre 2026), HRI 2027 (Octobre 2026).

### 4. DLLP - Digital Language Learning Platform (Digital Education)
* **Concept** : Plateforme d'apprentissage numérique des langues avec orchestration de tuteurs intelligents personnalisés et optimisation multi-agents (frontière de Pareto : latence, throughput, coût).
* **Méthodologie & Fondations** : Ancrage théorique sur les théories d'apprentissage (Sweller, Bloom, TAM, constructivisme, SLMs). Étude d'ablation systématique (5 groupes d'ablation, jumeaux) et validation sur données réelles de production (33 enseignants inscrits).
* **Collaborateurs** : Pamela, Yash. Brainstorming hebdomadaire le lundi à 11h30.
* **Statut (2026)** : Phase de Refine complétée pour l'article (méthodologie et revue de littérature).

---

## 🛠️ Infrastructure & Outils Scientifiques

### Slurmray (DESI Cluster Integration)
* **Description** : Pont Slurm-Ray déployé avec succès sur le cluster de calcul du département DESI.
* **Fonctionnalité** : Automatise la sérialisation des environnements d'exécution et la distribution des tâches LLM (hyperparameter sweeps) pour les projets PathFinderRAG / GSET et LLM as Recommender.
* **Fichiers clés** :
  - [SlurmRay.md](file:///C:/Users/hjamet/Documents/VoiceNotes/SlurmRay.md)
  - [Set up cluster DESI JOB Slurm - RAY.md](file:///C:/Users/hjamet/Documents/VoiceNotes/notes/Set%20up%20cluster%20DESI%20JOB%20Slurm%20-%20RAY.md)

---

## 👥 Réseau de Collaborateurs

* **Prof. Michalis Vlachos** : Directeur de thèse, spécialiste en Time Series et Data Mining. [Michalis Vlachos](file:///C:/Users/hjamet/Documents/VoiceNotes/notes/PhD%20Research%20Progress%20&%202026%20Publication%20Strategy.md#L49)
* **Yash** : Postdoc/Chercheur sénior à l'AAIL, co-auteur principal.
* **Pamela** : Spécialiste en éducation digitale et interface d'apprentissage.
* **Amir** : Expert systèmes MCP et multi-agents (collaboration sur le projet AVC MCP).
* **Yuanjun** : Collaborateur pour les analyses qualitatives sur le test de Turing.

---

## 🔗 Liens Internes

* 🧭 **Index Principal** : [index_principal.md](file:///C:/Users/hjamet/Documents/VoiceNotes/antigravity/index_principal.md)
* 📋 **Suivi des Tâches** : [todolist.md](file:///C:/Users/hjamet/Documents/VoiceNotes/antigravity/todolist.md)
* 🎓 **Enseignement & Master** : [enseignements.md](file:///C:/Users/hjamet/Documents/VoiceNotes/antigravity/souvenirs/enseignements.md)
