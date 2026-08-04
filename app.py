import streamlit as st
import pandas as pd
import re
from datetime import datetime, time

st.set_page_config(
    page_title="Generatore Catena di Scambi Turni",
    page_icon="🔄",
    layout="wide"
)

def estrai_orario_inizio(turno_str):
    """
    Estrae l'orario di inizio da una stringa turno (es. 'NL 12:50 06:17', '116 11,05', '184 5,35').
    Ritorna un oggetto datetime.time per il confronto o time(23, 59) se non trovato.
    """
    if pd.isna(turno_str):
        return time(23, 59)
    
    turno_str = str(turno_str).replace(',', ':')
    match = re.search(r'(\d{1,2})[:\.](\d{2})', turno_str)
    
    if match:
        ora = int(match.group(1))
        minuto = int(match.group(2))
        if 0 <= ora < 24 and 0 <= minuto < 60:
            return time(ora, minuto)
    
    # Se c'è solo un'ora espressa in modo generico (es. 12:00)
    match_ora = re.search(r'\b(\d{1,2})\b', turno_str)
    if match_ora:
        ora = int(match_ora.group(1))
        if 0 <= ora < 24:
            return time(ora, 0)
            
    return time(23, 59)

def elabora_catena_scambi(df, col_dipendente, col_turno, col_assegnato, orario_target=time(12, 0)):
    # 1. FILTRAGGIO: Considera solo righe con Assegnato valido (non vuoto/non 'nan')
    df_filtered = df.dropna(subset=[col_assegnato]).copy()
    df_filtered[col_assegnato] = df_filtered[col_assegnato].astype(str).str.strip()
    df_filtered = df_filtered[df_filtered[col_assegnato] != '']
    df_filtered = df_filtered[~df_filtered[col_assegnato].str.upper().isin(['NAN', 'NONE', '-'])]
    
    if df_filtered.empty:
        return None, "Nessuna riga valida trovata con destinatario nella colonna Assegnato."

    # 2. INVERSIONE LOGICA DELLE COLONNE E DEL FLUSSO
    # Inversione dal basso verso l'alto
    df_reversed = df_filtered.iloc[::-1].reset_index(drop=True)
    
    # Costruzione mappa di scambio inversa:
    # Chi cede (originariamente Assegnato) -> Chi riceve (originariamente Dipendente)
    # E salviamo il turno del cedente (turno originario del dipendente uscente)
    scambi = []
    for _, row in df_reversed.iterrows():
        scambi.append({
            'cedente': str(row[col_assegnato]),
            'ricevente': str(row[col_dipendente]),
            'turno': str(row[col_turno]),
            'orario_inizio': estrai_orario_inizio(row[col_turno])
        })
    
    # 3. PUNTO DI INIZIO: Trova il turno che inizia attorno alle 12:00 (o immediatamente successivo)
    # Filtriamo per orari >= 12:00 e prendiamo il più vicino a 12:00
    orari_validi = [s for s in scambi if s['orario_inizio'] >= orario_target and s['orario_inizio'] != time(23, 59)]
    
    if not orari_validi:
        # Se non ci sono orari >= 12:00, prendiamo l'orario più vicino in assoluto
        orari_validi = [s for s in scambi if s['orario_inizio'] != time(23, 59)]
        
    if not orari_validi:
        # Fallback al primo elemento se nessun orario è parsabile
        start_item = scambi[0]
    else:
        # Ordina per vicinanza a 12:00 (in avanti)
        start_item = min(orari_validi, key=lambda x: (x['orario_inizio'].hour - 12)*60 + x['orario_inizio'].minute)
    
    # 4. PROPAGAZIONE E CHIUSURA CATENA
    # Troviamo l'indice di partenza
    start_idx = scambi.index(start_item)
    n = len(scambi)
    
    catena_finale = []
    for i in range(n):
        idx = (start_idx + i) % n
        item = scambi[idx]
        catena_finale.append({
            "# Passaggio": i + 1,
            "Chi cede": item['cedente'],
            "Chi riceve": item['ricevente'],
            "Turno del Cedente": item['turno']
        })
        
    return pd.DataFrame(catena_finale), None


# --- INTERFACCIA UTENTE STREAMLIT ---
st.title("🔄 Generatore Catena di Scambi Turni")
st.markdown("""
Questa applicazione calcola la **Catena di Scambi Reale** invertendo le colonne e il flusso (dal basso verso l'alto) 
e impostando l'avvio al turno delle **12:00** (o immediatamente successivo).
""")

uploaded_file = st.sidebar.file_uploader("Carica File Excel o CSV", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.subheader("1. Anteprima Dati Caricati")
        st.dataframe(df.head(), use_container_width=True)
        
        # Mappatura Colonne
        st.sidebar.subheader("Mappatura Colonne")
        col_dipendente = st.sidebar.selectbox("Colonna Dipendente / Uscente", df.columns, index=0)
        
        # Tentativo di selezione automatica delle altre colonne
        def_turno_idx = 1 if len(df.columns) > 1 else 0
        def_ass_idx = 2 if len(df.columns) > 2 else 0
        
        col_turno = st.sidebar.selectbox("Colonna Turno", df.columns, index=def_turno_idx)
        col_assegnato = st.sidebar.selectbox("Colonna Assegnato / Destinatario", df.columns, index=def_ass_idx)
        
        target_hour = st.sidebar.time_input("Orario Target Partenza", time(12, 0))
        
        if st.sidebar.button("⚡ Calcola Catena di Scambi", type="primary"):
            res_df, error = elabora_catena_scambi(df, col_dipendente, col_turno, col_assegnato, target_hour)
            
            if error:
                st.error(error)
            else:
                st.success("Catena generata con successo!")
                
                st.subheader("2. Catena di Scambi Reale")
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                
                # Info sul ciclo
                primo = res_df.iloc[0]['Chi cede']
                ultimo = res_df.iloc[-1]['Chi riceve']
                st.info(f"**Verifica Chiusura Ciclo**: La catena inizia con **{primo}** e termina con **{ultimo}** come destinatario finale.")
                
                # Download CSV
                csv = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Tabella Catena (CSV)",
                    data=csv,
                    file_name="Catena_Scambi_Reale.csv",
                    mime="text/csv"
                )
    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")
else:
    st.info("👆 Carica un file Excel o CSV dalla barra laterale per iniziare.")
