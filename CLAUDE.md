# BayWatch - Documentation pour Claude Code

## Vue d'ensemble

**BayWatch** est une application Streamlit simple et sécurisée pour analyser les annulations d'interventions.

- **Interface** : Streamlit (web)
- **Traitement** : 100% en mémoire, aucune sauvegarde disque
- **Données** : Fichiers Excel (.xlsx, .xls) — max 50 Mo
- **Sécurité** : Confidentiel, pas de logs, pas de serveur externe

## Structure

```
baywatch/
├── app/
│   └── app.py              # Application Streamlit principale
├── scripts/
│   └── analysis.py         # Logique d'analyse (InterventionAnalyzer)
├── requirements.txt        # Dépendances Python
├── README.md              # Documentation utilisateur
├── start.sh               # Script de lancement
└── CLAUDE.md              # Ce fichier
```

## Lancement

```bash
./start.sh
# ou
streamlit run app/app.py
```

L'app s'ouvre à `http://localhost:8501`

## Architecture de l'analyse

La classe `InterventionAnalyzer` (scripts/analysis.py) :
1. Charge le fichier Excel en mémoire (BytesIO)
2. Map automatiquement les colonnes (insensible casse/accents)
3. Analyse les données avec pandas :
   - Stats globales (taux, totals)
   - Par motif, intervenant, client, service
   - Temporelle (mois, jour semaine, heure)
   - Délais (entre annulation/intervention)
4. Retourne JSON/CSV pour export

## Points clés

- **Pas de cache disque** — chaque upload est éphémère
- **Détection flexible** — reconnaît "Oui", "Yes", "True", "1", "Annulé", etc.
- **Colonnes optionnelles** — certaines colonnes peuvent manquer, pas d'erreur
- **Streaming** — le cache Streamlit TTL=3600s (1h)

## Fichiers à connaître

| Fichier | Rôle |
|---------|------|
| `app/app.py` | Interface utilisateur, upload, affichage |
| `scripts/analysis.py` | Moteur d'analyse, calculs statistiques |
| `requirements.txt` | Dépendances (`streamlit`, `pandas`, `openpyxl`) |

## Si tu dois améliorer

- **Ajouter une visualisation** → éditer `app/app.py`, ajouter `plotly` à requirements
- **Changer les colonnes attendues** → éditer `KEY_COLUMNS` dans `scripts/analysis.py`
- **Modifier l'interface** → éditer la section "Interface principale" de `app/app.py`
- **Ajouter une analyse** → ajouter une méthode `_analyze_xyz()` dans `InterventionAnalyzer`

## Dépendances

Minimales et stables :
- `streamlit` ≥ 1.28.0
- `pandas` ≥ 2.0.0
- `openpyxl` ≥ 3.1.0

## Notes de sécurité

✅ Aucun fichier disque → variables locales uniquement  
✅ Pas de sauvegarde BD → tout en RAM  
✅ Cache Streamlit → sessiones isolées par utilisateur  
✅ Pas de loggeur → audit trail minimal  

C'est confidentiel by design.
