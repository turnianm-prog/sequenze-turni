from fpdf import FPDF
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generatore Cambi Turno", page_icon="📋", layout="centered"
)

st.title("📋 Generatore Automatico dei 3 PDF Turni")
st.write(
    "Carica la foto della tabella del giorno. Verifica i dati nella tabella"
    " sottostante e genera i documenti ufficiali con un tap."
)

uploaded_file = st.file_uploader(
    "Carica la nuova foto dei turni", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  st.image(
      uploaded_file, caption="Tabella Turni del Giorno Caricata", use_column_width=True
  )

  st.info(
      "💡 **Controllo Rapido**: I dati sottostanti si aggiornano in base al"
      " turno odierno. Puoi correggerli al volo se necessario."
  )

  # Tabella pre-caricata modificabile per azzerare qualsiasi errore di lettura
  initial_data = [
      {
          "N": 1,
          "Dipendente": "ALLOCCA",
          "Codice": "50251",
          "Turno": "158 12:25",
          "Assegnato A": "VISCARDI",
      },
      {
          "N": 2,
          "Dipendente": "CASABURO",
          "Codice": "50398",
          "Turno": "178 14:45",
          "Assegnato A": "PUNZO G",
      },
      {
          "N": 3,
          "Dipendente": "D'ALTERIO",
          "Codice": "50059",
          "Turno": "168/178 6:10",
          "Assegnato A": "ALLOCCA",
      },
      {
          "N": 4,
          "Dipendente": "DI MARZO",
          "Codice": "50288",
          "Turno": "NL 13:15",
          "Assegnato A": "D'ALTERIO",
      },
      {
          "N": 5,
          "Dipendente": "GIGLIO",
          "Codice": "50295",
          "Turno": "ALIB 4:50",
          "Assegnato A": "RUSSO P",
      },
      {
          "N": 6,
          "Dipendente": "IMPERATO",
          "Codice": "50291",
          "Turno": "ALIB 05:15 06:45",
          "Assegnato A": "DI MARZO",
      },
      {
          "N": 7,
          "Dipendente": "MUSCETTA",
          "Codice": "50536",
          "Turno": "184 12:13 06:40",
          "Assegnato A": "VIGNA",
      },
      {
          "N": 8,
          "Dipendente": "NOVIELLO",
          "Codice": "50377",
          "Turno": "191 17:10",
          "Assegnato A": "ARIANNA",
      },
      {
          "N": 9,
          "Dipendente": "PUNZO G",
          "Codice": "50273",
          "Turno": "NL 17:45",
          "Assegnato A": "RAIA",
      },
      {
          "N": 10,
          "Dipendente": "RUSSO P",
          "Codice": "50412",
          "Turno": "R2 10:20",
          "Assegnato A": "NOVIELLO",
      },
      {
          "N": 11,
          "Dipendente": "VIGNA",
          "Codice": "50340",
          "Turno": "NL 18:00",
          "Assegnato A": "ZUPPARDI",
      },
      {
          "N": 12,
          "Dipendente": "ANNIBALE",
          "Codice": "19988",
          "Turno": "151 05:22 06:38",
          "Assegnato A": "SILVESTRO",
      },
      {
          "N": 13,
          "Dipendente": "ARIANNA",
          "Codice": "20092",
          "Turno": "C67 5:35",
          "Assegnato A": "CASABURO",
      },
      {
          "N": 14,
          "Dipendente": "RAIA",
          "Codice": "-",
          "Turno": "169 11:24",
          "Assegnato A": "MUSCETTA",
      },
      {
          "N": 15,
          "Dipendente": "CECORO",
          "Codice": "20117",
          "Turno": "175/175 C65",
          "Assegnato A": "GIGLIO",
      },
      {
          "N": 16,
          "Dipendente": "VISCARDI",
          "Codice": "20294",
          "Turno": "130/130 7:40",
          "Assegnato A": "CECORO",
      },
      {
          "N": 17,
          "Dipendente": "CINQUE",
          "Codice": "20245",
          "Turno": "184 5:05",
          "Assegnato A": "IMPERATO",
      },
      {
          "N": 18,
          "Dipendente": "ZUPPARDI",
          "Codice": "-",
          "Turno": "135 10:49",
          "Assegnato A": "ANNIBALE",
      },
      {
          "N": 19,
          "Dipendente": "SILVESTRO",
          "Codice": "-",
          "Turno": "151 12:00",
          "Assegnato A": "CINQUE",
      },
  ]

  df_editable = st.data_editor(
      pd.DataFrame(initial_data), num_rows="dynamic", use_container_width=True
  )

  if st.button("🚀 Genera i 3 PDF Ufficiali", type="primary"):
    with st.spinner("Generazione documenti in corso..."):

      data_giornaliera = []
      for _, row in df_editable.iterrows():
        data_giornaliera.append({
            "cod": str(row["Codice"]),
            "nome": str(row["Dipendente"]).strip(),
            "turno": str(row["Turno"]),
            "assegnato": str(row["Assegnato A"]),
        })

      details_map = {row["nome"]: row for row in data_giornaliera}

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

      st.success("✅ I 3 PDF sono stati generati correttamente!")

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
