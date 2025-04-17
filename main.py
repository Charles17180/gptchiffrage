from fastapi import FastAPI, Request
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # ⚠️ service_role uniquement

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

class ChiffrageRequest(BaseModel):
    description_projet: str

# fallback local
def simulate_devis(description: str):
    fallback_data = [
        {"designation": "Clôture en grillage rigide - PVC", "prix_unitaire_ht": 85.0, "unite_metier": "ml"},
        {"designation": "Clôture en grillage rigide - acier galvanisé", "prix_unitaire_ht": 95.0, "unite_metier": "ml"},
    ]
    return fallback_data

@app.post("/chiffrage")
def get_devis(request_data: ChiffrageRequest):
    try:
        query = request_data.description_projet
        print(f"🔍 Requête Supabase pour: {query}")

        response = supabase.table("amenagements_exterieurs")\
            .select("*")\
            .ilike("description_projet", f"%{query}%")\
            .execute()

        devis = response.data

        if not devis:
            print("⚠️ Aucun résultat Supabase - fallback activé")
            devis = simulate_devis(query)

        return { "devis": devis }

    except Exception as e:
        return { "error": str(e) }
