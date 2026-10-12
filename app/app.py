import streamlit as st
import pandas as pd
import json
from io import BytesIO
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.analysis import InterventionAnalyzer


st.set_page_config(
    page_title="BayWatch - Analyse d'Annulations",
    page_icon="👀",
    layout="wide",
)

st.title("👀 BayWatch")
st.markdown("**Analyse des Annulations d'Interventions** — Simple, rapide, confidentiel")

# Upload
uploaded_file = st.file_uploader(
    "📤 Téléchargez votre fichier Excel",
    type=["xlsx", "xls"],
)

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        analyzer = InterventionAnalyzer(file_bytes)
        results = analyzer.analyze()

        st.success("✅ Fichier chargé")

        # === STATS GLOBALES EN HAUT ===
        st.markdown("## 📊 Statistiques Globales")
        global_stats = results.get('global', {})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Annulations", global_stats.get('total_annulations', 0))
        with col2:
            if results.get('delais'):
                delais = results['delais']
                st.metric("Délai Moyen", f"{delais.get('delai_moyen_jours', 0):.1f} j")
        with col3:
            if results.get('delais'):
                delais = results['delais']
                st.metric("Délai Médian", f"{delais.get('delai_median_jours', 0)} j")
        with col4:
            st.metric("Plage Délais", f"{results.get('delais', {}).get('delai_min_jours', 0)}-{results.get('delais', {}).get('delai_max_jours', 0)} j")

        st.markdown("---")

        # === MOTIFS ===
        if results['par_motif']:
            st.markdown("## 🎯 Annulations par Motif")
            df_motif = pd.DataFrame(
                list(results['par_motif'].items()),
                columns=['Motif', 'Nombre']
            ).sort_values('Nombre', ascending=False)
            col_chart, col_table = st.columns([1, 1])
            with col_chart:
                st.bar_chart(df_motif.set_index('Motif'))
            with col_table:
                st.dataframe(df_motif, use_container_width=True, hide_index=True)

        st.markdown("---")

        # === 2 COLONNES : INTERVENANT & CLIENT ===
        col_interv, col_client = st.columns(2)

        with col_interv:
            st.markdown("### 👤 Intervenants")

            # Top 10 annulations par intervenant
            if results['par_intervenant']:
                st.markdown("**Top 10 Annulations**")
                df_interv = pd.DataFrame(
                    list(results['par_intervenant'].items()),
                    columns=['Intervenant', 'Nombre']
                ).sort_values('Nombre', ascending=False).head(10)
                st.bar_chart(df_interv.set_index('Intervenant'))
                st.dataframe(df_interv, use_container_width=True, hide_index=True)

            # Top motif par intervenant
            if results['motif_par_intervenant']:
                st.markdown("**Motifs par Intervenant (Top 3)**")
                for interv, motifs in list(results['motif_par_intervenant'].items())[:10]:
                    with st.expander(f"🧑‍🔧 {interv}"):
                        df_motifs = pd.DataFrame(list(motifs.items()), columns=['Motif', 'Nombre']).sort_values('Nombre', ascending=False)
                        st.dataframe(df_motifs, use_container_width=True, hide_index=True)

        with col_client:
            st.markdown("### 🏢 Clients")

            # Top 10 annulations par client
            if results['par_client']:
                st.markdown("**Top 10 Annulations**")
                df_client = pd.DataFrame(
                    list(results['par_client'].items()),
                    columns=['Client', 'Nombre']
                ).sort_values('Nombre', ascending=False).head(10)
                st.bar_chart(df_client.set_index('Client'))
                st.dataframe(df_client, use_container_width=True, hide_index=True)

            # Top motif par client
            if results['motif_par_client']:
                st.markdown("**Motifs par Client (Top 3)**")
                for client, motifs in list(results['motif_par_client'].items())[:10]:
                    with st.expander(f"🏢 {client}"):
                        df_motifs = pd.DataFrame(list(motifs.items()), columns=['Motif', 'Nombre']).sort_values('Nombre', ascending=False)
                        st.dataframe(df_motifs, use_container_width=True, hide_index=True)

        # === SERVICES ===
        if results['par_service']:
            st.markdown("## 🔧 Annulations par Service")
            df_service = pd.DataFrame(
                list(results['par_service'].items()),
                columns=['Service', 'Nombre']
            ).sort_values('Nombre', ascending=False)
            st.dataframe(df_service, use_container_width=True, hide_index=True)

        # === TEMPORELLE ===
        temporal = results.get('temporelle', {})
        if temporal.get('par_mois') or temporal.get('par_jour'):
            st.markdown("## 📈 Analyse Temporelle")
            col1, col2 = st.columns(2)

            with col1:
                if temporal.get('par_mois'):
                    st.markdown("### Par Mois")
                    df_mois = pd.DataFrame(list(temporal['par_mois'].items()), columns=['Mois', 'Nombre'])
                    st.line_chart(df_mois.set_index('Mois'))

            with col2:
                if temporal.get('par_jour'):
                    st.markdown("### Par Jour Semaine")
                    df_jour = pd.DataFrame(list(temporal['par_jour'].items()), columns=['Jour', 'Nombre'])
                    st.bar_chart(df_jour.set_index('Jour'))

        # === EXPORTS ===
        st.markdown("---")
        st.markdown("## 📥 Exports")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 CSV",
                analyzer.get_csv_export(),
                file_name="annulations.csv",
                mime="text/csv",
            )
        with col2:
            st.download_button(
                "📥 JSON",
                analyzer.get_stats_json(),
                file_name="stats.json",
                mime="application/json",
            )

        # Debug
        with st.expander("🔧 Colonnes détectées"):
            st.write("**Colonnes du fichier :**", list(analyzer.df.columns))
            st.write("**Colonnes mappées :**", analyzer.mapped_columns)

    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")

else:
    st.info("👈 Téléchargez votre Excel pour commencer")
