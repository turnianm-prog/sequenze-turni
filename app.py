from fpdf import FPDF
import google.generativeai as genai
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generatore Automatico Cambi Turno", page_icon="📋", layout="centered"
)

st.title("📋 Generatore Automatico dei 3 PDF Turni")
st.write(
    "Carica la foto della tabella: l'IA leggerà i dati, filtrerà i cambi"
    " validi e ordinerà la catena dalle ore 12:00."
)

api_key = st.secrets.get("GEMINI_API_KEY", "")

uploaded_file = st.file_uploader(
    "Carica la foto dei turni del giorno", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  st.image(
      uploaded_file, caption="Tabella Turni del Giorno Caricata", use_column_width=True
  )

  if not api_key:
    st.error(
        "⚠️ Manca la GEMINI_API_KEY nei Secrets di Streamlit. Configurala"
        " nelle impostazioni dell'app."
    )
  else:
    if st.button("🚀 Elabora Foto e Genera i 3 PDF", type="primary"):
      with st.spinner(
          "Lettura intelligente della foto e generazione documenti in"
          " corso..."
      ):
        try:
          genai.configure(api_key=api_key)
          model = genai.GenerativeModel("gemini-1.5-flash")

          # Prompt corretto e blindato per evitare errori di formattazione
          prompt = (
              "Sei un assistente esperto nell'analisi di tabelle ferroviarie."
              " Analizza questa immagine ed estrai SOLO le righe della tabella"
              " principale che hanno un cambio assegnato valido nella colonna"
              " di destra (scritta a mano). Ignora rigorosamente i riposi 'R',"
              " 'NO', i trattini '-' o i campi vuoti. Per ogni riga valida,"
              " restituisci i dati in un'unica riga di testo nel formato esatto:"
              " COGNOME;CODICE;TURNO;ASSEGNATO_A. "
              "Non aggiungere elenchi puntati, markdown o testo descrittivo"
              " aggiuntivo: solo le righe separate da punto e virgola."
          )

          response = model.generate_content([prompt, uploaded_file.getvalue()])
          lines = response.text.strip().split("\n")

          data_giornaliera = []
          for line in lines:
            line = line.replace("*", "").strip()
            if not line or ";" not in line:
              continue
            parts = line.split(";")
            if len(parts) >= 4:
              data_giornaliera.append({
                  "nome": parts[0].strip(),
                  "cod": parts[1].strip(),
                  "turno": parts[2].strip(),
                  "assegnato": parts[3].strip(),
              })

          if not data_giornaliera:
            st.error(
                "Non è stato possibile estrarre dati validi. Assicurati che la"
                " foto sia ben illuminata e leggibile."
            )
          else:
            details_map = {row["nome"]: row for row in data_giornaliera}
            all_active_names = [row["nome"] for row in data_giornaliera]

            # Ordinamento automatico a partire dai turni delle ore 12:00 in poi
            start_index = 0
            for idx, row in enumerate(data_giornaliera):
              turno_str = row["turno"]
              parts = turno_str.replace(",", ":").split()
              found_twelve = False
              for p in parts:
                if ":" in p:
                  try:
                    hour = int(p.split(":")[0])
                    if hour >= 12:
                      found_twelve = True
                      break
                  except:
                    pass
              if found_twelve:
                start_index = idx
                break

            correct_chain = (
                all_active_names[start_index:] + all_active_names[:start_index]
            )

            # --- PDF 1: Variazioni Servizio ---
            pdf1 = FPDF()
            pdf1.add_page()
            pdf1.set_font("Arial", "B", 12)
            pdf1.cell(
                0,
                10,
                "Variazioni Servizio - Tabella Estratta via IA",
                ln=True,
                align="center",
            )
            pdf1.ln(5)
            pdf1.set_font("Arial", "B", 9)
            pdf1.cell(10, 7, "N", 1, 0, "C")
            pdf1.cell(60, 7, "Dipendente", 1, 0, "L")
            pdf1.cell(60, 7, "Turno", 1, 0, "L")
            pdf1.cell(60, 7, "Assegnato A", 1, 1, "L")
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
                "Catena Consequenziale (dalle ore 12:00)",
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

            # --- PDF 3: Matrice & Riepilogo ---
            pdf3 = FPDF()
            pdf3.add_page()
            pdf3.set_font("Arial", "B", 12)
            pdf3.cell(
                0,
                10,
                "Matrice & Riepilogo Chiusura Circolare (dalle ore 12:00)",
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

            st.success("✅ PDF generati con successo dalle ore 12:00!")

            st.download_button(
                label="📥 Scarica PDF 1: Variazioni Servizio",
                data=pdf1_bytes,
                file_name="PDF1_Variazioni.pdf",
                mime="application/pdf",
            )
            st.download_button(
                label="📥 Scarica PDF 2: Catena Consequenziale",
                data=pdf2_bytes,
                file_name="PDF2_Catena.pdf",
                mime="application/pdf",
            )
            st.download_button(
                label="📥 Scarica PDF 3: Matrice & Riepilogo",
                data=pdf3_bytes,
                file_name="PDF3_Matrice.pdf",
                mime="application/pdf",
            )

        except Exception as e:
          st.error(f"Errore durante l'elaborazione: {e}")
