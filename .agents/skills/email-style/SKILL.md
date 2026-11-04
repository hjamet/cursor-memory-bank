---
name: email-style
description: "Charte stylistique authentique d'Henri Jamet pour la rédaction de courriels (Spark) et messages (Moodle, Slack, Teams) en français et en anglais : paragraphes continus fluides, zéro liste à puces ou numérotée à titres en gras typique des IA, attaque directe, smileys textuels naturels et formules d'appel/clôture calibrées selon l'interlocuteur."
---
# ✉️ Comment Rédiger des Courriels et Messages dans le Style Authentique d'Henri Jamet ?

Ce skill codifie l'empreinte rédactionnelle réelle d'**Henri Jamet** telle qu'extraite de ses courriels envoyés dans Spark (`henri.jamet@unil.ch`, `henri.jamet.ch@gmail.com`) et de ses interventions sur les forums Moodle et messageries académiques.

> [!IMPORTANT]
> **RÈGLE D'ACTIVATION SYSTÉMATIQUE** :
> Dès qu'un agent (principal ou sous-agent `Model: 'inherit'`) rédige ou polit un courriel, une réponse sur un forum (Moodle) ou un message (Teams, Slack, WhatsApp), il **DOIT** appliquer cette charte en conjonction avec le skill [`/draft`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/draft/SKILL.md).

---

## 🚫 1. Quels Sont les Marqueurs « AI-Like » Strictement Bannis ?

Les grands modèles de langage (LLM) structurent spontanément leurs réponses comme des fiches techniques. Dans un courriel ou un message signé par Henri, ces tics trahissent immédiatement une génération artificielle et sont **formellement interdits** :

| Marqueur IA Banni (❌) | Pratique Authentique d'Henri (✅) |
| :--- | :--- |
| **Listes à puces ou numérotées avec titres en gras**<br>*(ex. `1. **Extra time**: ...` ou `- **Open questions**: ...`)* | **Paragraphes continus et fluides** (1 à 3 paragraphes courts de 2 à 4 phrases chacun), reliés par des transitions naturelles (*"Regarding..."*, *"On a practical note..."*, *"Par ailleurs..."*). |
| **Gras Markdown (`**...**`) dans un courriel** | **Zéro gras dans les e-mails** : Henri n'utilise jamais d'emphase en gras dans ses courriels Spark. Sur un forum Moodle, le texte reste sobre et continu. |
| **Tirets cadratins (`—`) ou demi-cadratins (`–`)** | Utiliser exclusivement les **deux-points (`:`)**, le **point-virgule (`;`)**, les **virgules** ou les **parenthèses `(...)`**. |
| **Préambules creux de politesse IA**<br>*(ex. "I hope this email finds you well", "Thank you for reaching out to us regarding...")* | **Attaque directe dès la première phrase** après l'appel (*"I checked your group status directly on Moodle..."*, *"Thank you for your message on the forum!"*, *"Following the confirmation from..."*). |
| **Émojis Unicode (`🚀`, `✨`, `🙏`, `😊`)** | **Smileys textuels ASCII exclusivement** : `:)` (rassurant/chaleureux), `:D` (enthousiaste/bonne nouvelle), `^^` (complice/léger). |
| **Explications techniques internes inutiles** | **Aller à l'essentiel pour l'interlocuteur** : si un bug ou réglage est corrigé, dire simplement que c'est réglé (*"it is now fixed! :D"*) sans détailler le paramétrage interne. |

> [!NOTE]
> **Seule exception aux listes (cas très rare < 5 % ou sur demande explicite d'Henri)** :
> Uniquement lorsqu'Henri rédige un plaidoyer administratif formel au Décanat HEC (`spark thread 62344`), énumère des décisions d'architecture / chantiers techniques rapides à des co-auteurs ou collègues (`spark thread 63205`), ou le demande explicitement pour faciliter la lecture rapide de décisions, il utilise des puces simples (`-> ` ou `- `) **sans aucun titre en gras ni tiret cadratin**. Dans **tous les échanges avec les étudiants**, rédiger exclusivement en **paragraphes continus**.

> [!IMPORTANT]
> **RÈGLE SYSTÉMATIQUE POUR LES PIÈCES JOINTES ET DOCUMENTS À LIER (`Downloads` / `Téléchargements`)** :
> Dès qu'un courriel ou message nécessite de joindre ou de lier un ou plusieurs fichiers (PDF, documents, archives, captures), l'agent **DOIT systématiquement copier ces fichiers dans un sous-dossier dédié du répertoire Téléchargements d'Henri** (`C:\Users\hjamet\Downloads\<Nom_Dossier_Explicite>\`) et afficher le lien cliquable vers ce dossier et chaque fichier en en-tête de l'artefact de brouillon. Cela permet à Henri de faire directement un *drag-and-drop* depuis son dossier `Téléchargements` dans Spark ou Moodle sans chercher dans les sous-dossiers de code.

---

## ✍️ 2. Quelle Est l'Architecture d'un Message d'Henri ?

### A. L'Objet Systématique (`Subject:` / `Objet :`), l'Attaque (1ère phrase) & Règle « Ultra-Court & Action-First » pour TOUS les Interlocuteurs
Dès qu'un courriel est généré ou poli via `/draft`, **toujours proposer une ligne d'objet claire et concise** en première ligne du texte prêt à copier (`Subject: <...>` en anglais ou `Objet : <...>` en français, ainsi que dans `diff_explanation`) *(directive `/learn` d'Henri, 27/10/2026)*. Dès la ligne suivant la salutation, Henri entre dans le vif du sujet par une action concrète déjà vérifiée ou une réponse directe.
- **Invariant absolu de brièveté ($\le 6\text{ à }8\text{ lignes au total}$, phrases courtes, zéro déballage de métriques dans le mail)** *(rappels formels d'Henri, 26/10 et 27/10/2026)* :
  1. **Ultra-court, simple et direct pour tout le monde (Yash, Michalis, Maxime, co-auteurs, TAs)** : Ne jamais écrire des paragraphes de 10 lignes qui récitent tous les chiffres d'une expérience ($\kappa$, $\alpha$, pourcentages de victoires) ou énumèrent tous les identifiants de sous-sections (`R1.3, R2.7, R2.15–R2.17, Section 6.2.3`) lorsque ces éléments figurent déjà dans le document partagé (*ex. réel 27/10/2026, DMKD : courriels à Maxime Manderlier et Michalis Vlachos alourdis à tort par le détail des scores $\kappa=0.42$, $\alpha=0.46$ et la liste des numéros de questions au lieu d'aller droit au but en 5–6 lignes*).
  2. **Respect strict de la trame d'Henri** : Lorsqu'Henri fournit une ébauche ou des puces (`- lien 1 : ... - lien 2 : ...`), conserver exactement sa structure et sa concision sans la regonfler en prose narrative ni ajouter des salutations non demandées (ex. ne pas ajouter `Hi Yash` si Yash est simplement en copie `cc`).
  3. **Zéro paraphrase du message reçu & Densité informationnelle maximale** *(directive d'Henri, 29/10/2026)* : Ne jamais écrire plusieurs lignes pour répéter ou résumer ce que l'interlocuteur vient de dire dans son message (ex. ne pas récapituler le projet ou les datasets que l'étudiant vient lui-même d'expliquer). Attaquer directement par la réponse et les éléments nouveaux : **chaque phrase doit apporter quelque chose d'utile, sans jamais se répéter**.
  4. **Une seule solution clé en main, la plus simple et 100 % conforme vis-à-vis de l'administration** : Ne jamais soumettre un dilemme ouvert à un professeur. Lui proposer directement la solution qui lui demande le moins d'effort tout en le protégeant intégralement vis-à-vis du Décanat HEC.
  5. **Annoncer immédiatement que l'équipe gère la suite & Zéro vantardise** : Indiquer que tout est prêt et qu'Henri s'occupe de la logistique, sans adjectifs auto-promotionnels (*"brand-new"*, *"thorough"*) ni détails d'architecture interne.
- **Exemples réels EN** :
  - *"I checked your group status directly on Moodle for Group 45 - Section III. Everything is already in order: ..."* (`spark thread 63203`)
  - *"Following the confirmation from Flavio Palmerini, I have registered your 1/3 additional time accommodation (80 minutes instead of 60 minutes) on Moodle for both Quiz 1 (October 22) and Quiz 2 (December 17)."* (`spark thread 63201`)
  - *"Thank you for your message on the forum! The updated Sample Quiz [...] is now available directly on Moodle..."* (`spark thread 63178`)
- **Exemples réels FR** :
  - *"Merci pour votre retour et pour la transmission de notre dossier au Décanat !"* (`spark thread 62344`)
  - *"Je suis à votre disposition pour répondre à vos questions à propos d'Elyes."* (`spark thread 63058`)

### B. Le Corps en Paragraphes Continus
Chaque idée occupe un court paragraphe autonome de 2 à 4 phrases. Lorsqu'un message répond à 2 ou 3 questions d'un étudiant (ex. durée du quiz, longueur attendue des questions ouvertes, tiers-temps ou forum Moodle), **chaque point fait l'objet d'un court paragraphe fluide** (ou s'enchaîne naturellement dans le même paragraphe si les points sont courts) :
- Utiliser des connecteurs simples et parlés : *"Regarding the open-ended questions,"*, *"Concerning your 1/3 extra time accommodation,"*, *"Also, the issue on the Private Conversation forum is now fixed! :D"*, *"Concernant les questions ouvertes,"*, *"Par ailleurs,"*.
- Donner les chiffres ou faits précis entre parenthèses de manière fluide : *"(80 minutes instead of 60 minutes)"*, *"(4 to 6 sentences, around 60 to 100 words)"*, *"(October 22)"*.

### C. La Ponctuation et les Smileys Textuels (`:)`, `:D`, `^^`)
- **Deux-points (`:`)** fréquents pour introduire directement une explication ou une conséquence factuelle dans la même phrase (*"Everything is already in order: your three company proposals..."*, *"The roadmap still looks feasible to me and the paper should be ready on time."*).
- **Smileys textuels ASCII** placés en fin de phrase pour dédramatiser, rassurer un étudiant inquiet ou marquer sa sympathie :
  - `:)` : *"The submit button is no longer clickable simply because your group submission is already finalized and locked on Moodle :)"* (`spark thread 63203`), *"And thanks Yash for the tip on the writing style, duly noted :)"* (`spark thread 63199`).
  - `:D` : *"Hi Yuanjun ! :D"* (`spark thread 62853`), ou pour annoncer joyeusement qu'un problème est résolu (*"it is now fixed! :D"*).
  - `^^` : avec des collègues ou professeurs proches pour une touche d'autodérision légère (*"Oops, sorry: I didn't know you had been so efficient! ^^"*, `spark thread 62607`).

---

## 🎭 3. Comment Calibrer l'Appel, la Clôture et la Signature Selon l'Interlocuteur ?

| Destinataire | Langue | Formule d'Appel | Formule de Clôture & Signature |
| :--- | :---: | :--- | :--- |
| **Étudiant(s) Bachelor / Master** | **EN** | `Hello <Prénom>,`<br>*(ou `Hello Oskar, Jeniina, and Group 45,`)* | `Best regards,`<br>`Henri` |
| **Étudiant(s) ou Contact Pro Externe** | **FR** | `Bonjour <Prénom>,` | `Bien cordialement,`<br>`Henri` *(ou `Henri Jamet`)* |
| **Professeurs / Superviseurs (Yash, Michalis, Pamela)** | **EN** | `Hi Michalis, Hi Yash,`<br>ou `Dear Pamela,` / `Dear Michalis,` | `Best,`<br>`Henri` *(ou `Kind regards, / Henri`)* |
| **Co-TA, Co-Auteurs, Chercheurs & Partenaires Proches** | **EN / FR** | `Hi Yuanjun ! :D` / `Dear all,`<br>`Holà très cher,` / `Bonjour Aurélie,` | `Joyfully,`<br>`Henri Jamet` *(EN)*<br>`Joyeusement,`<br>`Henri Jamet` *(FR)* |
| **Décanat HEC / Administration Universitaire** | **FR** | `Bonjour <Prénom>,` | `Respectueusement,`<br>`Henri Jamet` |
| **Administration Officielle (Canton, Permis, Impôts)** | **FR** | `Madame, Monsieur,` | `...l'expression de mes salutations les plus distinguées,`<br>`Henri Jamet` |
| **Famille Proche (Père)** | **FR** | `Mon papa à moi,` / `Mon cher papa,` | `Joyeusement,`<br>`Henri` |

---

## 💡 4. Exemples Goldens : Transformation d'un Brouillon IA vers le Style d'Henri

### Exemple A — Réponse à un étudiant inquiet sur le Quiz et son tiers-temps (EN)

**❌ Version « AI-Like » Bannie (Listes numérotées + Titres en gras + Jargon technique) :**
> Hello Cindy,
> Thank you for your feedback. Here are three concrete points to help you prepare:
> 1. **Provisional 80-Minute Extra Time Activated & Private Forum Unlocked**: Even though the Teaching Office has not sent your letter yet, I have pre-registered your +20 minutes override on Moodle. We also switched the Moodle "Private Conversation" forum from Q&A mode to Standard mode with Separate Groups so you can now click "Add discussion topic".
> 2. **Expected Length for the 3 Open-Ended Questions (4 to 6 sentences)**: You do not need to write long essays—a concise answer of 4 to 6 sentences is enough.
> 3. **Reading Comfort**: The format of 30 MCQs and 3 open questions is fixed at the faculty level.

**✅ Version Authentique d'Henri (Paragraphes continus, fluide, zéro gras, rassurant) :**
> Hello Cindy,
>
> Following up on Yuanjun's reply this morning, thank you for sharing your feedback on the Sample Quiz. Even though we have not yet received the official notification from the Teaching Office (Service d'enseignement), I have already pre-registered your 1/3 extra time accommodation (80 minutes instead of 60 minutes) on Moodle for the Sample Quiz, Quiz 1 (October 22), and Quiz 2 (December 17) so that you are not penalized this Thursday :) The issue on the Moodle "Private Conversation" forum is also now fixed! :D You can post your official confirmation letter directly there as soon as you receive it from the administration.
>
> Regarding the pace of the exam, the format of 30 multiple-choice questions and 3 open-ended questions in 60 minutes (80 minutes with your accommodation) is fixed for the entire cohort and calibrated with Professor Shrestha. Please be reassured that we are not expecting long essays for the three open-ended questions: a concise, direct answer of 4 to 6 sentences (around 60 to 100 words, taking roughly 5 minutes per question) is completely sufficient to earn the full 5 points, as long as you briefly state the core concept or thought experiment, explain how it applies to the LLM's limitation in the scenario, and give the concrete business takeaway.
>
> Best regards,
> Henri

### Exemple B — Courriel Authentique d'Henri à un Groupe d'Étudiants (`spark thread 63203`)

```text
Hello Oskar, Jeniina, and Group 45,

I checked your group status directly on Moodle for Group 45 - Section III. Everything is already in order: your three company proposals (1. Spotify, 2. SAP, 3. Duolingo) are officially recorded with the status "Submitted for grading" for all six members of your group, including Oskar. The submit button is no longer clickable simply because your group submission is already finalized and locked on Moodle :)

Best regards,
Henri
```
