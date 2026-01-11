# Dépannage & Troubleshooting

Ce guide rassemble les solutions aux problèmes courants rencontrés avec Cursor Memory Bank.

## 🐛 Problèmes Windows : Encodage & Emojis

Si vous rencontrez une `UnicodeEncodeError` lors de l'exécution de commandes avec des emojis sur Windows :

**Problème** : Windows utilise l'encodage `cp1252` par défaut, ce qui pose problème avec les caractères Unicode/Emojis.

**Solution** : Définissez les variables d'environnement suivantes :
- `PYTHONIOENCODING=utf-8` : Force Python à utiliser l'UTF-8 pour les I/O.
- `PYTHONLEGACYWINDOWSSTDIO=0` : Active le mode UTF-8 sur la console Windows.
- `LC_ALL=C.UTF-8` et `LANG=C.UTF-8` : Définit la locale.

### Git Diff Encoding Fix
Si `python tomd.py` lève une `UnicodeDecodeError` (problème de décodage CP1252), le script `tomd.py` a été mis à jour pour écrire le diff `git` en binaire brut. Aucune action utilisateur n'est requise si vous utilisez la dernière version du dépôt.

## 🔄 Problèmes de Workflow

Si le workflow autonome semble bloqué ou se comporte de manière inattendue :
1. **Vérifier les systèmes de sécurité** : Regarder si le frein d'urgence ("Emergency Brake") a été activé.
2. **Monitorer les transitions** : Vérifier que les étapes du workflow se complètent.
3. **Vérifier la mémoire** : Consulter la mémoire de travail pour des patterns d'erreur.
4. **Redémarrer** : Utiliser `start-workflow` pour réinitialiser l'état.

## 🔔 Problèmes de Notifications

Si les notifications "toast" n'apparaissent pas :
1. **Session State** : Vérifier l'initialisation du session state Streamlit.
2. **Cache** : Vider le cache Streamlit.
3. **Check Manuel** : Utiliser le testeur de notifications intégré si disponible.
