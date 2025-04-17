from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
import openai
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(f"✅ SUPABASE_URL : {SUPABASE_URL}")
print(f"✅ SUPABASE_KEY (début) : {SUPABASE_KEY[:20]}...")
print(f"✅ OPENAI_API_KEY (début) : {OPENAI_API_KEY[:20]}...")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai.api_key = OPENAI_API_KEY

app = FastAPI()

class Projet(BaseModel):
    description_projet: str

@app.post("/chiffrage")
def generer_devis(projet: Projet):
    try:
        prompt = f"""
Tu es un assistant expert en devis pour un atelier de menuiserie-agencement.
Génère une liste de 5 lignes de devis correspondant à la demande suivante :
\"{projet.description_projet}\".

Chaque ligne de devis doit contenir :
- une désignation précise du produit ou service
- un prix unitaire HT réaliste
- une unité métier cohérente (ex : m², ml, unité, heure, etc.)

Retourne uniquement un JSON de ce type :
[
  {{
    "designation": "...",
    "prix_unitaire_ht": 123.45,
    "unite_metier": "..."
  }},
  ...
]
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        )

        message = response.choices[0].message["content"]
        devis = eval(message)  # À sécuriser si besoin
        return {"devis": devis}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
