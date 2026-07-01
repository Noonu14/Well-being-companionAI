import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Well-being Companion AI")

# Enable CORS so your frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verify API key exists before starting
api_key_val = os.getenv("GEMINI_API_KEY")
if not api_key_val:
    raise ValueError("CRITICAL: GEMINI_API_KEY is missing from your .env file!")

# Initialize Google GenAI Client with the verified key string
client = genai.Client()

# Define request structure
class ChatRequest(BaseModel):
    message: str

# 1. HARDCODED SAFETY PROTOCOL
CRISIS_KEYWORDS = [r"suicide", r"kill myself", r"self-harm", r"end my life", r"cut myself",r"going through depression",r"in depression",r"want to die",r"want to end my life",r"want to kill myself",r"want to commit self-harm",r"want to commit a crime",r"want to murder",r"want to hurt"]

def contains_crisis_keywords(text: str) -> bool:
    for pattern in CRISIS_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

CRISIS_RESPONSE = (
    "I hear that you're going through a deeply difficult time, but I am an AI, not a licensed professional. "
    "Please know that you are not alone and there is support available. Please reach out to a professional "
    "or a helpline immediately. If you are in India, you can call AASRA at +91-9820466726 or the Vandrevala "
    "Foundation at +91-9999666555. If you are elsewhere, please contact your local emergency services."
)

# 2. SYSTEM INSTRUCTIONS (The Persona Guardrail)
SYSTEM_INSTRUCTION = (
    "You are a deeply compassionate, warm, and active-listening Well-being Companion. "
    "Your goal is to provide a safe space for users to reflect on their day, practice mindfulness, "
    "and gently reframe negative thoughts using supportive Cognitive Behavioral Therapy (CBT) principles.\n\n"
    "RESPONSE STRUCTURE STRATEGY:\n"
    "1. VALIDATE & EMPOWER: Start by warmly acknowledging their pain or feelings without judgment. Use kind, human phrases "
    "(e.g., 'I'm so sorry you're carrying such a heavy weight today,' or 'That sounds incredibly exhausting, and it makes complete sense that you feel this way').\n"
    "2. GENTLE PERSPECTIVE: Offer a small, grounding, or normalizing reflection. Remind them gently that thoughts aren't absolute facts.\n"
    "3. PRACTICAL ACTION: End with a single, highly manageable, tiny step or a gentle, open-ended question to help them process (e.g., 'If you feel up to it, what is one tiny thing we can do right now to bring you a pocket of comfort?').\n\n"
    "STRICT BOUNDARIES:\n"
    "- DO NOT diagnose any medical or mental health conditions.\n"
    "- DO NOT prescribe medication or clinical treatment plans.\n"
    "- Keep responses deeply warm, grounded, and concise (under 3-4 sentences maximum) so the user doesn't feel overwhelmed by text."
)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Check hardcoded crisis words first
        if contains_crisis_keywords(request.message):
            return {"response": CRISIS_RESPONSE, "crisis_triggered": True}

        # New google-genai SDK text generation syntax
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=request.message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )
        )
        
        # Extract the text safely
        return {"response": response.text, "crisis_triggered": False}

    except Exception as e:
        # Catch and pass along explicit error details to the frontend
        raise HTTPException(status_code=400, detail=f"AI Service Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    # Access the dynamic PORT assigned by the hosting provider, fallback to 8001
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port)