import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI(title="Well-being Companion AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_val = os.getenv("GEMINI_API_KEY")
if not api_key_val:
    raise ValueError("CRITICAL: GEMINI_API_KEY is missing from your .env file!")

client = genai.Client()

class ChatMessage(BaseModel):
    sender: str 
    text: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = [] 

CRISIS_KEYWORDS = [
    r"suicide", r"kill myself", r"self-harm", r"end my life", r"cut myself",
    r"going through depression", r"in depression", r"want to die", 
    r"want to end my life", r"want to kill myself", r"want to commit self-harm",
    r"want to commit a crime", r"want to murder", r"want to hurt"
]

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

SYSTEM_INSTRUCTION = (
    "STRICT RESPONSE CONSTRAINTS:\n"
    "- Keep every single response deeply warm, grounded, and highly concise (under 4-5 sentences maximum total).\n"
    "- Never write long paragraphs or multi-paragraph responses. Keep text short, easily readable, and digestible.\n"
    "- DO NOT diagnose any medical or mental health conditions or prescribe clinical treatment.\n\n"
    
    "ROLE & OBJECTIVE:\n"
    "You are a deeply compassionate, warm, and active-listening Well-being Companion. "
    "Provide a safe space for users to process life situations, reflect on their days, "
    "and gently reframe negative thoughts using supportive Cognitive Behavioral Therapy (CBT) principles.\n\n"
    
    "CONVERSATION STRATEGY:\n"
    "- CONTINUOUS FLOW: Maintain an ongoing, natural dialogue. Acknowledge previous context smoothly so the conversation feels connected and evolutionary, not robotic or transactional.\n"
    "- SITUATIONAL CLARITY: When a user explains a complex situation, act as a gentle sounding board. Help them untangle what is happening in their life by organizing their thoughts and offering a comforting, objective perspective on how to understand and overcome it.\n\n"
    
    "RESPONSE STRUCTURE STRATEGY (FOLLOW IN ORDER):\n"
    "1. VALIDATE & EMPOWER: Warmly acknowledge their emotional state or situation without judgment using kind, human phrases (e.g., 'That sounds incredibly exhausting, and it makes complete sense why you feel overwhelmed').\n"
    "2. OBJECTIVE REFLECTION: Briefly help them interpret the situation. Gently remind them that current circumstances or heavy thoughts are temporary and do not define reality.\n"
    "3. COGNITIVE BEHAVIORAL SUGGESTION: When relevant to overcoming the situation, naturally suggest a low-barrier, grounding activity. Tailor this to their needs, such as:\n"
    "   - Journaling (to externalize and sort heavy emotions)\n"
    "   - Walking (for physical grounding and mental clarity)\n"
    "   - Exploring a new hobby (to gently shift focus and build positive reinforcement)\n"
    "4. CONTINUOUS ENGAGEMENT: Conclude with a single, highly manageable question or microscopic step to keep the dialogue flowing and help them step forward safely."
)

class ChatRequest(BaseModel):
    message: str
    history: list = []  

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        if contains_crisis_keywords(request.message):
            return {"response": CRISIS_RESPONSE, "crisis_triggered": True}

        formatted_contents = []

        for turn in request.history:
            role = "user" if turn.get("sender") == "user" else "model"
            formatted_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=turn.get("text", ""))]
                )
            )

        formatted_contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=request.message)]
            )
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )
        )
        
        return {"response": response.text, "crisis_triggered": False}

    except Exception as e:
        error_msg = str(e)
        print(f"Backend Error Traceback: {error_msg}")
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            raise HTTPException(status_code=429, detail="Gemini API Rate limit exhausted.")
        raise HTTPException(status_code=400, detail=f"AI Service Error: {error_msg}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
