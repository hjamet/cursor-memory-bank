#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎲 Asharde Dice Engine & Character Generator CLI
Moteur de lancer de dés et générateur de caractéristiques pour le JDR Asharde.

Règles officielles d'Asharde :
- Jet d'action : Pool de d10 = Caractéristique.
  Succès si dé <= Compétence.
  - 1 : Succès + Explosion (relance indéfinie tant qu'on fait des 1).
  - 10 : Dé mort (retire 1 succès du total).
  - Dés bonus/malus : on lance les dés additionnels et on garde les meilleurs (bonus) ou pires (malus).
  - Réussite Critique : >= 2 'uns' sans aucun 'dix' (+5 Marge).
  - Échec Critique : >= 2 'dix' sans aucun 'un' (-5 Marge).

- Génération de Caractéristiques :
  1. Hiérarchie des Aspirations (1 à 10).
  2. Lancer de 10d4.
  3. Tri décroissant des 10d4 et assignation dans l'ordre des Aspirations.
  4. Application des modificateurs raciaux.
"""

import argparse
import random
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CARACTERISTIQUES_OFFICIELLES = [
    "Force", "Constitution", "Agilité", "Vitesse", "Perception",
    "Intelligence", "Érudition", "Autorité", "Chance", "Attractivité"
]

RACES_MODIFS = {
    "Humain": {},
    "Capraquis": {"Force": 1, "Constitution": 1, "Agilité": -1, "Attractivité": -1},
    "Scaphandrier": {"Intelligence": 1, "Agilité": 1, "Perception": -1, "Attractivité": -1},
    "Arachnide": {"Agilité": 1, "Autorité": 1, "Constitution": -1, "Attractivité": -1},
    "Jotun": {"Force": 2, "Constitution": 1, "Agilité": -2, "Vitesse": -1},
    "Asken": {"Perception": 1, "Chance": 1, "Force": -1, "Constitution": -1},
    "Purgeur": {"Force": 1, "Autorité": 1, "Chance": -1, "Attractivité": -1},
    "Fée": {"Attractivité": 1, "Chance": 1, "Agilité": 1, "Force": -2, "Constitution": -1},
    "Valdien": {"Perception": 1, "Chance": 1, "Constitution": -1, "Attractivité": -1},
    "Kobold": {"Agilité": 1, "Intelligence": 1, "Force": -1, "Autorité": -1},
    "Rat": {"Vitesse": 1, "Agilité": 1, "Force": -1, "Autorité": -1}
}


def roll_d10_action(carac: int, comp: int, bonus_dice: int = 0, malus_dice: int = 0, diff: int = 0):
    """Effectue un jet de résolution d'action selon le système Asharde."""
    total_dice_to_roll = max(1, carac + bonus_dice + malus_dice)
    raw_rolls = [random.randint(1, 10) for _ in range(total_dice_to_roll)]
    
    # Gestion des dés bonus / malus sur le pool initial
    if bonus_dice > 0:
        # On garde les carac meilleurs dés (les plus bas pour faire <= comp, mais avec priorité aux 1 et évitement des 10)
        # Score de qualité d'un dé : 1 est le meilleur (0), puis 2..comp, puis >comp, puis 10 est le pire (99)
        def die_quality(d):
            if d == 1: return -10
            if d <= comp: return d
            if d == 10: return 100
            return 50 + d
        sorted_raw = sorted(raw_rolls, key=die_quality)
        kept_rolls = sorted_raw[:carac]
        discarded_rolls = sorted_raw[carac:]
    elif malus_dice > 0:
        def die_quality_malus(d):
            if d == 10: return -100
            if d > comp: return -50 - d
            if d == 1: return 10
            return -d
        sorted_raw = sorted(raw_rolls, key=die_quality_malus)
        kept_rolls = sorted_raw[:carac]
        discarded_rolls = sorted_raw[carac:]
    else:
        kept_rolls = list(raw_rolls)
        discarded_rolls = []

    # Explosions sur les 1 conservés
    explosions = []
    initial_ones = kept_rolls.count(1)
    initial_tens = kept_rolls.count(10)
    
    for die in kept_rolls:
        if die == 1:
            current = 1
            while current == 1:
                reroll = random.randint(1, 10)
                explosions.append(reroll)
                current = reroll

    # Décompte des succès
    base_successes = sum(1 for d in kept_rolls if d <= comp)
    explosion_successes = sum(1 for d in explosions if d <= comp)
    
    dead_dice_from_kept = initial_tens
    dead_dice_from_explosions = explosions.count(10)
    total_dead_dice = dead_dice_from_kept + dead_dice_from_explosions
    
    total_ones = initial_ones + explosions.count(1)
    
    raw_successes = base_successes + explosion_successes
    final_successes = max(0, raw_successes - total_dead_dice)
    margin = final_successes - diff

    # Critiques
    is_crit_success = (total_ones >= 2 and total_dead_dice == 0)
    is_crit_failure = (total_dead_dice >= 2 and total_ones == 0)
    
    if is_crit_success:
        margin += 5
    elif is_crit_failure:
        margin -= 5

    return {
        "carac": carac,
        "comp": comp,
        "bonus_dice": bonus_dice,
        "malus_dice": malus_dice,
        "diff": diff,
        "raw_rolls": raw_rolls,
        "kept_rolls": kept_rolls,
        "discarded_rolls": discarded_rolls,
        "explosions": explosions,
        "total_ones": total_ones,
        "total_tens": total_dead_dice,
        "final_successes": final_successes,
        "margin": margin,
        "is_crit_success": is_crit_success,
        "is_crit_failure": is_crit_failure,
        "status": "SUCCÈS" if margin >= 0 else "ÉCHEC"
    }


def generate_characteristics(aspirations: list, race: str = "Humain"):
    """Génère les caractéristiques officielles selon la méthode 10d4 triés."""
    dice_10d4 = [random.randint(1, 4) for _ in range(10)]
    sorted_10d4 = sorted(dice_10d4, reverse=True)
    
    assigned = {}
    modifs = RACES_MODIFS.get(race, {})
    
    for i, carac in enumerate(aspirations):
        base_val = sorted_10d4[i]
        race_mod = modifs.get(carac, 0)
        final_val = max(1, base_val + race_mod)
        assigned[carac] = {
            "rang_aspiration": i + 1,
            "de_10d4": base_val,
            "mod_race": race_mod,
            "valeur_finale": final_val
        }
        
    return {
        "race": race,
        "tirage_10d4_brut": dice_10d4,
        "tirage_10d4_trie": sorted_10d4,
        "caracteristiques": assigned
    }


def main():
    parser = argparse.ArgumentParser(description="Moteur de dés et création de personnage Asharde")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Commande Jet d'action
    roll_parser = subparsers.add_parser("roll", help="Effectuer un jet d'action d10")
    roll_parser.add_argument("-c", "--carac", type=int, required=True, help="Valeur de la Caractéristique (pool de dés)")
    roll_parser.add_argument("-k", "--comp", type=int, required=True, help="Seuil de Compétence (succès si dé <= comp)")
    roll_parser.add_argument("-b", "--bonus", type=int, default=0, help="Nombre de dés bonus")
    roll_parser.add_argument("-m", "--malus", type=int, default=0, help="Nombre de dés malus")
    roll_parser.add_argument("-d", "--diff", type=int, default=0, help="Difficulté / Seuil de succès requis")

    # Commande Génération de caractéristiques
    gen_parser = subparsers.add_parser("gen-stats", help="Générer les 10 caractéristiques d'un personnage (10d4)")
    gen_parser.add_argument("-r", "--race", type=str, default="Humain", help="Race du personnage")
    gen_parser.add_argument("-a", "--aspirations", type=str, required=True, 
                            help="Liste des 10 caractéristiques ordonnées séparées par des virgules")

    args = parser.parse_args()

    if args.command == "roll":
        res = roll_d10_action(args.carac, args.comp, args.bonus, args.malus, args.diff)
        print("\n" + "="*50)
        print(f"🎲 JET D'ACTION ASHARDE (Carac: {res['carac']}d10 | Comp: <={res['comp']})")
        print("="*50)
        print(f"• Dés lancés : {res['raw_rolls']}")
        if res['discarded_rolls']:
            print(f"• Dés conservés : {res['kept_rolls']} (écartés : {res['discarded_rolls']})")
        if res['explosions']:
            print(f"💥 Explosions (sur les 1) : {res['explosions']}")
        print(f"• 1 obtenus (explosions) : {res['total_ones']}")
        print(f"• 10 obtenus (dés morts) : {res['total_tens']}")
        print(f"• SUCCÈS NETS : {res['final_successes']} (Difficulté: {res['diff']})")
        print(f"• MARGE : {res['margin']:+d}")
        
        if res['is_crit_success']:
            print("🌟 RÉUSSITE CRITIQUE (+5 Marge) !")
        elif res['is_crit_failure']:
            print("💀 ÉCHEC CRITIQUE (-5 Marge) !")
        print(f"➡️ VERDICT : {res['status']}")
        print("="*50 + "\n")

    elif args.command == "gen-stats":
        aspirations = [a.strip() for a in args.aspirations.split(",") if a.strip()]
        if len(aspirations) != 10:
            print(f"❌ Erreur : Il faut exactement 10 caractéristiques ordonnées (reçu {len(aspirations)}).")
            print(f"Caractéristiques valides : {', '.join(CARACTERISTIQUES_OFFICIELLES)}")
            sys.exit(1)
            
        res = generate_characteristics(aspirations, args.race)
        print("\n" + "="*60)
        print(f"🧙 CRÉATION DE CARACTÉRISTIQUES ASHARDE — Race: {res['race']}")
        print("="*60)
        print(f"• Tirage 10d4 brut : {res['tirage_10d4_brut']}")
        print(f"• Tirage 10d4 ordonné décroissant : {res['tirage_10d4_trie']}")
        print("\n| Rang | Caractéristique | Dé 10d4 | Mod. Race | Valeur Finale |")
        print("| :--- | :--- | :---: | :---: | :---: |")
        for carac, data in res["caracteristiques"].items():
            mod_str = f"{data['mod_race']:+d}" if data['mod_race'] != 0 else "-"
            print(f"| {data['rang_aspiration']:2d} | {carac:15s} | {data['de_10d4']:^7d} | {mod_str:^9s} | **{data['valeur_finale']:^13d}** |")
        print("="*60 + "\n")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
