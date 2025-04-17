from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os

# Récupération des credentials Supabase depuis les variables d’environnement
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Vérification minimale
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ Variables d’environnement SUPABASE_URL ou SUPABASE_KEY manquantes.")

# === DEBUG TEMPORAIRE ===
print("✅ SUPABASE_URL :", SUPABASE_URL)
print("✅ SUPABASE_KEY (début) :", SUPABASE_KEY[:6], "...")
# =========================

# Initialisation Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialisation FastAPI
app = FastAPI()

# Modèle pour la requête
class Demande(BaseModel):
    description_projet: str

# Endpoint POST /chiffrage
@app.post("/chiffrage")
def chiffrage(demande: Demande):
    description = demande.description_projet.lower()

    # Requête vers Supabase
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
