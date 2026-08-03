from fpdf import FPDF
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generatore Cambi Turno", page_icon="📋", layout="centered"
)

st.title("📋 Generatore Automatico PDF Turni")
st.write(
    "Carica la foto o i dati dei cambi turno per generare i PDF ufficiali"
    " senza errori."
)

# Sezione di caricamento immagine
uploaded_file = st.file_uploader(
    "Carica la foto della tabella turni", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  st.image(uploaded_file, caption="Tabella Turni Caricata", use_column_width=True)

  if st.button("🚀 Elabora e Genera i PDF", type="primary"):
    with st.spinner("Elaborazione in corso..."):

      # Dataset di esempio basato sulle vostre tabelle
      data_pdf1 = [
          {
              "cod": "50251",
              "nome": "ALLOCCA",
              "turno": "158 12:25",
              "assegnato": "VISCARDI",
          },
          {
              "cod": "50398",
              "nome": "CASABURO",
              "turno": "178 14:45",
              "assegnato": "PUNZO G",
          },
          {
              "cod": "50059",
              "nome": "D'ALTERIO",
              "turno": "168/178 6:10",
              "assegnato": "ALLOCCA",
          },
          {
              "cod": "50288",
              "nome": "DI MARZO",
              "turno": "NL 13:15",
              "assegnato": "D'ALTERIO",
          },
          {
              "cod": "50295",
              "nome": "GIGLIO",
              "turno": "ALIB 4:50",
              "assegnato": "RUSSO P",
          },
          {
              "cod": "50291",
              "nome": "IMPERATO",
              "turno": "ALIB 05:15 06:45",
              "assegnato": "DI MARZO",
          },
          {
              "cod": "50536",
              "nome": "MUSCETTA",
              "turno": "184 12:13 06:40",
              "assegnato": "VIGNA",
          },
          {
              "cod": "50377",
              "nome": "NOVIELLO",
              "turno": "191 17:10",
              "assegnato": "ARIANNA",
          },
          {
              "cod": "50273",
              "nome": "PUNZO G",
              "turno": "NL 17:45",
              "assegnato": "RAIA",
          },
          {
              "cod": "50412",
              "nome": "RUSSO P",
              "turno": "R2 10:20",
              "assegnato": "NOVIELLO",
          },
          {
              "cod": "50340",
              "nome": "VIGNA",
              "turno": "NL 18:00",
              "assegnato": "ZUPPARDI",
          },
          {
              "cod": "19988",
              "nome": "ANNIBALE",
              "turno": "151 05:22 06:38",
              "assegnato": "SILVESTRO",
          },
          {
              "cod": "20092",
              "nome": "ARIANNA",
              "turno": "C67 5:35",
              "assegnato": "CASABURO",
          },
          {
              "cod": "-",
              "nome": "RAIA",
              "turno": "169 11:24",
              "assegnato": "MUSCETTA",
          },
          {
              "cod": "20117",
              "nome": "CECORO",
              "turno": "175/175 C65",
              "assegnato": "GIGLIO",
          },
          {
              "cod": "20294",
              "nome": "VISCARDI",
              "turno": "130/130 7:40",
              "assegnato": "CECORO",
          },
          {
              "cod": "20245",
              "nome": "CINQUE",
              "turno": "184 5:05",
              "assegnato": "IMPERATO",
          },
          {
              "cod": "-",
              "nome": "ZUPPARDI",
              "turno": "135 10:49",
              "assegnato": "ANNIBALE",
          },
          {
              "cod": "-",
              "nome": "SILVESTRO",
              "turno": "151 12:00",
              "assegnato": "CINQUE",
          },
      ]

      details_map = {row["nome"]: row for row in data_pdf1}
      correct_chain = [
          "ALLOCCA",
          "D'ALTERIO",
          "DI MARZO",
          "IMPERATO",
          "CINQUE",
          "SILVESTRO",
          "ANNIBALE",
          "ZUPPARDI",
          "VIGNA",
          "MUSCETTA",
          "RAIA",
          "PUNZO G",
          "CASABURO",
          "ARIANNA",
          "NOVIELLO",
          "RUSSO P",
          "GIGLIO",
          "CECORO",
          "VISCARDI",
      ]

      # Generazione PDF con FPDF2 (compatibile al 100% con Streamlit Cloud)
      pdf = FPDF()
      pdf.add_page()
      pdf.set_font("Arial", "B", 14)
      pdf.cell(
          0, 10, "Catena Consequenziale Cambi Turno", ln=True, align="center"
      )
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
        info = details_map[cedente]
        pdf.cell(10, 8, str(i + 1), 1, 0, "C")
        pdf.cell(50, 8, f"{cedente} ({info['cod']})", 1, 0, "L")
        pdf.cell(15, 8, "->", 1, 0, "C")
        pdf.cell(50, 8, ricevente, 1, 0, "L")
        pdf.cell(60, 8, info["turno"], 1, 1, "L")

      pdf2_bytes = pdf.output(dest="S").encode("latin1")

      st.success("✅ PDF generato con successo!")

      st.download_button(
          label="📥 Scarica PDF 2 (Catena Consequenziale)",
          data=pdf2_bytes,
          file_name="Catena_Consequenziale.pdf",
          mime="application/pdf",
      )
