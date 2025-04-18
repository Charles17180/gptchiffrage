from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from openai import OpenAI
import os

# 🔐 Chargement des variables d'environnement
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

class ChiffrageRequest(BaseModel):
    description_projet: str

def nettoyer_requete(description: str) -> str:
    """
    Utilise GPT pour simplifier / nettoyer la demande du client.
    """
    prompt = f"""Tu es un assistant pour une entreprise de menuiserie. 
    Simplifie cette description client pour qu’elle corresponde à une désignation technique, sans les tailles ni quantités.
    Exemple : "terrasse bois exotique de 50m²" -> "terrasse bois exotique"
    Voici la description : {description}
    Réponds uniquement avec la désignation simplifiée, sans autre texte.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en chiffrage."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        cleaned = response.choices[0].message.content.strip()
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur GPT: {str(e)}")

@app.post("/chiffrage")
def chiffrage(request: ChiffrageRequest):
    description_client = request.description_projet.lower()

    try:
        # Étape 1 : Nettoyage intelligent
        terme_recherche = nettoyer_requete(description_client)

        # Étape 2 : Recherche Supabase avec terme nettoyé
        response = supabase.table("amenagements_exterieurs") \
            .select("*") \
            .ilike("designation", f"%{terme_recherche}%") \
            .execute()

        data = response.data
        if not data:
            raise HTTPException(status_code=404, detail="Aucun résultat trouvé pour ce projet")

        return {
            "recherche_nettoyee": terme_recherche,
            "resultats": data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
