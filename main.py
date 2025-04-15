from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = "https://rcldqrzhcknyukbshxbr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # clé OK déjà utilisée

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# API
app = FastAPI()

class Demande(BaseModel):
    description_projet: str

@app.post("/chiffrage")
def chiffrage(demande: Demande):
    description = demande.description_projet.lower()

    # Récupération des données
    response = supabase.table("amenagements_exterieurs").select("*").execute()
    lignes = response.data

    # Filtrage intelligent
    resultats = []
    for ligne in lignes:
        if ligne["designation"] and any(mot in ligne["designation"].lower() for mot in description.split()):
            resultats.append({
                "designation": ligne["designation"],
                "prix_unitaire_ht": ligne["prix_unitaire_ht"],
                "unite_metier": ligne["unite_metier"]
            })

    if not resultats:
        return {"devis": "Aucun poste trouvé dans la base pour cette description."}

    return {"devis": resultats}
