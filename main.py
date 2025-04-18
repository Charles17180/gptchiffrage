from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# 🔐 Récupération des clés Supabase depuis le .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialisation du client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Création de l'application FastAPI
app = FastAPI()

# ✅ Modèle de la requête attendue
class ChiffrageRequest(BaseModel):
    description_projet: str

# ✅ Route principale de chiffrage
@app.post("/chiffrage")
def chiffrage(request: ChiffrageRequest):
    description_projet = request.description_projet.lower()

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


# ✅ Démarrage local ET déploiement Render
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
