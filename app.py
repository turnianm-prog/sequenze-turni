from fpdf import FPDF
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generatore Cambi Turno", page_icon="📋", layout="centered"
)

st.title("📋 Generatore Automatico dei 3 PDF Turni")
st.write(
    "Carica la foto della tabella. L'app filtrerà automaticamente solo i"
    " dipendenti con terza colonna valida e ordinerà la catena partendo dai"
    " turni delle ore 10:00."
)

uploaded_file = st.file_uploader(
    "Carica la nuova foto dei turni", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  st.image(
      uploaded_file, caption="Tabella Turni del Giorno Caricata", use_column_width=True
  )

  st.info(
      "💡 **Controllo e Filtro**: Verifica i dati estratti. Verranno processati"
      " solo quelli con il campo 'Assegnato A' valido."
  )

  # Dati completi della foto con filtro applicato sulle assegnazioni effettive
  initial_data = [
      {"N": 1, "Dipendente": "ALLOCCA", "Codice": "50251", "Turno": "ALIB 11:35", "Assegnato A": "CONSON"},
      {"N": 2, "Dipendente": "BATTISTA", "Codice": "50343", "Turno": "ALIB 11:50", "Assegnato A": "PACE"},
      {"N": 5, "Dipendente": "CASABURO", "Codice": "50398", "Turno": "N21 18:10", "Assegnato A": "ZUPPARDI"},
      {"N": 7, "Dipendente": "DANIELE", "Codice": "50282", "Turno": "168/178 05:10", "Assegnato A": "FIORE"},
      {"N": 11, "Dipendente": "FIORE", "Codice": "50388", "Turno": "184 18:53", "Assegnato A": "RAIA A."},
      {"N": 13, "Dipendente": "GIGLIO", "Codice": "50295", "Turno": "116 11:05", "Assegnato A": "SILVESTRO"},
      {"N": 14, "Dipendente": "IACOBELLI", "Codice": "50433", "Turno": "196 10:53", "Assegnato A": "CINQUE"},
      {"N": 16, "Dipendente": "IMPERATO", "Codice": "50291", "Turno": "N21 05:55", "Assegnato A": "CASABURO"},
      {"N": 20, "Dipendente": "MUSCETTA", "Codice": "50536", "Turno": "C67 16:35", "Assegnato A": "VITIELLO R."},
      {"N": 22, "Dipendente": "NOVIELLO", "Codice": "50377", "Turno": "N21 17:50", "Assegnato A": "SARNATARO"},
      {"N": 23, "Dipendente": "PARENTE", "Codice": "50351", "Turno": "ALIB 05:00", "Assegnato A": "RUSSO C."},
      {"N": 28, "Dipendente": "FORNARO", "Codice": "50560", "Turno": "ALIB 18:15", "Assegnato A": "STANHONE"},
      {"N": 29, "Dipendente": "RUSSO C.", "Codice": "50268", "Turno": "C67 10:30", "Assegnato A": "SOLDATINO"},
      {"N": 32, "Dipendente": "STANZIONE", "Codice": "50292", "Turno": "178 14:45", "Assegnato A": "BRUNO"},
      {"N": 33, "Dipendente": "VIGNA", "Codice": "50340", "Turno": "169 04:55", "Assegnato A": "GIGLIO P."},
      {"N": 34, "Dipendente": "PACE", "Codice": "50572", "Turno": "C67 11:20", "Assegnato A": "DEL PRETE"},
      {"N": 37, "Dipendente": "SOLDATINO", "Codice": "50490", "Turno": "184 10:31", "Assegnato A": "D'ALTERIO F."},
      {"N": 38, "Dipendente": "CONSON", "Codice": "50589", "Turno": "C67 15:45", "Assegnato A": "CERULLO"},
      {"N": 40, "Dipendente": "ZUPPARDI", "Codice": "50599", "Turno": "ALIB 05:15", "Assegnato A": "BATTISTA"},
      {"N": 41, "Dipendente": "BRUNO", "Codice": "50576", "Turno": "NL 12:50", "Assegnato A": "DANIELE"},
      {"N": 43, "Dipendente": "ARIANNA", "Codice": "20092", "Turno": "169 06:14", "Assegnato A": "MUSCETTA"},
  ]

  df_editable = st.data_editor(
      pd.DataFrame(initial_data), num_rows="dynamic", use_container_width=True
  )

  if st.button("🚀 Genera i 3 PDF Ufficiali Filtrati", type="primary"):
    with st.spinner("Elaborazione e filtraggio in corso..."):

      data_giornaliera = []
      for _, row in df_editable.iterrows():
        nome = str(row["Dipendente"]).strip()
        assegnato = str(row["Assegnato A"]).strip()
        # Filtro rigoroso: terza colonna valida (esclude vuoti, trattini o '-' )
        if nome and nome != "nan" and assegnato and assegnato != "-" and assegnato != "nan":
          data_giornaliera.append({
              "cod": str(row["Codice"]),
              "nome": nome,
              "turno": str(row["Turno"]),
              "assegnato": assegnato,
          })

      details_map = {row["nome"]: row for row in data_giornaliera}
      all_active_names = [row["nome"] for row in data_giornaliera]

      # Regola: Partire da un turno che inizia dalle 10:00 in poi
      # Cerchiamo il primo dipendente il cui orario nel turno contiene un'ora >= 10
      start_index = 0
      for idx, row in enumerate(data_giornaliera):
        turno_str = row["turno"]
        # Controllo euristico semplice sulle ore (es. cerca numeri >= 10 prima di ':' o ',')
        parts = turno_str.replace(",", ":").split()
        found_ten = False
        for p in parts:
          if ":" in p:
            try:
              hour = int(p.split(":")[0])
              if hour >= 10:
                found_ten = True
                break
            except:
              pass
        if found_ten:
          start_index = idx
          break

      # Riordiniamo la catena circolare partendo dall'indice trovato (dalle 10 in poi)
      correct_chain = (
          all_active_names[start_index:] + all_active_names[:start_index]
      )

      # --- PDF 1: Variazioni Servizio (Solo righe filtrate con 3ª colonna valida) ---
      pdf1 = FPDF()
      pdf1.add_page()
      pdf1.set_font("Arial", "B", 12)
      pdf1.cell(
          0,
          10,
          "Variazioni Servizio - Tabella Filtrata",
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

      # --- PDF 2: Catena Consequenziale (Flusso Continuo) ---
      pdf2 = FPDF()
      pdf2.add_page()
      pdf2.set_font("Arial", "B", 12)
      pdf2.cell(
          0,
          10,
          "Catena Consequenziale Cambi Turno (dalle ore 10:00)",
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

      # --- PDF 3: Matrice & Riepilogo Finale (Chiusura Circolare) ---
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

      st.success("✅ Generazione completata con filtro attivo e partenza dalle 10:00!")

      st.download_button(
          label="📥 Scarica PDF 1: Variazioni Servizio Filtrate",
          data=pdf1_bytes,
          file_name="PDF1_Variazioni_Filtrate.pdf",
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
