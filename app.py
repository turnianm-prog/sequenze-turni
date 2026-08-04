import base64
import json
from openai import OpenAI

# Inserisci la tua API Key (o salvala nei Secrets di Streamlit)
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", "LA_TUA_API_KEY"))

def estrai_dati_da_foto_ai(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    prompt = """
    Analizza questa foto di una tabella di variazioni turni.
    La foto contiene due colonne principali di tabelle affiancate.
    Estrai SOLO le righe in cui è presente una variazione o un nome compilato a mano nella colonna 'Assegnato'.
    
    Restituisci unicamente un array JSON di oggetti con questa struttura esatta:
    [
      {"Dipendente": "COGNOME", "Turno": "TURNO_SCRITTO", "Assegnato": "DESTINATARIO_A_MANO"},
      ...
    ]
    Assicurati di pulire i dati (rimuovi il codice numerico matricola dal Cognome se presente).
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    data = json.loads(content)
    # Cerca la lista nel JSON
    for key, val in data.items():
        if isinstance(val, list):
            return pd.DataFrame(val)
    return pd.DataFrame(data)
