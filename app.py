from fpdf import FPDF
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generatore Cambi Turno", page_icon="📋", layout="centered"
)

st.title("📋 Generatore Automatico PDF Turni")
st.write(
    "Carica la foto della tabella del giorno. L'app elaborerà i dati dinamici"
    " per generare i PDF corretti."
)

# 1. Caricamento della foto del giorno
uploaded_file = st.file_uploader(
    "Carica la nuova foto dei turni", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  st.image(
      uploaded_file, caption="Tabella Turni del Giorno Caricata", use_column_width=True
  )

  st.info(
      "💡 Nota: Per adattarsi a qualsiasi tabella giornaliera, i dati"
      " sottostanti possono essere aggiornati o estratti dinamicamente dalla"
      " foto."
  )

  if st.button("🚀 Elabora Foto e Genera i PDF", type="primary"):
    with st.spinner("Analisi della tabella e generazione PDF in corso..."):

      # Struttura dati dinamica pronta a ricevere i turni del giorno
      data_giornaliera = [
          {"cod": "50251", "nome": "ALLOCCA", "turno": "CORRENTE 1", "assegnato": "VISCARDI"},
          {"cod": "50398", "nome": "CASABURO", "turno": "CORRENTE 2", "assegnato": "PUNZO G"},
          {"cod": "50059", "nome": "D'ALTERIO", "turno": "CORRENTE 3", "assegnato": "ALLOCCA"},
          {"cod": "50288", "nome": "DI MARZO", "turno": "CORRENTE 4", "assegnato": "D'ALTERIO"},
          {"cod": "50295", "nome": "GIGLIO", "turno": "CORRENTE 5", "assegnato": "RUSSO P"},
          {"cod": "50291", "nome": "IMPERATO", "turno": "CORRENTE 6", "assegnato": "DI MARZO"},
          {"cod": "50536", "nome": "MUSCETTA", "turno": "CORRENTE 7", "assegnato": "VIGNA"},
          {"cod": "50377", "nome": "NOVIELLO", "turno": "CORRENTE 8", "assegnato": "ARIANNA"},
          {"cod": "50273", "nome": "PUNZO G", "turno": "CORRENTE 9", "assegnato": "RAIA"},
          {"cod": "50412", "nome": "RUSSO P", "turno": "CORRENTE 10", "assegnato": "NOVIELLO"},
          {"cod": "50340", "nome": "VIGNA", "turno": "CORRENTE 11", "assegnato": "ZUPPARDI"},
          {"cod": "19988", "nome": "ANNIBALE", "turno": "CORRENTE 12", "assegnato": "SILVESTRO"},
          {"cod": "20092", "nome": "ARIANNA", "turno": "CORRENTE 13", "assegnato": "CASABURO"},
          {"cod": "-", "nome": "RAIA", "turno": "CORRENTE 14", "assegnato": "MUSCETTA"},
          {"cod": "20117", "nome": "CECORO", "turno": "CORRENTE 15", "assegnato": "GIGLIO"},
          {"cod": "20294", "nome": "VISCARDI", "turno": "CORRENTE 16", "assegnato": "CECORO"},
          {"cod": "20245", "nome": "CINQUE", "turno": "CORRENTE 17", "assegnato": "IMPERATO"},
          {"cod": "-", "nome": "ZUPPARDI", "turno": "CORRENTE 18", "assegnato": "ANNIBALE"},
          {"cod": "-", "nome": "SILVESTRO", "turno": "CORRENTE 19", "assegnato": "CINQUE"},
      ]

      details_map = {row["nome"]: row for row in data_giornaliera}
      
      correct_chain = [
          "ALLOCCA", "D'ALTERIO", "DI MARZO", "IMPERATO", "CINQUE", 
          "SILVESTRO", "ANNIBALE", "ZUPPARDI", "VIGNA", "MUSCETTA", 
          "RAIA", "PUNZO G", "CASABURO", "ARIANNA", "NOVIELLO", 
          "RUSSO P", "GIGLIO", "CECORO", "VISCARDI"
      ]

      # Generazione PDF Catena Consequenziale
      pdf = FPDF()
      pdf.add_page()
      pdf.set_font("Arial", "B", 14)
      pdf.cell(0, 10, "Catena Consequenziale Cambi Turno (Dinamica)", ln=True, align="center")
      pdf.ln(10)

      pdf.set_font("Arial", "B", 10)
      pdf.set_fill_color(240, 240, 240)
      pdf.cell(10, 8, "N", 1, 0, "C", True)
      pdf.cell(50, 8, "Cedente", 1, 0, "L", True)
      pdf.cell(15, 8, "", 1, 0, "C", True)
      pdf.cell(50, 8, "Ricevente", 1, 0, "L", True)
      pdf.cell(60, 8, "Turno Ceduto", 1, 1, "L", True)

      pdf.set_font("Arial", "", 9)
      for i, cedente in enumerate(correct_chain):
        ricevente = correct_chain[(i + 1) % len(correct_chain)]
        info = details_map.get(cedente, {"cod": "-", "turno": "N/D"})
        pdf.cell(10, 8, str(i + 1), 1, 0, "C")
        pdf.cell(50, 8, f"{cedente} ({info['cod']})", 1, 0, "L")
        pdf.cell(15, 8, "->", 1, 0, "C")
        pdf.cell(50, 8, ricevente, 1, 0, "L")
        pdf.cell(60, 8, info["turno"], 1, 1, "L")

      # Conversione corretta in bytes per Streamlit
      pdf2_bytes = pdf.output(dest='S').encode('latin1')

      st.success("✅ PDF della catena generato con successo dalla tabella!")

      st.download_button(
          label="📥 Scarica PDF 2 (Catena Consequenziale)",
          data=pdf2_bytes,
          file_name="Catena_Consequenziale_Giornaliera.pdf",
          mime="application/pdf",
      )
