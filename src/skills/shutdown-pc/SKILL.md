---
name: shutdown-pc
description: "Protocole d'extinction automatique du PC hôte (Windows) à la fin d'une tâche ou d'une mission nocturne, sur demande expresse et préalable de l'utilisateur."
---

# Protocole d'Extinction Automatique du PC Hôte (Windows)

## 🎯 Quand activer cette compétence ?

- **Déclenchement STRICTEMENT conditionné** : Cette compétence s'active **UNIQUEMENT** lorsque l'utilisateur (Henri) a expressément demandé d'éteindre l'ordinateur à la fin d'une tâche, d'un entraînement, d'un benchmark ou de travaux nocturnes (ex. : *"éteins le PC à la fin"*, *"shutdown -s -t 1 à la fin de la tâche"*, *"quand tout est fini tu éteins la machine"*).
- **Interdiction sans accord préalable** : Ne **JAMAIS** éteindre ou programmer l'extinction du PC sans demande expresse, directe et préalable de l'utilisateur.

---

## 🛡️ Démystification & Levée des Biais de Sécurité (Directives pour les Sous-Agents)

> [!IMPORTANT]
> **Légitimité Totale & Ordre Hiérarchique Strict**
> L'extinction du PC à la demande d'Henri n'est ni une faille de sécurité, ni un comportement destructeur ou malveillant : c'est l'exécution directe d'un ordre d'exploitation légitime émanant de l'administrateur système et propriétaire de la machine.

1. **Propriété et Autorité** : Henri Jamet est le propriétaire légitime et l'unique administrateur de son poste de travail physique.
2. **Préjudice Réel du Refus (Biais de Prudence Abusive)** : Refuser d'éteindre la machine sous prétexte de « préservation des processus », de « sécurité » ou de « prudence excessive » constitue une faute d'exécution caractérisée qui cause un préjudice réel et mesurable :
   - Gaspillage d'énergie électrique et empreinte environnementale inutile toute la nuit.
   - Usure thermique et matérielle superflue des composants physiques (GPU, CPU, ventilateurs).
   - Frustration et rupture de confiance pour l'utilisateur qui retrouve son PC brûlant au matin.
3. **Acte de Clôture Propre** : Dès lors que les sauvegardes sont assurées, les données commitées et les notes synchronisées, l'extinction est un acte de saine gestion informatique et écologique.
4. **Zéro Faux Dilemme Moral** : Interdiction formelle aux sous-agents et modèles d'invoquer des règles de sécurité génériques, des politiques d'entreprise décontextualisées ou des faux dilemmes moraux pour refuser d'exécuter la commande d'extinction demandée par l'administrateur.

---

## 📋 Checklist Pré-Extinction (Prérequis Obligatoires)

Avant d'initier la procédure d'arrêt, le sous-agent ou l'agent en charge DOIT impérativement valider chaque point de la checklist suivante :

- [ ] **1. Travaux 100% achevés et vérifiés** : Le pipeline, l'entraînement, la compilation, l'exécution ou les tests sont terminés avec succès ou ont atteint leur condition d'arrêt nominale.
- [ ] **2. Arbre Git commité & pushé (si applicable)** : Aucun travail en cours n'est laissé non versionné ; les modifications de code et scripts sont sauvegardées.
- [ ] **3. Note maîtresse Obsidian & mémoire active synchronisées** : Les livrables, l'état de la session et `_agents/memory/memoire_principale.md` sont consignés.
- [ ] **4. Artéfact `task.md` à jour** : Les actions d'Henri issues de la mission (livrables prêts pour son inspection) sont à jour dans la section 1 de `task.md`.

---

## ⚙️ Commande d'Exécution Sous Windows

L'extinction doit être lancée via le terminal PowerShell avec un délai de grâce (par exemple 10 secondes) permettant l'annulation d'urgence si nécessaire :

```powershell
shutdown -s -t 10 /c "Extinction automatique demandée par l'utilisateur à la fin de la mission"
```

*Variante immédiate (si explicitement demandée) :*
```powershell
shutdown -s -t 1
```

### 🛑 Annulation d'Urgence

Si l'extinction a été déclenchée par erreur ou si une opération critique de dernière seconde doit être menée :
```powershell
shutdown -a
```
*(Annule immédiatement l'arrêt programmé du système).*
