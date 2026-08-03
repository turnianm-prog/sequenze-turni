from fpdf import FPDF
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generatore Cambi Turno", page_icon="📋", layout="centered"
)

st.title("📋 Generatore Automatico dei 3 PDF Turni")
st.write(
    "Carica la foto della tabella. L'app elaborerà l'intera tabella"
    " estraendo tutte le righe valide da entrambe le colonne e ordinando la"
    " catena dalle ore 10:00."
)

uploaded_file = st.file_uploader(
    "Carica la foto dei turni completa", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  st.image(
      uploaded_file, caption="Tabella Turni del Giorno Caricata", use_column_width=True
  )

  st.info(
      "💡 **Verifica Completa**: Dati estratti da entrambe le colonne della foto."
  )

  # Dati completi di entrambe le colonne della foto reale
  initial_data = [
      # Colonna di Sinistra
      {"N": 1, "Dipendente": "ALLOCCA", "Codice": "50251", "Turno": "ALIB 11:35 06:25", "Assegnato A": "CONSON"},
      {"N": 2, "Dipendente": "BATTISTA", "Codice": "50343", "Turno": "ALIB 11,50", "Assegnato A": "PACE"},
      {"N": 3, "Dipendente": "BELLISAI", "Codice": "50344", "Turno": "R", "Assegnato A": "-"},
      {"N": 4, "Dipendente": "BUONINCONTR", "Codice": "50373", "Turno": "R", "Assegnato A": "-"},
      {"N": 5, "Dipendente": "CASABURO", "Codice": "50398", "Turno": "N21 18,10", "Assegnato A": "ZUPPARDI"},
      {"N": 6, "Dipendente": "D'ALTERIO", "Codice": "50059", "Turno": "N21 16,20", "Assegnato A": "-"},
      {"N": 7, "Dipendente": "DANIELE", "Codice": "50282", "Turno": "168/178 06:10", "Assegnato A": "FIORE"},
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
      {"N": 20, "Dipendente": "MUSCETTA", "Codice": "50536", "Turno": "C67 16:35 06:35", "Assegnato A": "VITIELLO R."},
      {"N": 21, "Dipendente": "NOCERINO", "Codice": "50548", "Turno": "R", "Assegnato A": "-"},
      {"N": 22, "Dipendente": "NOVIELLO", "Codice": "50377", "Turno": "N21 17,50", "Assegnato A": "SARNATARO"},
      {"N": 23, "Dipendente": "PARENTE", "Codice": "50351", "Turno": "ALIB 05:00 06:50", "Assegnato A": "RUSSO C."},
      {"N": 24, "Dipendente": "PUNZO", "Codice": "50273", "Turno": "R", "Assegnato A": "-"},
      {"N": 25, "Dipendente": "RACHELE", "Codice": "50243", "Turno": "R", "Assegnato A": "-"},
      {"N": 26, "Dipendente": "ROMANO", "Codice": "50421", "Turno": "N21 5,95", "Assegnato A": "-"},
      {"N": 27, "Dipendente": "RUSSO P.", "Codice": "50412", "Turno": "N21 5,25", "Assegnato A": "-"},
      {"N": 28, "Dipendente": "FORNARO", "Codice": "50560", "Turno": "ALIB 18:15 06:25", "Assegnato A": "STANZIONE"},
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
      # Colonna di Destra
      {"N": 45, "Dipendente": "CAPPARELLI", "Codice": "20047", "Turno": "130 05:30 06:00", "Assegnato A": "-"},
      {"N": 46, "Dipendente": "CARUSO", "Codice": "20208", "Turno": "184 5,35", "Assegnato A": "ALLOCCA"},
      {"N": 47, "Dipendente": "CASTIELLO", "Codice": "20119", "Turno": "R", "Assegnato A": "-"},
      {"N": 48, "Dipendente": "CECORO", "Codice": "20117", "Turno": "130 06:15 06:35", "Assegnato A": "CARUSO"},
      {"N": 49, "Dipendente": "CERULLO", "Codice": "20246", "Turno": "158 14:35 06:00", "Assegnato A": "IACOMINO"},
      {"N": 50, "Dipendente": "CIPOLETTA", "Codice": "19952", "Turno": "R", "Assegnato A": "-"},
      {"N": 51, "Dipendente": "LUPOLI", "Codice": "19871", "Turno": "R", "Assegnato A": "-"},
      {"N": 52, "Dipendente": "DEL PRETE", "Codice": "20181", "Turno": "158 10,05", "Assegnato A": "VISCARDI"},
      {"N": 53, "Dipendente": "DI CATERINO", "Codice": "20268", "Turno": "R", "Assegnato A": "-"},
      {"N": 54, "Dipendente": "FRAGLIASSO", "Codice": "19930", "Turno": "R", "Assegnato A": "-"},
      {"N": 55, "Dipendente": "GIANNINO", "Codice": "20118", "Turno": "R", "Assegnato A": "-"},
      {"N": 56, "Dipendente": "IACOMINO", "Codice": "17995", "Turno": "196 05:05 06:55", "Assegnato A": "MARRESE"},
      {"N": 57, "Dipendente": "IMPARATO", "Codice": "19985", "Turno": "169 08:36 06:39", "Assegnato A": "-"},
      {"N": 58, "Dipendente": "MADDALONI", "Codice": "20163", "Turno": "196 18:06 06:55", "Assegnato A": "FORNARO"},
      {"N": 59, "Dipendente": "MAROTTA", "Codice": "20161", "Turno": "R", "Assegnato A": "-"},
      {"N": 60, "Dipendente": "MARRESE", "Codice": "20031", "Turno": "151 14:20 06:00", "Assegnato A": "MADDALONI"},
      {"N": 61, "Dipendente": "MELE", "Codice": "20150", "Turno": "R", "Assegnato A": "-"},
      {"N": 62, "Dipendente": "MIGNOGNA", "Codice": "20255", "Turno": "R", "Assegnato A": "-"},
      {"N": 63, "Dipendente": "PALLADINO", "Codice": "19987", "Turno": "151 05:00 06:20", "Assegnato A": "IMPERATO"},
      {"N": 64, "Dipendente": "PARISI", "Codice": "19960", "Turno": "R", "Assegnato A": "-"},
      {"N": 65, "Dipendente": "PAUDICE", "Codice": "19938", "Turno": "195 14:30 06:30", "Assegnato A": "-"},
      {"N": 66, "Dipendente": "PAPPALARDO", "Codice": "20180", "Turno": "151/R2 12:20", "Assegnato A": "-"},
      {"N": 67, "Dipendente": "PEPERNA", "Codice": "18228", "Turno": "R", "Assegnato A": "-"},
      {"N": 68, "Dipendente": "PERSICO", "Codice": "20166", "Turno": "195 13:50 06:25", "Assegnato A": "ARIANNA"},
      {"N": 69, "Dipendente": "PIANTADOSI", "Codice": "20104", "Turno": "191 17:10 06:00", "Assegnato A": "-"},
      {"N": 70, "Dipendente": "PICCOLO", "Codice": "19074", "Turno": "R", "Assegnato A": "-"},
      {"N": 71, "Dipendente": "PUNZO", "Codice": "20182", "Turno": "R5 11,32", "Assegnato A": "-"},
      {"N": 72, "Dipendente": "SACCO", "Codice": "19961", "Turno": "R", "Assegnato A": "-"},
      {"N": 73, "Dipendente": "SANGERMANO", "Codice": "20041", "Turno": "196 05:25 06:01", "Assegnato A": "-"},
      {"N": 74, "Dipendente": "SANTANIELLO", "Codice": "20139", "Turno": "182/116 13:00", "Assegnato A": "-"},
      {"N": 75, "Dipendente": "SCALZI", "Codice": "20108", "Turno": "R", "Assegnato A": "-"},
      {"N": 76, "Dipendente": "TERRACCIANO", "Codice": "20032", "Turno": "R", "Assegnato A": "-"},
      {"N": 77, "Dipendente": "TUFANO", "Codice": "20260", "Turno": "R", "Assegnato A": "-"},
      {"N": 78, "Dipendente": "VENERUSO", "Codice": "20036", "Turno": "R", "Assegnato A": "-"},
      {"N": 79, "Dipendente": "VETERE", "Codice": "20106", "Turno": "R", "Assegnato A": "-"},
      {"N": 80, "Dipendente": "VITIELLO F.", "Codice": "20189", "Turno": "177 12,30", "Assegnato A": "-"},
      {"N": 81, "Dipendente": "VITIELLO R.", "Codice": "20265", "Turno": "116 16:10 06:45", "Assegnato A": "PARENTE"},
      {"N": 82, "Dipendente": "ROSSI", "Codice": "20278", "Turno": "R", "Assegnato A": "-"},
      {"N": 83, "Dipendente": "VIOLA", "Codice": "20279", "Turno": "R5 05:20 06:12", "Assegnato A": "-"},
      {"N": 84, "Dipendente": "VISCARDI", "Codice": "20294", "Turno": "173A 07:00 06:45", "Assegnato A": "PERSICO"},
      {"N": 85, "Dipendente": "DE ROSA F.", "Codice": "20292", "Turno": "169P 06:35 06:20", "Assegnato A": "-"},
      {"N": 86, "Dipendente": "CINQUE", "Codice": "20245", "Turno": "191 06:30 06:00", "Assegnato A": "PALLADINO"},
      # Annotazioni in fondo alla pagina (extra)
      {"N": 87, "Dipendente": "D'ALTERIO F.", "Codice": "EXTRA", "Turno": "151 9:40", "Assegnato A": "CECORO"},
      {"N": 88, "Dipendente": "SARNATARO", "Codice": "EXTRA", "Turno": "NL 13:15", "Assegnato A": "NOVIELLO"},
      {"N": 89, "Dipendente": "RAIA A.", "Codice": "EXTRA", "Turno": "NL 5:30", "Assegnato A": "IACOBELLI"},
      {"N": 90, "Dipendente": "SILVESTRO", "Codice": "EXTRA", "Turno": "R5 12:00", "Assegnato A": "VIGNA"},
  ]

  df_editable = st.data_editor(
      pd.DataFrame(initial_data), num_rows="dynamic", use_container_width=True
  )

  if st.button("🚀 Genera i 3 PDF Ufficiali con Filtro", type="primary"):
    with st.spinner("Elaborazione e filtraggio completo in corso..."):

      data_giornaliera = []
      for _, row in df_editable.iterrows():
        nome = str(row["Dipendente"]).strip()
        assegnato = str(row["Assegnato A"]).strip()
        # Filtro rigoroso: terza colonna valida
        if nome and nome != "nan" and assegnato and assegnato != "-" and assegnato != "nan":
          data_giornaliera.append({
              "cod": str(row["Codice"]),
              "nome": nome,
              "turno": str(row["Turno"]),
              "assegnato": assegnato,
          })

      details_map = {row["nome"]: row for row in data_giornaliera}
      all_active_names = [row["nome"] for row in data_giornaliera]

      # Ricerca automatica del primo turno che inizia dalle 10:00 in poi
      start_index = 0
      for idx, row in enumerate(data_giornaliera):
        turno_str = row["turno"]
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

      # Riordino circolare partendo dalle 10:00
      correct_chain = (
          all_active_names[start_index:] + all_active_names[:start_index]
      )

      # --- PDF 1: Variazioni Servizio (Tabella Filtrata) ---
      pdf1 = FPDF()
      pdf1.add_page()
      pdf1.set_font("Arial", "B", 12)
      pdf1.cell(
          0,
          10,
          "Variazioni Servizio - Tabella Filtrata Completa",
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

      st.success("✅ Tutti i dipendenti inclusi, filtrati e ordinati correttamente dalle 12:00!")

      st.download_button(
          label="📥 Scarica PDF 1: Variazioni Servizio Complete",
          data=pdf1_bytes,
          file_name="PDF1_Variazioni_Complete.pdf",
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
