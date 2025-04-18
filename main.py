from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from openai import OpenAI

# 🌍 Chargement des variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🛠 Connexions
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

# 🚀 App FastAPI
app = FastAPI()

# 📥 Schéma d'entrée attendu
class ChiffrageRequest(BaseModel):
    description_projet: str

# 🔁 Route POST principale
@app.post("/chiffrage")
def chiffrage(request: ChiffrageRequest):
    description = request.description_projet.lower()

    try:
        # Étape 1 : recherche Supabase
        data = supabase.table("amenagements_exterieurs") \
            .select("*") \
            .ilike("designation", f"%{description}%") \
            .execute() \
            .data

        if data:
            return {"source": "supabase", "devis": data}

        # Étape 2 : fallback GPT si rien trouvé
        prompt = f"""
        Tu es un expert en menuiserie-agencement. 
        Propose une estimation pour : {description}
        Formate ta réponse en JSON structuré avec désignation, prix_unitaire_ht, unite_metier.
        """

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        gpt_response = completion.choices[0].message.content
        return {"source": "gpt", "devis": gpt_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur GPT ou Supabase : {str(e)}")
