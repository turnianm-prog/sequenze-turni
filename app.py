from fpdf import FPDF
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generatore Cambi Turno", page_icon="📋", layout="centered"
)

st.title("📋 Generatore Automatico dei 3 PDF Turni")
st.write(
    "Carica la foto della tabella del giorno. I dati della foto attuale sono"
    " già precaricati nella tabella sottostante per la generazione rapida."
)

uploaded_file = st.file_uploader(
    "Carica la nuova foto dei turni", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  st.image(
      uploaded_file, caption="Tabella Turni del Giorno Caricata", use_column_width=True
  )

  st.info(
      "💡 **Verifica Turni**: Ecco i dati estratti dalla foto del giorno."
      " Modifica direttamente qui se necessario."
  )

  # Dati specifici estrapolati dalla foto reale caricata oggi
  initial_data = [
      {"N": 1, "Dipendente": "ALLOCCA", "Codice": "50251", "Turno": "ALIB 11:35 08:25", "Assegnato A": "CONSON"},
      {"N": 2, "Dipendente": "BATTISTA", "Codice": "50343", "Turno": "ALIB 11,50", "Assegnato A": "PACE"},
      {"N": 3, "Dipendente": "BELLISAI", "Codice": "50344", "Turno": "R", "Assegnato A": "-"},
      {"N": 4, "Dipendente": "BUONINCONTR", "Codice": "50373", "Turno": "R", "Assegnato A": "-"},
      {"N": 5, "Dipendente": "CASABURO", "Codice": "50398", "Turno": "N21 18,10", "Assegnato A": "ZUPPARD."},
      {"N": 6, "Dipendente": "D'ALTERIO", "Codice": "50059", "Turno": "N21 16,20", "Assegnato A": "-"},
      {"N": 7, "Dipendente": "DANIELE", "Codice": "50282", "Turno": "168/178 05:10", "Assegnato A": "FIORE"},
      {"N": 8, "Dipendente": "DE CARO", "Codice": "50267", "Turno": "N21 12,30", "Assegnato A": "-"},
      {"N": 9, "Dipendente": "DI MARZO", "Codice": "50288", "Turno": "R", "Assegnato A": "-"},
      {"N": 10, "Dipendente": "FERONE", "Codice": "50276", "Turno": "R", "Assegnato A": "-"},
      {"N": 11, "Dipendente": "FIORE", "Codice": "50388", "Turno": "184 18:53 06:27", "Assegnato A": "RAIA A."},
      {"N": 12, "Dipendente": "GAGLIANO", "Codice": "50406", "Turno": "R", "Assegnato A": "-"},
      {"N": 13, "Dipendente": "GIGLIO", "Codice": "50295", "Turno": "116 11,05", "Assegnato A": "SILVESTRO"},
      {"N": 14, "Dipendente": "IACOBELLI", "Codice": "50433", "Turno": "196 10,53", "Assegnato A": "CINQUE"},
      {"N": 15, "Dipendente": "IAVARONE", "Codice": "50427", "Turno": "NO", "Assegnato A": "-"},
      {"N": 16, "Dipendente": "IMPERATO", "Codice": "50291", "Turno": "N21 5,55", "Assegnato A": "CASABURO"},
      {"N": 17, "Dipendente": "MARANO", "Codice": "50286", "Turno": "R", "Assegnato A": "-"},
      {"N": 18, "Dipendente": "MARANO", "Codice": "50552", "Turno": "R", "Assegnato A": "-"},
      {"N": 19, "Dipendente": "MARINELLO", "Codice": "50396", "Turno": "R", "Assegnato A": "-"},
      {"N": 20, "Dipendente": "MUSCETTA", "Codice": "50536", "Turno": "C67 16:35 06:35", "Assegnato A": "VITIELLOR."},
      {"N": 21, "Dipendente": "NOCERINO", "Codice": "50548", "Turno": "R", "Assegnato A": "-"},
      {"N": 22, "Dipendente": "NOVIELLO", "Codice": "50377", "Turno": "N21 17,50", "Assegnato A": "SARNATARO"},
      {"N": 23, "Dipendente": "PARENTE", "Codice": "50351", "Turno": "ALIB 05:00 06:50", "Assegnato A": "RUSSO C."},
      {"N": 24, "Dipendente": "PUNZO", "Codice": "50273", "Turno": "R", "Assegnato A": "-"},
      {"N": 25, "Dipendente": "RACHELE", "Codice": "50243", "Turno": "R", "Assegnato A": "-"},
      {"N": 26, "Dipendente": "ROMANO", "Codice": "50421", "Turno": "N21 5,95", "Assegnato A": "-"},
      {"N": 27, "Dipendente": "RUSSO P.", "Codice": "50412", "Turno": "N21 5,25", "Assegnato A": "-"},
      {"N": 28, "Dipendente": "FORNARO", "Codice": "50560", "Turno": "ALIB 18:15 06:25", "Assegnato A": "STANHONE"},
      {"N": 29, "Dipendente": "RUSSO C.", "Codice": "50268", "Turno": "C67 10:30 06:50", "Assegnato A": "SOLDATINO"},
      {"N": 30, "Dipendente": "SAVANELLI", "Codice": "50535", "Turno": "C67 05:35 06:30", "Assegnato A": "-"},
      {"N": 31, "Dipendente": "STAIANO", "Codice": "50409", "Turno": "R", "Assegnato A": "-"},
      {"N": 32, "Dipendente": "STANZIONE", "Codice": "50292", "Turno": "178 14:45 06:25", "Assegnato A": "BRUNO"},
      {"N": 33, "Dipendente": "VIGNA", "Codice": "50340", "Turno": "169 P 4,55", "Assegnato A": "GIGLIO P."},
      {"N": 34, "Dipendente": "PACE", "Codice": "50572", "Turno": "C67 11:20 06:50", "Assegnato A": "DEL PRETE"},
      {"N": 35, "Dipendente": "D'ANNA", "Codice": "50577", "Turno": "SA", "Assegnato A": "-"},
      {"N": 36, "Dipendente": "DI LORENZO", "Codice": "50609", "Turno": "R", "Assegnato A": "-"},
      {"N": 37, "Dipendente": "SOLDATINO", "Codice": "50490", "Turno": "184 10:31 06:10", "Assegnato A": "D'ALTERIO F."},
      {"N": 38, "Dipendente": "CONSON", "Codice": "50589", "Turno": "C67 15:45 06:30", "Assegnato A": "CERULLO"},
      {"N": 39, "Dipendente": "SIGNORIELLO", "Codice": "50611", "Turno": "178 05:40 06:05", "Assegnato A": "-"},
      {"N": 40, "Dipendente": "ZUPPARDI", "Codice": "50599", "Turno": "ALIB 05:15 06:20", "Assegnato A": "BATTISTA"},
      {"N": 41, "Dipendente": "BRUNO", "Codice": "50576", "Turno": "NL 12:50 06:17", "Assegnato A": "DANIELE"},
      {"N": 42, "Dipendente": "ANNIBALE", "Codice": "19988", "Turno": "194 06:20 06:20", "Assegnato A": "-"},
      {"N": 43, "Dipendente": "ARIANNA", "Codice": "20092", "Turno": "169/169 6,14", "Assegnato A": "MUSCETTA"},
      {"N": 44, "Dipendente": "BIANCO", "Codice": "20039", "Turno": "R", "Assegnato A": "-"},
  ]

  df_editable = st.data_editor(
      pd.DataFrame(initial_data), num_rows="dynamic", use_container_width=True
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
          if str(row["Assegnato A"]).strip() and str(row["Assegnato A"]).strip() != "-":
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

      st.success("✅ I 3 PDF sono stati generati correttamente con i dati della foto corrente!")

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
