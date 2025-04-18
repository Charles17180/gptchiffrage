from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement (depuis .env)
load_dotenv()

# 🔐 Clés API à récupérer depuis ton .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Connexion Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Création de l'app FastAPI
app = FastAPI()

# ✅ Modèle de requête attendue
class ChiffrageRequest(BaseModel):
    description_projet: str

# ✅ Route principale
@app.post("/chiffrage")
def chiffrage(request: ChiffrageRequest):
    description_projet = request.description_projet.lower()

    # 🔍 Recherche simple dans la table Supabase
    try:
        response = supabase.table("amenagements_exterieurs") \
            .select("*") \
            .ilike("designation", f"%{description_projet}%") \
            .execute()

        data = response.data

        if not data:
            raise HTTPException(status_code=404, detail="Aucun résultat trouvé pour ce projet")

        return {"devis": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
