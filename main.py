from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 🔐 Charger les variables d'environnement (.env local ou Render)
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ✅ Connexion à Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🚀 Instance FastAPI
app = FastAPI()

# 📥 Modèle de la requête POST
class ChiffrageRequest(BaseModel):
    description_projet: str

# 🔍 Route de recherche
@app.post("/chiffrage")
def chiffrage(request: ChiffrageRequest):
    description_projet = request.description_projet.lower()
    mots_cles = description_projet.split()

    try:
        # Construction dynamique de la requête avec plusieurs .ilike()
        query = supabase.table("amenagements_exterieurs").select("*")

        for mot in mots_cles:
            query = query.ilike("designation", f"%{mot}%")

        response = query.execute()
        data = response.data

        if not data:
            raise HTTPException(status_code=404, detail="Aucun résultat trouvé pour ce projet")

        return {"devis": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
