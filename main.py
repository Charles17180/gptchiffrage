from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from openai import OpenAI

load_dotenv()

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(f"✅ SUPABASE_URL : {SUPABASE_URL}")
print(f"✅ SUPABASE_KEY (début) : {SUPABASE_KEY[:20]}...")
print(f"✅ OPENAI_API_KEY (début) : {OPENAI_API_KEY[:20]}...")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


class Projet(BaseModel):
    description_projet: str


@app.post("/chiffrage")
async def chiffrage(projet: Projet):
    try:
        print("🔍 Envoi à OpenAI...")

        messages = [
            {"role": "system", "content": "Tu es un expert en chiffrage de travaux d’aménagement extérieur."},
            {"role": "user", "content": f"Fais-moi 5 propositions de devis pour ce projet : {projet.description_projet}. Format JSON avec désignation, prix_unitaire_ht et unité_metier."}
        ]

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content
        print("✅ Réponse OpenAI reçue")

        return {"devis": ai_reply}

    except Exception as e:
        print(f"❌ Erreur : {e}")
        raise HTTPException(status_code=500, detail=str(e))
