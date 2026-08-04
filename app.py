import streamlit as st
import pandas as pd
import re
import io
from PIL import Image
import pytesseract
from datetime import time

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
    return time(23, 59)

def parse_ocr_text_to_df(raw_text):
    """
    Parser basato sull'output OCR dell'immagine.
    Estrae le righe strutturate in: Dipendente | Turno | Assegnato
    """
    lines = raw_text.split('\n')
    data = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Regex per identificare una riga con Nome, Turno/Orario, Destinatario
        # Es: ALLOCCA ALIB 11:35 06:25 CONSON
        parts = line.split()
        if len(parts) >= 3:
            dipendente = parts[0]
            assegnato = parts[-1]
            turno = " ".join(parts[1:-1])
            data.append({
                "Dipendente": dipendente,
                "Turno": turno,
                "Assegnato": assegnato
            })
            
    return pd.DataFrame(data)

def genera_catena_reale(df, target_hour=time(12, 0)):
    df_filtered = df.dropna(subset=['Assegnato']).copy()
    df_filtered['Assegnato'] = df_filtered['Assegnato'].astype(str).str.strip()
    df_filtered = df_filtered[~df_filtered['Assegnato'].str.upper().isin(['', 'NAN', 'NONE', '-'])]
    
    if df_filtered.empty:
        return None, "Nessun dato valido trovato per creare la catena."

    # Inversione flusso e colonne (dal basso verso l'alto)
    df_reversed = df_filtered.iloc[::-1].reset_index(drop=True)
    
    scambi = []
    for _, row in df_reversed.iterrows():
        scambi.append({
            'cedente': str(row['Assegnato']),
            'ricevente': str(row['Dipendente']),
            'turno': str(row['Turno']),
            'orario_inizio': estrai_orario_inizio(row['Turno'])
        })
    
    # Trova il punto di avvio (turno ~12:00 o subito successivo)
    orari_validi = [s for s in scambi if s['orario_inizio'] >= target_hour and s['orario_inizio'] != time(23, 59)]
    start_item = min(orari_validi, key=lambda x: (x['orario_inizio'].hour - 12)*60 + x['orario_inizio'].minute) if orari_validi else scambi[0]
    
    # Ricostruzione e rotazione ciclica
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

st.title("🔄 Generatore Catena di Scambi Turni (2 Step)")

# Sidebar Upload
uploaded_file = st.sidebar.file_uploader(
    "Upload Foto/Immagine o PDF/Excel", 
    type=["png", "jpg", "jpeg", "csv", "xlsx"]
)

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    # ----------------------------------------------------
    # STEP 1: Lettura Immagine e Generazione Dati Intermedi (PDF 2)
    # ----------------------------------------------------
    st.header("📌 Step 1: Estrazione Dati dall'Immagine / File")
    
    if file_type in ["png", "jpg", "jpeg"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Immagine Caricata", width=400)
        
        with st.spinner("Esecuzione OCR e lettura dati dall'immagine..."):
            # Estrazione testo con OCR
            raw_text = pytesseract.image_to_string(image)
            df_step1 = parse_ocr_text_to_df(raw_text)
            
        st.subheader("Catena Consequenziale Estratta (PDF 2)")
        st.dataframe(df_step1, use_container_width=True)
        
    elif file_type in ["csv", "xlsx"]:
        df_step1 = pd.read_csv(uploaded_file) if file_type == "csv" else pd.read_excel(uploaded_file)
        st.subheader("Tabella Catena Consequenziale Caricata (PDF 2)")
        st.dataframe(df_step1, use_container_width=True)

    # ----------------------------------------------------
    # STEP 2: Elaborazione della Catena di Scambi Reale
    # ----------------------------------------------------
    st.markdown("---")
    st.header("📌 Step 2: Generazione Catena di Scambi Reale")
    
    target_hour = st.time_input("Orario Target Partenza", time(12, 0))
    
    if st.button("🚀 ELABORA CATENA DI SCAMBI", type="primary"):
        if 'df_step1' in locals() and not df_step1.empty:
            res_df, err = genera_catena_reale(df_step1, target_hour)
            
            if err:
                st.error(err)
            else:
                st.success("Catena Reale Calcolata con Successo!")
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                
                # Verifica Anello
                primo = res_df.iloc[0]['Chi cede']
                ultimo = res_df.iloc[-1]['Chi riceve']
                st.info(f"**Verifica Chiusura**: La catena parte da **{primo}** (cede il turno delle 12:00+) e si chiude con **{ultimo}** come ultimo ricevente.")
                
                # Bottone Download
                csv_bytes = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Scarica Tabella Finale (CSV)",
                    data=csv_bytes,
                    file_name="Catena_Scambi_Reale_Finale.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Nessun dato disponibile dallo Step 1.")
else:
    st.info("👈 Carica l'immagine iniziale dalla barra laterale per avviare il processo a 2 step.")
