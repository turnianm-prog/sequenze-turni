import streamlit as st
import pandas as pd
import re
import shutil
from PIL import Image
import pytesseract
from datetime import time

# --- CONFIGURAZIONE TESSERACT OCR ---
# Su Linux / Streamlit Cloud Tesseract viene trovato automaticamente nel PATH se installato via packages.txt.
# Su Windows tenta di individuare il percorso standard se non è già nel PATH.
if not shutil.which("tesseract"):
    import platform
    if platform.system() == "Windows":
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(
    page_title="Generatore Catena di Scambi Turni",
    page_icon="🔄",
    layout="wide"
)

# --- FUNZIONI DI SUPPORTO ---

def estrai_orario_inizio(turno_str):
    """
    Estrae l'orario di inizio da una stringa di turno (es. 'NL 12:50 06:17', '116 11,05', '184 5,35').
    Ritorna un oggetto datetime.time o time(23, 59) se non parsabile.
    """
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


def parse_ocr_text_to_df(raw_text):
    """
    Parsifica il testo grezzo restituito dall'OCR dell'immagine.
    Estrae le righe strutturate nelle colonne: Dipendente | Turno | Assegnato
    """
    lines = raw_text.split('\n')
    data = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Suddivide la riga assumendo:
        # Primo elemento = Dipendente (Cedente originario)
        # Ultimo elemento = Assegnato (Destinatario originario)
        # Elementi centrali = Turno
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


def genera_catena_reale(df, col_dip, col_tur, col_ass, target_hour=time(12, 0)):
    """
    Step 2: Applica la logica di inversione colonne + inversione flusso (dal basso verso l'alto)
    e ruota il cerchio partendo dal turno ~12:00 fino alla chiusura del ciclo.
    """
    # 1. Filtraggio righe con destinatario valido
    df_filtered = df.dropna(subset=[col_ass]).copy()
    df_filtered[col_ass] = df_filtered[col_ass].astype(str).str.strip()
    df_filtered = df_filtered[~df_filtered[col_ass].str.upper().isin(['', 'NAN', 'NONE', '-', 'NULL'])]
    
    if df_filtered.empty:
        return None, "Nessuna riga valida trovata con destinatario indicato nella colonna Assegnato."

    # 2. Inversione logica delle colonne e del flusso (dal basso verso l'alto)
    df_reversed = df_filtered.iloc[::-1].reset_index(drop=True)
    
    scambi = []
    for _, row in df_reversed.iterrows():
        scambi.append({
            'cedente': str(row[col_ass]),
            'ricevente': str(row[col_dip]),
            'turno': str(row[col_tur]),
            'orario_inizio': estrai_orario_inizio(row[col_tur])
        })
    
    # 3. Individuazione punto di avvio (turno >= 12:00 più vicino)
    orari_validi = [s for s in scambi if s['orario_inizio'] >= target_hour and s['orario_inizio'] != time(23, 59)]
    
    if not orari_validi:
        orari_validi = [s for s in scambi if s['orario_inizio'] != time(23, 59)]
        
    if not orari_validi:
        start_item = scambi[0]
    else:
        start_item = min(orari_validi, key=lambda x: (x['orario_inizio'].hour - target_hour.hour)*60 + (x['orario_inizio'].minute - target_hour.minute))
    
    # 4. Propagazione ciclica e chiusura dell'anello
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
Questa applicazione gestisce il flusso completo a **2 Step**:
1. **Step 1**: Carica la foto/file della variazione ed estrae la **Catena Consequenziale** (Dati intermedi).
2. **Step 2**: Parte dal risultato dello Step 1, inverte il flusso (dal basso verso l'alto e colonne scambiate) 
   e genera la **Catena di Scambi Reale** con avvio al turno delle **12:00** (o subito successivo).
""")

# Sidebar Upload
st.sidebar.header("📁 Caricamento File")
uploaded_file = st.sidebar.file_uploader(
    "Carica Immagine o File (PNG, JPG, CSV, XLSX)", 
    type=["png", "jpg", "jpeg", "csv", "xlsx"]
)

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    df_step1 = pd.DataFrame()
    
    # ====================================================
    # STEP 1: Lettura File / OCR Immagine
    # ====================================================
    st.header("📌 Step 1: Estrazione Dati e Catena Consequenziale")
    
    if file_type in ["png", "jpg", "jpeg"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Foto Caricata", width=450)
        
        with st.spinner("Esecuzione OCR in corso..."):
            try:
                # Esegue OCR (se disponibile il pacchetto italiano usa 'ita', altrimenti standard)
                try:
                    raw_text = pytesseract.image_to_string(image, lang='ita')
                except Exception:
                    raw_text = pytesseract.image_to_string(image)
                    
                df_step1 = parse_ocr_text_to_df(raw_text)
                
                if df_step1.empty:
                    st.warning("⚠️ L'OCR non è riuscito a formattare automaticamente le colonne. Inserisci o modifica i dati nella tabella sotto.")
            except Exception as e:
                st.error(f"Errore durante l'esecuzione dell'OCR: {e}")
                st.info("Assicurati di aver aggiunto 'tesseract-ocr' nel file packages.txt su Streamlit Cloud.")
                
    elif file_type in ["csv", "xlsx"]:
        df_step1 = pd.read_csv(uploaded_file) if file_type == "csv" else pd.read_excel(uploaded_file)
    
    # Visualizzazione / Edizione Dati Step 1
    if not df_step1.empty:
        st.subheader("Tabella Dati Estratti (Catena Consequenziale / PDF 2)")
        df_step1 = st.data_editor(df_step1, use_container_width=True, num_rows="dynamic")
        
        # Download risultati Step 1
        csv_step1 = df_step1.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Scarica Dati Step 1 (CSV)",
            data=csv_step1,
            file_name="Catena_Consequenziale_Step1.csv",
            mime="text/csv"
        )
    
    # ====================================================
    # STEP 2: Generazione Catena di Scambi Reale
    # ====================================================
    st.markdown("---")
    st.header("📌 Step 2: Generazione della Catena di Scambi Reale")
    
    if not df_step1.empty:
        st.sidebar.subheader("Mappatura Colonne per Step 2")
        cols = list(df_step1.columns)
        
        # Selezione automatica delle colonne se presenti
        def_dip = 0
        def_tur = 1 if len(cols) > 1 else 0
        def_ass = 2 if len(cols) > 2 else 0
        
        col_dipendente = st.sidebar.selectbox("Colonna Dipendente / Cedente Orig.", cols, index=def_dip)
        col_turno = st.sidebar.selectbox("Colonna Turno", cols, index=def_tur)
        col_assegnato = st.sidebar.selectbox("Colonna Assegnato / Ricevente Orig.", cols, index=def_ass)
        
        target_hour = st.sidebar.time_input("Orario Target Partenza", time(12, 0))
        
        if st.button("🚀 ELABORA CATENA DI SCAMBI REALE", type="primary"):
            res_df, error = genera_catena_reale(df_step1, col_dipendente, col_turno, col_assegnato, target_hour)
            
            if error:
                st.error(error)
            else:
                st.success("✅ Catena di Scambi Reale generata con successo!")
                
                st.subheader("Tabella Finale della Catena di Scambi")
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                
                # Verifica anello chiuso
                primo = res_df.iloc[0]['Chi cede']
                ultimo = res_df.iloc[-1]['Chi riceve']
                st.info(f"💡 **Verifica Ciclo**: La catena si apre con **{primo}** (che cede il turno delle 12:00 o successivo) e si chiude correttamente con **{ultimo}** come ultimo ricevente al passaggio finale #{len(res_df)}.")
                
                # Download finale
                csv_step2 = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Scarica Tabella Catena Reale Finale (CSV)",
                    data=csv_step2,
                    file_name="Catena_Scambi_Reale_Finale.csv",
                    mime="text/csv"
                )
    else:
        st.info("Inserisci o carica i dati nello Step 1 per poter procedere allo Step 2.")

else:
    st.info("👈 Carica un'immagine o un file dalla barra laterale per iniziare il processo.")
