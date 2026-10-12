import pandas as pd
import json
from io import BytesIO
from datetime import datetime
import re


class InterventionAnalyzer:
    """Moteur d'analyse pour les annulations d'interventions."""

    KEY_COLUMNS = {
        'date_intervention': ['date_intervention', 'date intervention', 'intervention_date', 'intervention date', 'date', 'début', 'debut'],
        'date_annulation': ['date_annulation', 'date annulation', 'cancellation_date', 'cancellation date', 'date_annul', 'date annul'],
        'motif_annulation': ['motif_annulation', 'motif annulation', 'cancellation_reason', 'reason', 'motif_annul', 'motif annul', 'origine_annul', 'origine annul'],
        'intervenant': ['intervenant', 'technician', 'personnel', 'technician name', 'nom_intervenant', 'nom intervenant', 'nom_intervena', 'nom intervena'],
        'client': ['client', 'company', 'account', 'customer', 'nom_client', 'nom client'],
        'service': ['service', 'department', 'type_service', 'service type', 'prestation', 'agence'],
        'heure_intervention': ['heure_intervention', 'heure intervention', 'intervention_time', 'time'],
    }

    def __init__(self, file_bytes):
        """Initialise l'analyseur avec un fichier Excel."""
        self.file_bytes = file_bytes
        self.df = None
        self.mapped_columns = {}
        self.load_data()

    def load_data(self):
        """Charge les données du fichier Excel en mémoire."""
        self.df = pd.read_excel(BytesIO(self.file_bytes))
        self._map_columns()

    def _map_columns(self):
        """Map automatiquement les colonnes (insensible casse/accents)."""
        df_columns_lower = [self._normalize(col) for col in self.df.columns]

        for key, aliases in self.KEY_COLUMNS.items():
            for alias in aliases:
                alias_normalized = self._normalize(alias)
                if alias_normalized in df_columns_lower:
                    idx = df_columns_lower.index(alias_normalized)
                    self.mapped_columns[key] = self.df.columns[idx]
                    break

    @staticmethod
    def _normalize(text):
        """Normalise un texte (minuscules, sans accents)."""
        text = text.lower()
        text = re.sub(r'[éèêë]', 'e', text)
        text = re.sub(r'[àâä]', 'a', text)
        text = re.sub(r'[ôö]', 'o', text)
        text = re.sub(r'[ûü]', 'u', text)
        text = re.sub(r'[ç]', 'c', text)
        return text

    def _is_yes(self, value):
        """Détecte si une valeur représente 'oui'."""
        if pd.isna(value):
            return False
        str_val = str(value).lower().strip()
        return str_val in ['oui', 'yes', 'true', '1', 'vrai', 'annulé', 'annulee', 'cancelled', 'canceled']

    def analyze(self):
        """Analyse complète des données."""
        if self.df is None or self.df.empty:
            return {}

        results = {
            'global': self._analyze_global(),
            'par_motif': self._analyze_by_motif(),
            'par_intervenant': self._analyze_by_intervenant(),
            'par_client': self._analyze_by_client(),
            'par_service': self._analyze_by_service(),
            'motif_par_intervenant': self._analyze_motif_by_intervenant(),
            'motif_par_client': self._analyze_motif_by_client(),
            'temporelle': self._analyze_temporal(),
            'delais': self._analyze_delais(),
        }

        return results

    def _analyze_global(self):
        """Statistiques globales."""
        total = len(self.df)

        annulations = 0
        if 'date_annulation' in self.mapped_columns:
            col = self.mapped_columns['date_annulation']
            annulations = self.df[col].notna().sum()

        taux = (annulations / total * 100) if total > 0 else 0

        return {
            'total_interventions': int(total),
            'total_annulations': int(annulations),
            'taux_annulation': round(taux, 2),
        }

    def _analyze_by_motif(self):
        """Analyse par motif d'annulation."""
        if 'motif_annulation' not in self.mapped_columns:
            return {}

        col = self.mapped_columns['motif_annulation']
        motifs = self.df[col].value_counts().head(10).to_dict()

        return {motif: int(count) for motif, count in motifs.items()}

    def _analyze_by_intervenant(self):
        """Analyse par intervenant."""
        if 'intervenant' not in self.mapped_columns:
            return {}

        col = self.mapped_columns['intervenant']
        intervenants = self.df[col].value_counts().head(20).to_dict()

        return {intervenant: int(count) for intervenant, count in intervenants.items()}

    def _analyze_by_client(self):
        """Analyse par client."""
        if 'client' not in self.mapped_columns:
            return {}

        col = self.mapped_columns['client']
        clients = self.df[col].value_counts().head(20).to_dict()

        return {client: int(count) for client, count in clients.items()}

    def _analyze_by_service(self):
        """Analyse par service."""
        if 'service' not in self.mapped_columns:
            return {}

        col = self.mapped_columns['service']
        services = self.df[col].value_counts().head(10).to_dict()

        return {service: int(count) for service, count in services.items()}

    def _analyze_motif_by_intervenant(self):
        """Analyse des motifs d'annulation par intervenant (top 10)."""
        if 'intervenant' not in self.mapped_columns or 'motif_annulation' not in self.mapped_columns:
            return {}

        col_interv = self.mapped_columns['intervenant']
        col_motif = self.mapped_columns['motif_annulation']

        # Crosstab motif par intervenant
        crosstab = pd.crosstab(self.df[col_interv], self.df[col_motif])

        # Top motif par intervenant (top 10 intervenants)
        top_intervenants = self.df[col_interv].value_counts().head(10).index
        result = {}

        for interv in top_intervenants:
            motifs = crosstab.loc[interv].nlargest(3).to_dict()
            result[str(interv)] = {motif: int(count) for motif, count in motifs.items()}

        return result

    def _analyze_motif_by_client(self):
        """Analyse des motifs d'annulation par client (top 10)."""
        if 'client' not in self.mapped_columns or 'motif_annulation' not in self.mapped_columns:
            return {}

        col_client = self.mapped_columns['client']
        col_motif = self.mapped_columns['motif_annulation']

        # Crosstab motif par client
        crosstab = pd.crosstab(self.df[col_client], self.df[col_motif])

        # Top motif par client (top 10 clients)
        top_clients = self.df[col_client].value_counts().head(10).index
        result = {}

        for client in top_clients:
            motifs = crosstab.loc[client].nlargest(3).to_dict()
            result[str(client)] = {motif: int(count) for motif, count in motifs.items()}

        return result

    def _analyze_temporal(self):
        """Analyse temporelle (mois, jour semaine, heure)."""
        temporal = {
            'par_mois': {},
            'par_jour': {},
            'par_heure': {},
        }

        if 'date_intervention' in self.mapped_columns:
            col = self.mapped_columns['date_intervention']
            dates = pd.to_datetime(self.df[col], errors='coerce')

            # Par mois
            par_mois = dates.dt.to_period('M').value_counts().sort_index()
            temporal['par_mois'] = {str(k): int(v) for k, v in par_mois.items()}

            # Par jour semaine
            jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            par_jour = dates.dt.dayofweek.value_counts().sort_index()
            temporal['par_jour'] = {jours_fr[k]: int(v) for k, v in par_jour.items()}

        if 'heure_intervention' in self.mapped_columns:
            col = self.mapped_columns['heure_intervention']
            heures = pd.to_datetime(self.df[col], format='%H:%M', errors='coerce').dt.hour
            par_heure = heures.value_counts().sort_index()
            temporal['par_heure'] = {f"{k:02d}h": int(v) for k, v in par_heure.items()}

        return temporal

    def _analyze_delais(self):
        """Analyse des délais entre annulation et intervention."""
        if 'date_intervention' not in self.mapped_columns or 'date_annulation' not in self.mapped_columns:
            return {}

        col_interv = self.mapped_columns['date_intervention']
        col_annul = self.mapped_columns['date_annulation']

        dates_interv = pd.to_datetime(self.df[col_interv], errors='coerce')
        dates_annul = pd.to_datetime(self.df[col_annul], errors='coerce')

        delais = (dates_interv - dates_annul).dt.days
        delais = delais[delais.notna()]

        if len(delais) == 0:
            return {}

        return {
            'delai_moyen_jours': round(delais.mean(), 2),
            'delai_median_jours': int(delais.median()),
            'delai_min_jours': int(delais.min()),
            'delai_max_jours': int(delais.max()),
        }

    def get_csv_export(self):
        """Exporte les données en CSV."""
        return self.df.to_csv(index=False)

    def get_stats_json(self):
        """Retourne les statistiques en JSON."""
        return json.dumps(self.analyze(), indent=2, default=str)
