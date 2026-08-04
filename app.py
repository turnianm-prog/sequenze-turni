from fpdf import FPDF
import google.generativeai as genai
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generatore Cambi Turno - Due Step",
    page_icon="📋",
    layout="centered",
)

st.title("📋 Generatore Turni - Procedura a 2 Step")
st.write(
    "Carica la foto: il sistema eseguirà prima l'estrazione e i primi 2 PDF,"
    " e successivamente la catena a cascata invertita dalle ore 12:00."
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
    if st.button("🚀 Esegui Step 1 e Step 2", type="primary"):
      with st.spinner("Elaborazione in corso..."):
        try:
          genai.configure(api_key=api_key)
          model = genai.GenerativeModel("gemini-1.5-flash")

          # Prompt per estrarre i dati grezzi validi
          prompt = (
              "Analizza questa immagine di una tabella di cambi turno ferroviari."
              " Estrai SOLO le righe in cui la terza colonna (Assegnato A) ha un"
              " valore valido (ignora i riposi 'R', 'NO', i trattini '-' o i"
              " campi vuoti). Restituisci i dati in formato strutturato"
              " separato da punto e virgola in questo esatto formato:"
              " COGNOME;CODICE;TURNO;ASSEGNATO_A."
          )

          response = model.generate_content([prompt, uploaded_file.getvalue()])

          if not response or not response.text:
            st.error("L'IA non ha restituito alcun testo.")
          else:
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
              st.error("Nessun dato valido estratto dalla foto.")
            else:
              # ==========================================
              # STEP 1: Generazione PDF 1 e PDF 2 (Grezzi/Base)
              # ==========================================

              # PDF 1: Tabella completa delle variazioni (ordine foto, filtrata)
              pdf1 = FPDF()
              pdf1.add_page()
              pdf1.set_font("Arial", "B", 12)
              pdf1.cell(
                  0,
                  10,
                  "PDF 1: Tabella Completa Variazioni Servizio",
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

              # PDF 2: Catena consequenziale flusso base
              names_step1 = [row["nome"] for row in data_giornaliera]
              details_map = {row["nome"]: row for row in data_giornaliera}

              pdf2 = FPDF()
              pdf2.add_page()
              pdf2.set_font("Arial", "B", 12)
              pdf2.cell(
                  0,
                  10,
                  "PDF 2: Catena Consequenziale Base",
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
              for i, cedente in enumerate(names_step1):
                ricevente = names_step1[(i + 1) % len(names_step1)]
                info = details_map.get(
                    cedente, {"cod": "-", "turno": "N/D", "assegnato": "-"}
                )
                pdf2.cell(10, 7, str(i + 1), 1, 0, "C")
                pdf2.cell(50, 7, f"{cedente} ({info['cod']})", 1, 0, "L")
                pdf2.cell(15, 7, "->", 1, 0, "C")
                pdf2.cell(50, 7, ricevente, 1, 0, "L")
                pdf2.cell(65, 7, info["turno"], 1, 1, "L")
              pdf2_bytes = bytes(pdf2.output())

              # ==========================================
              # STEP 2: Analisi a cascata invertita & Chiusura Anello
              # ==========================================
              # Regola:
              # - Chi cede = Assegnato A (destinatario originario)
              # - Chi riceve = Dipendente originario
              # - Direzione dal basso verso l'alto
              # - Partenza dal turno attorno/dopo le 12:00
              # - Chiusura cerchio (chi avvia finisce in fondo come ultimo ricevente)

              # Costruiamo la lista mappata con la logica invertita
              scambi_invertiti = []
              for row in data_giornaliera:
                cedente = row["assegnato"]  # Chi cede (ex Assegnato)
                ricevente = row["nome"]  # Chi riceve (ex Dipendente)
                turno = row["turno"]
                scambi_invertiti.append({
                    "cedente": cedente,
                    "ricevente": ricevente,
                    "turno": turno,
                })

              # Invertiamo l'ordine (dal basso verso l'alto)
              scambi_invertiti.reverse()

              # Individuiamo il punto di inizio: il turno dalle ore 12:00 in poi
              start_idx = 0
              for idx, item in enumerate(scambi_invertiti):
                turno_str = item["turno"]
                parts = turno_str.replace(",", ":").split()
                found = False
                for p in parts:
                  if ":" in p:
                    try:
                      h = int(p.split(":")[0])
                      if h >= 12:
                        found = True
                        break
                    except:
                      pass
                if found:
                  start_idx = idx
                  break

              # Riordiniamo la catena partendo da quel punto
              catena_ordinata = (
                  scambi_invertiti[start_idx:] + scambi_invertiti[:start_idx]
              )

              # PDF 3: Tabella Finale Ricorsiva Step 2
              pdf3 = FPDF()
              pdf3.add_page()
              pdf3.set_font("Arial", "B", 12)
              pdf3.cell(
                  0,
                  10,
                  "PDF 3: Sequenza Scambi a Cascata (Step 2)",
                  ln=True,
                  align="center",
              )
              pdf3.ln(5)
              pdf3.set_font("Arial", "B", 9)
              pdf3.cell(10, 7, "#", 1, 0, "C")
              pdf3.cell(50, 7, "Chi cede", 1, 0, "L")
              pdf3.cell(15, 7, "", 1, 0, "C")
              pdf3.cell(50, 7, "Chi riceve", 1, 0, "L")
              pdf3.cell(65, 7, "Turno del Cedente", 1, 1, "L")
              pdf3.set_font("Arial", "", 9)

              for i, step_data in enumerate(catena_ordinata, 1):
                pdf3.cell(10, 7, str(i), 1, 0, "C")
                pdf3.cell(50, 7, step_data["cedente"], 1, 0, "L")
                pdf3.cell(15, 7, "->", 1, 0, "C")
                pdf3.cell(50, 7, step_data["ricevente"], 1, 0, "L")
                pdf3.cell(65, 7, step_data["turno"], 1, 1, "L")

              pdf3_bytes = bytes(pdf3.output())

              st.success(
                  "✅ Procedura completata con successo! I 3 PDF sono pronti."
              )

              st.download_button(
                  label="📥 Scarica PDF 1 (Variazioni Complete)",
                  data=pdf1_bytes,
                  file_name="PDF1_Variazioni_Base.pdf",
                  mime="application/pdf",
              )
              st.download_button(
                  label="📥 Scarica PDF 2 (Catena Base)",
                  data=pdf2_bytes,
                  file_name="PDF2_Catena_Base.pdf",
                  mime="application/pdf",
              )
              st.download_button(
                  label="📥 Scarica PDF 3 (Sequenza a Cascata Step 2)",
                  data=pdf3_bytes,
                  file_name="PDF3_Cascata_Invertita.pdf",
                  mime="application/pdf",
              )

        except Exception as e:
          st.error(f"Errore durante l'elaborazione dei 2 Step: {e}")
