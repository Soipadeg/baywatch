# BayWatch - Analyse des Annulations d'Interventions

Application Streamlit simple et sécurisée pour analyser les annulations d'interventions.

## Caractéristiques

- **Interface** : Web (Streamlit)
- **Traitement** : 100% en mémoire, aucune sauvegarde disque
- **Données** : Fichiers Excel (.xlsx, .xls) — max 50 Mo
- **Sécurité** : Confidentiel, pas de logs, pas de serveur externe

## Lancement rapide

```bash
./start.sh
```

L'application s'ouvre automatiquement à `http://localhost:8501`

## Utilisation

1. Téléchargez un fichier Excel contenant vos données
2. L'application détecte automatiquement les colonnes
3. Consultez les analyses et graphiques
4. Exportez les résultats en CSV

## Colonnes reconnues

- `date_intervention` / `date intervention` / `intervention_date`
- `date_annulation` / `date annulation` / `cancellation_date`
- `motif_annulation` / `motif annulation` / `cancellation_reason`
- `intervenant` / `technician` / `personnel`
- `client` / `company` / `account`
- `service` / `department` / `type_service`
- `heure_intervention` / `heure intervention` / `intervention_time`

*L'application est insensible à la casse et aux accents.*

## Architecture

- `app/app.py` — Interface utilisateur
- `scripts/analysis.py` — Moteur d'analyse statistique
- `requirements.txt` — Dépendances Python

## Sécurité

✅ Pas de fichier disque — données uniquement en RAM  
✅ Pas de base de données — tout traitée localement  
✅ Pas de logs — aucun audit trail externe  
✅ Confidentiel by design  
