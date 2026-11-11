---
name: call-copilot
description: Copilote universel d'appels en direct en lecture seule (superviseurs de thèse, étudiants Master, séances d'hypnose, réunions projet) : transcription locale gratuite GPU Faster-Whisper micro (Henri) + son système (Interlocuteurs / identification multi-voix Interlocuteur 1, 2…), artefact HUD HTML interactif à gros boutons colorés dépliants adaptant librement ses catégories à la nature de l'appel (mis à jour en <5s par simple édition JSON), et sauvegarde finale automatique dans VoiceNotes/voicenotes/ avec liens du projet.
---

# Copilote Universel d'Appels en Direct (`call-copilot`)

Ce skill transforme Antigravity en assistant temps réel en **lecture seule** pendant n'importe quel appel vocal (Discord, Teams, Zoom), sans API payante, avec une interface visuelle HTML épurée dont le moteur reste figé mais dont **les catégories de boutons s'adaptent librement à la nature de l'appel**.

## 1. Initialisation avant l'appel (Préchargement léger, Démon GPU & HUD HTML)

1. **Lecture de l'essentiel uniquement (en tête)** : lire directement la Note Maîtresse du projet (`notes/<Projet>.md`) et au maximum 1 ou 2 sous-notes clés pour garder l'essentiel en mémoire.
2. **Démarrage du démon GPU Faster-Whisper gratuit** : lancer hors Job Object via WMI (`Invoke-CimMethod -ClassName Win32_Process -MethodName Create`), en résolvant d'abord le binaire Python actif (`$py = (python -c "import sys; print(sys.executable)").Trim()`, car `Win32_Process.Create` n'exécute pas les shims `.bat` de `pyenv-win`) avec `-B` (zéro `.pyc` dans le coffre), puis attendre que `GET http://127.0.0.1:3055/status` affiche `audio.microphone -ne "Non démarré"` :
   ```powershell
   $py = (python -c "import sys; print(sys.executable)").Trim()
   Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
     CommandLine = "`"$py`" -B `"$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\live_transcriber.py`" --session-file `"<ArtifactDir>\scratch\live_session.md`" --speaker-label `"<Interlocuteurs ou Prénom>`" --project-note `"<Chemin absolu Note Maîtresse>`" --project-links `"<Wikilinks clés>`""
   }
   ```
   - **Attribution des voix & Prérequis multi-PC** :
     - Microphone entrant : toujours étiqueté **`Henri`**.
     - Sortie audio PC (WASAPI Loopback) : par défaut `--speaker-label "Interlocuteurs"` active la diarisation vocale locale (`resemblyzer` GE2E 256-dim embarqué de 17 Mo, zéro token HuggingFace) sous-segment par sous-segment Whisper, étiquetant automatiquement **`Interlocuteur 1`**, **`Interlocuteur 2`**, **`Interlocuteur 3`**… (et `Interlocuteurs` sur un premier éclat `< 2 s`). Pour un appel 1-à-1 identifié, passer `--speaker-label "Prénom"` coupe automatiquement le numérotage multiple (sauf si `--diarize` est forcé).
     - Sur un nouveau PC où `resemblyzer` ne serait pas encore installé dans le Python de `faster-whisper` : `python -m pip install torch scipy librosa webrtcvad-wheels; python -m pip install --no-deps resemblyzer`.
   - Écriture temps réel **uniquement dans `<ArtifactDir>\scratch\live_session.md`** (zéro écriture continue dans `VoiceNotes/` pendant l'appel).
3. **Choix libre des catégories de boutons selon la nature de l'appel** :
   Ne jamais imposer des rubriques artificielles (ex. pas de bouton « Mots-clés & Adjectifs » pour une réunion avec des superviseurs de thèse !). Choisir de **3 à 5 boutons pertinents** dans le tableau `sections` du JSON `hud-data`, en combinant les **5 primitives visuelles universelles** du gabarit (`checklist`, `cards`, `tags`, `kv`, `transcript`) et les palettes (`amber`, `sky`, `violet`, `emerald`, `rose`, `indigo`, `teal`, `slate`) :
   - **Réunion Superviseurs de Thèse / Co-auteurs (ex. Yash, Michalis)** :
     - `checklist` (`amber`) : *📌 Ordre du jour & Arbitrages à obtenir*
     - `kv` (`indigo`) : *📊 Chiffres exacts, Métriques & État des runs*
     - `cards` (`sky`) : *🧭 Arguments méthodologiques & Réponses aux objections*
     - `kv` (`slate`) : *📂 Documents & Liens rapides du projet*
     - `transcript` (`emerald`) : *🎙️ Derniers échanges captés (`Henri` / `Interlocuteur 1, 2…`)*
   - **Suivi d'Étudiant Master (ex. Tatiana, Guillaume)** :
     - `checklist` (`amber`) : *📌 Points d'avancement à vérifier aujourd'hui*
     - `cards` (`sky`) : *🔬 État du protocole, Prochaines étapes & Jalons*
     - `kv` (`rose`) : *⚠️ Points de vigilance méthodologique*
     - `transcript` (`emerald`) : *🎙️ Derniers échanges captés*
   - **Séance d'Hypnose / Table JDR (ex. Shadoa, Conseil des Voleurs)** :
     - `checklist` (`amber`) : *📌 Fil rouge & Contrat de séance*
     - `cards` (`sky`) : *🎭 Architecture dramaturgique & Bascules*
     - `tags` (`violet`) : *⚡ Lexique sensoriel, Mots-clés & Formules*
     - `transcript` (`emerald`) : *🎙️ Derniers échanges captés*
     - `kv` (`rose`) : *🛡️ Garde-fous, PNJ & Déclencheurs*
4. **Création de `<ArtifactDir>\hud_appel_live.html` (`UserFacing: true`)** avec le moteur HTML/JS canonique de la Section 3, puis armement au début de l'appel de `schedule(DurationSeconds=300, TimerCondition="any", Prompt="Suivi discret appel : lire scratch/live_session.md et actualiser le bloc JSON de hud_appel_live.html")`.

## 2. Fonctionnement en direct : Mise à jour JSON en < 5 secondes (Fast-Path absolu)

- **Moteur HTML/JS immuable, JSON dynamique** : pendant tout l'appel, le code `<script>` en bas de `hud_appel_live.html` ne bouge pas ; utiliser `edit_file` **uniquement sur le bloc `<script id="hud-data" type="application/json">`** (et ajouter/retirer une section JSON à la volée si la conversation bifurque).
- **Réveil manuel instantané (Henri envoie `.`, un message vide ou 2–3 mots)** :
  - `TimerCondition="any"` annule automatiquement le timer en cours.
  - En **un seul tour d'outils (~4 s)** : `read_file` de la fin de `scratch/live_session.md` ➔ `edit_file` du bloc JSON `hud-data` de `hud_appel_live.html` ➔ réarmement de `schedule(DurationSeconds=300, TimerCondition="any", Prompt="...")` ➔ confirmation d'une ligne.
- **Réveil périodique automatique (toutes les 5 min)** : actualiser `hud-data` si de nouveaux échanges ont eu lieu (cocher ce qui a été dit, rafraîchir `transcript` et les repères contextuels).

## 3. Gabarit HTML Canonique à Catégories Dynamiques (`hud_appel_live.html`)

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] antialiased p-4 select-text">

<!-- HUD_DATA_START -->
<script id="hud-data" type="application/json">
{
  "project_title": "Nom du Projet — Appel en direct",
  "updated_at": "14:00",
  "audio_status": "🟢 Actif CUDA FP16 · Henri + Interlocuteurs",
  "flash_focus": "Synthèse en 1 ligne de l'objectif immédiat ou du point en cours de discussion.",
  "sections": [
    {
      "id": "agenda",
      "icon": "📌",
      "title": "ORDRE DU JOUR & POINTS À VOIR",
      "color": "amber",
      "type": "checklist",
      "items": [
        {"text": "Premier point important à aborder", "done": false}
      ]
    },
    {
      "id": "key_points",
      "icon": "🧭",
      "title": "ARGUMENTS / DÉROULÉ CONTEXTUEL",
      "color": "sky",
      "type": "cards",
      "items": [
        {"title": "Point 1", "detail": "Détail synthétique directement exploitable à l'oral."}
      ]
    },
    {
      "id": "transcript",
      "icon": "🎙️",
      "title": "DERNIERS ÉCHANGES CAPTÉS",
      "color": "emerald",
      "type": "transcript",
      "items": []
    },
    {
      "id": "refs",
      "icon": "📂",
      "title": "CHIFFRES, REPÈRES & LIENS CLÉS",
      "color": "slate",
      "type": "kv",
      "items": [
        {"label": "Note Maîtresse", "hint": "Repère factuel clé"}
      ]
    }
  ]
}
</script>
<!-- HUD_DATA_END -->

<div id="app" class="max-w-3xl mx-auto space-y-3"></div>

<script>
(function() {
  const data = JSON.parse(document.getElementById('hud-data').textContent);
  const STORAGE_KEY = 'agy_call_hud_open_panels';
  let openPanels = {};
  try { openPanels = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) {}

  function saveOpen() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(openPanels)); } catch (e) {}
  }

  function esc(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  const PALETTES = {
    amber:   { btn: 'bg-amber-600 hover:bg-amber-500 text-white',     badge: 'bg-amber-950/50 text-amber-100',     tag: 'bg-amber-500/15 border-amber-500/30',     accent: 'accent-amber-500' },
    violet:  { btn: 'bg-violet-600 hover:bg-violet-500 text-white',   badge: 'bg-violet-950/50 text-violet-100',   tag: 'bg-violet-500/15 border-violet-500/30',   accent: 'accent-violet-500' },
    sky:     { btn: 'bg-sky-600 hover:bg-sky-500 text-white',         badge: 'bg-sky-950/50 text-sky-100',         tag: 'bg-sky-500/15 border-sky-500/30',         accent: 'accent-sky-500' },
    emerald: { btn: 'bg-emerald-600 hover:bg-emerald-500 text-white', badge: 'bg-emerald-950/50 text-emerald-100', tag: 'bg-emerald-500/15 border-emerald-500/30', accent: 'accent-emerald-500' },
    rose:    { btn: 'bg-rose-600 hover:bg-rose-500 text-white',       badge: 'bg-rose-950/50 text-rose-100',       tag: 'bg-rose-500/15 border-rose-500/30',       accent: 'accent-rose-500' },
    indigo:  { btn: 'bg-indigo-600 hover:bg-indigo-500 text-white',   badge: 'bg-indigo-950/50 text-indigo-100',   tag: 'bg-indigo-500/15 border-indigo-500/30',   accent: 'accent-indigo-500' },
    teal:    { btn: 'bg-teal-600 hover:bg-teal-500 text-white',       badge: 'bg-teal-950/50 text-teal-100',       tag: 'bg-teal-500/15 border-teal-500/30',       accent: 'accent-teal-500' },
    slate:   { btn: 'bg-slate-700 hover:bg-slate-600 text-white',     badge: 'bg-slate-950/50 text-slate-100',     tag: 'bg-slate-500/15 border-slate-500/30',     accent: 'accent-slate-500' }
  };

  const SPEAKER_BADGES = [
    'bg-amber-500/20 border-amber-500/40 text-amber-300',
    'bg-violet-500/20 border-violet-500/40 text-violet-300',
    'bg-rose-500/20 border-rose-500/40 text-rose-300',
    'bg-teal-500/20 border-teal-500/40 text-teal-300'
  ];

  function speakerBadgeClass(spk) {
    const s = String(spk || '');
    if (s === 'Henri') return 'bg-sky-500/20 border-sky-500/40 text-sky-300';
    let h = 0;
    for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
    return SPEAKER_BADGES[h % SPEAKER_BADGES.length];
  }

  function computeBadge(sec) {
    if (sec.badge) return sec.badge;
    if (sec.type === 'checklist') return (sec.items || []).filter(i => !i.done).length + ' à voir';
    if (sec.type === 'tags') return (sec.groups || []).reduce((n, g) => n + (g.items || []).length, 0) + ' éléments';
    if (sec.type === 'transcript') return (sec.items || []).length + ' répliques';
    return (sec.items || []).length + ' points';
  }

  function renderSectionBody(sec, sIdx, pal) {
    if (sec.type === 'checklist') {
      return `<div class="space-y-2 pt-1">${(sec.items || []).map((r, i) => `
        <label class="flex items-start gap-3 p-2.5 rounded-lg border border-[var(--border)] bg-[var(--background)] cursor-pointer">
          <input type="checkbox" data-sidx="${sIdx}" data-iidx="${i}" ${r.done ? 'checked' : ''} class="mt-1 h-4 w-4 ${pal.accent}">
          <span class="text-sm font-medium ${r.done ? 'line-through opacity-50' : ''}">${esc(r.text)}</span>
        </label>`).join('')}</div>`;
    }
    if (sec.type === 'tags') {
      return `<div class="space-y-3 pt-1">${(sec.groups || []).map(g => `
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-[var(--muted-foreground)] mb-1.5">${esc(g.label)}</div>
          <div class="flex flex-wrap gap-1.5">${(g.items || []).map(w => `
            <span class="px-2.5 py-1 rounded-md text-sm font-medium border ${pal.tag}">${esc(w)}</span>`).join('')}</div>
        </div>`).join('')}</div>`;
    }
    if (sec.type === 'cards') {
      return `<div class="space-y-2.5 pt-1">${(sec.items || []).map(c => `
        <div class="p-3 rounded-lg border border-[var(--border)] bg-[var(--background)]">
          <div class="font-semibold text-sm mb-1">${esc(c.title)}</div>
          <div class="text-sm text-[var(--muted-foreground)] leading-relaxed">${esc(c.detail)}</div>
        </div>`).join('')}</div>`;
    }
    if (sec.type === 'kv') {
      return `<div class="space-y-2 pt-1">${(sec.items || []).map(n => `
        <div class="p-2.5 rounded-lg border border-[var(--border)] bg-[var(--background)] text-sm">
          <span class="font-semibold">${esc(n.label)} :</span>
          ${n.url
            ? `<a href="${esc(n.url)}" target="_blank" class="underline ml-1 hover:opacity-80">${esc(n.hint || n.url)}</a>`
            : `<span class="text-[var(--muted-foreground)] ml-1">${esc(n.hint)}</span>`}
        </div>`).join('')}</div>`;
    }
    if (sec.type === 'transcript') {
      if (!(sec.items || []).length) {
        return `<div class="text-sm text-[var(--muted-foreground)] italic py-1">En attente des premières paroles captées…</div>`;
      }
      return `<div class="space-y-1.5 pt-1">${(sec.items || []).map(t => `
        <div class="text-sm p-2 rounded border border-[var(--border)] bg-[var(--background)] flex flex-wrap items-baseline gap-1.5">
          <span class="text-xs font-mono text-[var(--muted-foreground)]">[${esc(t.time)}]</span>
          <span class="text-xs font-bold px-2 py-0.5 rounded border ${speakerBadgeClass(t.speaker)}">${esc(t.speaker)}</span>
          <span class="flex-1 min-w-[200px]">${esc(t.text)}</span>
        </div>`).join('')}</div>`;
    }
    return '';
  }

  function renderAll() {
    const secs = data.sections || [];
    const app = document.getElementById('app');
    app.innerHTML = `
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
          <h1 class="text-base font-bold">${esc(data.project_title)}</h1>
          <div class="flex items-center gap-2 text-xs">
            <span class="px-2.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 font-semibold">${esc(data.audio_status)}</span>
            <span class="px-2 py-1 rounded bg-[var(--background)] border border-[var(--border)] font-mono">MAJ ${esc(data.updated_at)}</span>
          </div>
        </div>
        <div class="text-sm p-2.5 rounded-lg bg-[var(--background)] border border-[var(--border)] font-medium">
          🎯 ${esc(data.flash_focus)}
        </div>
        <div class="flex justify-end gap-2 mt-2.5">
          <button id="expand-all" class="text-xs px-2.5 py-1 rounded border border-[var(--border)] hover:opacity-80">Tout déplier</button>
          <button id="collapse-all" class="text-xs px-2.5 py-1 rounded border border-[var(--border)] hover:opacity-80">Tout replier</button>
        </div>
      </div>
      ${secs.map((sec, sIdx) => {
        const pal = PALETTES[sec.color] || PALETTES.slate;
        const isOpen = !!openPanels[sec.id];
        return `
        <div class="rounded-xl overflow-hidden border border-[var(--border)] bg-[var(--card)] shadow-sm">
          <button data-sec="${esc(sec.id)}" class="w-full flex items-center justify-between px-4 py-3.5 font-bold text-left transition ${pal.btn}">
            <span class="flex items-center gap-2.5 text-base">
              <span>${esc(sec.icon || '•')}</span>
              <span>${esc(sec.title)}</span>
            </span>
            <span class="flex items-center gap-2">
              <span class="text-xs font-semibold px-2.5 py-1 rounded-full ${pal.badge}">${esc(computeBadge(sec))}</span>
              <span class="text-lg leading-none">${isOpen ? '▾' : '▸'}</span>
            </span>
          </button>
          <div class="${isOpen ? 'block' : 'hidden'} p-3.5 border-t border-[var(--border)]">
            ${renderSectionBody(sec, sIdx, pal)}
          </div>
        </div>`;
      }).join('')}
    `;

    app.querySelectorAll('button[data-sec]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-sec');
        openPanels[id] = !openPanels[id];
        saveOpen();
        renderAll();
      });
    });
    document.getElementById('expand-all').addEventListener('click', () => {
      secs.forEach(s => openPanels[s.id] = true);
      saveOpen(); renderAll();
    });
    document.getElementById('collapse-all').addEventListener('click', () => {
      openPanels = {};
      saveOpen(); renderAll();
    });
    app.querySelectorAll('input[data-sidx]').forEach(cb => {
      cb.addEventListener('change', (e) => {
        const sIdx = Number(e.target.getAttribute('data-sidx'));
        const iIdx = Number(e.target.getAttribute('data-iidx'));
        data.sections[sIdx].items[iIdx].done = e.target.checked;
        renderAll();
      });
    });
  }

  renderAll();
})();
</script>
</body>
</html>
```

## 4. Fin d'appel & Archivage automatique dans `VoiceNotes/voicenotes/`

Dès qu'Henri signale la fin de l'appel, annuler tout `schedule` actif (`manage_task kill`) et exécuter :
```powershell
python -B "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\live_transcriber.py" --finalize --session-file "<ArtifactDir>\scratch\live_session.md" --title "<Titre descriptif avec espaces>" --project-links "<Wikilinks clés>"
```
Cela arrête proprement le démon GPU et génère d'un seul bloc `VoiceNotes/voicenotes/<Titre descriptif avec espaces>.md` avec durée réelle, dates `DD-MM-YYYY`, liens cliquables vers le projet et transcription horodatée distinguant `Henri` et chaque interlocuteur.
