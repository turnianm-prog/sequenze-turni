import streamlit as st
import pandas as pd
import re
import json
from datetime import time
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Generatore Catena di Scambi Turni",
    page_icon="🔄",
    layout="wide"
)

# --- FUNZIONI DI SUPPORTO ---

def estrai_orario_inizio(turno_str):
    if pd.isna(turno_str):
        return time(23, 59)
    
    turno_str = str(turno_str).replace(',', ':')
    match = re.search(r'(\d{1,2})[:\.](\d{2})', turno_str)
    if match:
        ora, minuto = int(match.group(1)), int(match.group(2))
        if 0 <= ora < 24 and 0 <= minuto < 60:
            return time(ora, minuto)
            
    match_ora = re.search(r'\b(\d{1,2})\b', turno_str)
    if match_ora:
        ora = int(match_ora.group(1))
        if 0 <= ora < 24:
            return time(ora, 0)
            
    return time(23, 59)


def analizza_foto_con_gemini(uploaded_file, api_key):
    """
    Step 1: Utilizza Google Gemini Flash per leggere la foto del foglio manoscritto.
    """
    client = genai.Client(api_key=api_key)
    image = Image.open(uploaded_file)
    
    prompt = """
    Sei un assistente esperto nella lettura di tabelle di turno di servizio scritte a mano.
    La foto allegata mostra una tabella con due colonne principali di fogli affiancati.
    
    Estrai TUTTE e sole le righe che contengono una variazione o un nome scritto a mano nella colonna 'Assegnato' (terza colonna di ciascun blocco).
    
    Istruzioni di pulizia:
    1. 'Dipendente': indica il cognome del dipendente titolare (se c'è una matricola numerica all'inizio tipo 50251 - ALLOCCA, estrai solo COGNOME, es. ALLOCCA).
    2. 'Turno': estrai la stringa esatta del turno (es. ALIB 11:35 06:25, 184 5,35, NL 18,10, ecc.).
    3. 'Assegnato': estrai il cognome del destinatario scritto a mano a destra (es. CONSON, PACE, BRUNO, ecc.).
    
    Restituisci unicamente una risposta formattata in JSON valido come lista di oggetti con le chiavi: "Dipendente", "Turno", "Assegnato".
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    parsed = json.loads(response.text)
    
    if isinstance(parsed, list):
        return pd.DataFrame(parsed)
    elif isinstance(parsed, dict):
        for val in parsed.values():
            if isinstance(val, list):
                return pd.DataFrame(val)
        return pd.DataFrame([parsed])
    return pd.DataFrame()


def genera_catena_reale(df, col_dip, col_tur, col_ass, target_hour=time(12, 0)):
    df_filtered = df.dropna(subset=[col_ass]).copy()
    df_filtered[col_ass] = df_filtered[col_ass].astype(str).str.strip()
    df_filtered = df_filtered[~df_filtered[col_ass].str.upper().isin(['', 'NAN', 'NONE', '-', 'NULL'])]
    
    if df_filtered.empty:
        return None, "Nessuna riga valida trovata nella tabella."

    # Inversione dal basso verso l'alto
    df_reversed = df_filtered.iloc[::-1].reset_index(drop=True)
    
    scambi = []
    for _, row in df_reversed.iterrows():
        scambi.append({
            'cedente': str(row[col_ass]),
            'ricevente': str(row[col_dip]),
            'turno': str(row[col_tur]),
            'orario_inizio': estrai_orario_inizio(row[col_tur])
        })
    
    orari_validi = [s for s in scambi if s['orario_inizio'] >= target_hour and s['orario_inizio'] != time(23, 59)]
    
    if not orari_validi:
        orari_validi = [s for s in scambi if s['orario_inizio'] != time(23, 59)]
        
    if not orari_validi:
        start_item = scambi[0]
    else:
        start_item = min(orari_validi, key=lambda x: (x['orario_inizio'].hour - target_hour.hour)*60 + (x['orario_inizio'].minute - target_hour.minute))
    
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

st.sidebar.header("⚙️ Configurazione API")

api_key = ""
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

api_key_input = st.sidebar.text_input(
    "Gemini API Key", 
    value=api_key, 
    type="password", 
    help="Inserisci la tua chiave Google Gemini"
)

if api_key_input:
    api_key = api_key_input

uploaded_file = st.sidebar.file_uploader(
    "Carica Foto (JPG/PNG) o File (CSV/XLSX)", 
    type=["png", "jpg", "jpeg", "csv", "xlsx"]
)

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if "df_step1" not in st.session_state:
        st.session_state.df_step1 = pd.DataFrame()
    
    # STEP 1
    st.header("📌 Step 1: Estrazione Tabella Variazioni")
    
    if file_type in ["png", "jpg", "jpeg"]:
        st.image(uploaded_file, caption="Foto Caricata", width=450)
        
        if st.button("🔍 Leggi Foto con Gemini AI"):
            if not api_key:
                st.error("⚠️ Inserisci la chiave API Gemini nella barra laterale o nei Secrets di Streamlit.")
            else:
                with st.spinner("L'AI sta analizzando la foto del foglio manoscritto..."):
                    try:
                        st.session_state.df_step1 = analizza_foto_con_gemini(uploaded_file, api_key)
                        st.success("Estrazione completata con successo!")
                    except Exception as e:
                        st.error(f"Errore durante l'analisi dell'immagine: {e}")
                        
    elif file_type in ["csv", "xlsx"]:
        if st.session_state.df_step1.empty:
            st.session_state.df_step1 = pd.read_csv(uploaded_file) if file_type == "csv" else pd.read_excel(uploaded_file)

    if not st.session_state.df_step1.empty:
        st.subheader("Tabella Dati Estratti (Modificabile)")
        st.session_state.df_step1 = st.data_editor(
            st.session_state.df_step1, 
            use_container_width=True, 
            num_rows="dynamic",
            key="editor_step1"
        )
        
        csv_s1 = st.session_state.df_step1.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Scarica Dati Step 1 (CSV)",
            data=csv_s1,
            file_name="Catena_Consequenziale_Step1.csv",
            mime="text/csv"
        )

    # STEP 2
    st.markdown("---")
    st.header("📌 Step 2: Generazione Catena di Scambi Reale")
    
    if not st.session_state.df_step1.empty:
        cols = list(st.session_state.df_step1.columns)
        
        st.sidebar.subheader("Mappatura Colonne per Step 2")
        col_dip = st.sidebar.selectbox("Colonna Dipendente / Cedente Orig.", cols, index=0)
        col_tur = st.sidebar.selectbox("Colonna Turno", cols, index=1 if len(cols) > 1 else 0)
        col_ass = st.sidebar.selectbox("Colonna Assegnato / Ricevente Orig.", cols, index=2 if len(cols) > 2 else 0)
        
        target_hour = st.sidebar.time_input("Orario Target Partenza", time(12, 0))
        
        if st.button("🚀 ELABORA CATENA DI SCAMBI REALE", type="primary"):
            res_df, error = genera_catena_reale(
                st.session_state.df_step1, 
                col_dip, col_tur, col_ass, 
                target_hour
            )
            
            if error:
                st.error(error)
            else:
                st.success("✅ Catena di Scambi Reale generata perfettamente!")
                
                st.subheader("Tabella Finale della Catena")
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                
                primo = res_df.iloc[0]['Chi cede']
                ultimo = res_df.iloc[-1]['Chi riceve']
                st.info(f"💡 **Verifica Anello**: La catena parte da **{primo}** e si chiude con **{ultimo}** al passaggio #{len(res_df)}.")
                
                csv_s2 = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Scarica Tabella Catena Reale Finale (CSV)",
                    data=csv_s2,
                    file_name="Catena_Scambi_Reale_Finale.csv",
                    mime="text/csv"
                )
    else:
        st.info("Esegui l'analisi dello Step 1 per poter generare la catena di scambi dello Step 2.")
else:
    st.info("👈 Carica la foto dalla barra laterale per iniziare.")
