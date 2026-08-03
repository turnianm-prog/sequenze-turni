from fpdf import FPDF
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generatore Cambi Turno", page_icon="📋", layout="centered"
)

st.title("📋 Generatore Automatico dei 3 PDF Turni")
st.write(
    "Carica la foto della tabella del giorno. Inserisci o verifica i dati"
    " sottostanti e genera i documenti ufficiali."
)

uploaded_file = st.file_uploader(
    "Carica la nuova foto dei turni", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  st.image(
      uploaded_file, caption="Tabella Turni del Giorno Caricata", use_column_width=True
  )

  st.info(
      "💡 **Tabella del Giorno**: Inserisci o incolla i dati visibili nella foto"
      " appena caricata. Questa tabella si azzera ad ogni nuova foto."
  )

  # Usiamo un template vuoto o righe vuote così non ci sono dati "vecchi" residui
  if "last_file" not in st.session_state or st.session_state["last_file"] != uploaded_file.name:
    st.session_state["last_file"] = uploaded_file.name
    # Creiamo righe vuote pronte per essere compilate con i dati della nuova foto
    st.session_state["df_data"] = [
        {"N": i, "Dipendente": "", "Codice": "", "Turno": "", "Assegnato A": ""}
        for i in range(1, 15)
    ]

  df_editable = st.data_editor(
      pd.DataFrame(st.session_state["df_data"]),
      num_rows="dynamic",
      use_container_width=True,
  )

  if st.button("🚀 Genera i 3 PDF Ufficiali", type="primary"):
    with st.spinner("Generazione documenti in corso..."):

      data_giornaliera = []
      correct_chain = []
      
      for _, row in df_editable.iterrows():
        nome = str(row["Dipendente"]).strip()
        if nome and nome != "nan":
          data_giornaliera.append({
              "cod": str(row["Codice"]),
              "nome": nome,
              "turno": str(row["Turno"]),
              "assegnato": str(row["Assegnato A"]),
          })
          correct_chain.append(nome)

      details_map = {row["nome"]: row for row in data_giornaliera}

      # --- PDF 1: Variazioni Servizio ---
      pdf1 = FPDF()
      pdf1.add_page()
      pdf1.set_font("Arial", "B", 12)
      pdf1.cell(
          0,
          10,
          "Variazioni Servizio - Tabella Giornaliera",
          ln=True,
          align="center",
      )
      pdf1.ln(5)
      pdf1.set_font("Arial", "B", 9)
      pdf1.cell(10, 7, "N", 1, 0, "C", True)
      pdf1.cell(60, 7, "Dipendente", 1, 0, "L", True)
      pdf1.cell(60, 7, "Turno", 1, 0, "L", True)
      pdf1.cell(60, 7, "Assegnato A", 1, 1, "L", True)
      pdf1.set_font("Arial", "", 9)
      for idx, row in enumerate(data_giornaliera, 1):
        pdf1.cell(10, 7, str(idx), 1, 0, "C")
        pdf1.cell(60, 7, f"{row['nome']} ({row['cod']})", 1, 0, "L")
        pdf1.cell(60, 7, row["turno"], 1, 0, "L")
        pdf1.cell(60, 7, row["assegnato"], 1, 1, "L")
      pdf1_bytes = bytes(pdf1.output())

      # --- PDF 2: Catena Consequenziale ---
      pdf2 = FPDF()
      pdf2.add_page()
      pdf2.set_font("Arial", "B", 12)
      pdf2.cell(
          0,
          10,
          "Catena Consequenziale Cambi Turno (Flusso Continuo)",
          ln=True,
          align="center",
      )
      pdf2.ln(5)
      pdf2.set_font("Arial", "B", 9)
      pdf2.cell(10, 7, "N", 1, 0, "C")
      pdf2.cell(50, 7, "Cedente", 1, 0, "L")
      pdf2.cell(15, 7, "", 1, 0, "C")
      pdf2.cell(50, 7, "Ricevente", 1, 0, "L")
      pdf2.cell(65, 7, "Turno Ceduto", 1, 1, "L")
      pdf2.set_font("Arial", "", 9)
      
      if correct_chain:
        for i, cedente in enumerate(correct_chain):
          ricevente = correct_chain[(i + 1) % len(correct_chain)]
          info = details_map.get(
              cedente, {"cod": "-", "turno": "N/D", "assegnato": "-"}
          )
          pdf2.cell(10, 7, str(i + 1), 1, 0, "C")
          pdf2.cell(50, 7, f"{cedente} ({info['cod']})", 1, 0, "L")
          pdf2.cell(15, 7, "->", 1, 0, "C")
          pdf2.cell(50, 7, ricevente, 1, 0, "L")
          pdf2.cell(65, 7, info["turno"], 1, 1, "L")
      pdf2_bytes = bytes(pdf2.output())

      # --- PDF 3: Matrice & Riepilogo Finale ---
      pdf3 = FPDF()
      pdf3.add_page()
      pdf3.set_font("Arial", "B", 12)
      pdf3.cell(
          0,
          10,
          "Matrice & Riepilogo Chiusura Circolare",
          ln=True,
          align="center",
      )
      pdf3.ln(5)
      pdf3.set_font("Arial", "B", 9)
      pdf3.cell(10, 7, "#", 1, 0, "C")
      pdf3.cell(45, 7, "Origine", 1, 0, "L")
      pdf3.cell(55, 7, "Turno Ceduto", 1, 0, "L")
      pdf3.cell(45, 7, "Destinatario", 1, 0, "L")
      pdf3.cell(35, 7, "Stato", 1, 1, "L")
      pdf3.set_font("Arial", "", 9)
      
      if correct_chain:
        for i, cedente in enumerate(correct_chain):
          ricevente = correct_chain[(i + 1) % len(correct_chain)]
          info = details_map.get(
              cedente, {"cod": "-", "turno": "N/D", "assegnato": "-"}
          )
          pdf3.cell(10, 7, str(i + 1), 1, 0, "C")
          pdf3.cell(45, 7, cedente, 1, 0, "L")
          pdf3.cell(55, 7, info["turno"], 1, 0, "L")
          pdf3.cell(45, 7, ricevente, 1, 0, "L")
          pdf3.cell(35, 7, "OK", 1, 1, "L")
      pdf3_bytes = bytes(pdf3.output())

      st.success("✅ I 3 PDF sono stati generati correttamente con i nuovi dati!")

      st.download_button(
          label="📥 Scarica PDF 1: Variazioni Servizio",
          data=pdf1_bytes,
          file_name="PDF1_Variazioni_Servizio.pdf",
          mime="application/pdf",
      )

      st.download_button(
          label="📥 Scarica PDF 2: Catena Consequenziale",
          data=pdf2_bytes,
          file_name="PDF2_Catena_Consequenziale.pdf",
          mime="application/pdf",
      )

      st.download_button(
          label="📥 Scarica PDF 3: Matrice & Riepilogo",
          data=pdf3_bytes,
          file_name="PDF3_Matrice_Riepilogo.pdf",
          mime="application/pdf",
      )
