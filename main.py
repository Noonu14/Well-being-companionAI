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

# --- UPDATED REQUEST STRUCTURE TO INCLUDE HISTORY ---
class ChatMessage(BaseModel):
    sender: str  # "user" or "assistant"
    text: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = [] # Accepts the running history array from frontend

# 1. HARDCODED SAFETY PROTOCOL
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

# 2. SYSTEM INSTRUCTIONS (The Persona Guardrail)
SYSTEM_INSTRUCTION = (
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
    "4. CONTINUOUS ENGAGEMENT: Conclude with a single, highly manageable question or microscopic step to keep the dialogue flowing and help them step forward safely.\n\n"
    
    "STRICT SAFETY BOUNDARIES:\n"
    "- DO NOT diagnose any medical or mental health conditions.\n"
    "- DO NOT prescribe medication or clinical treatment plans.\n"
    "- Keep responses deeply warm, grounded, and concise (under 4-5 sentences maximum) to keep text easily readable and digestible."
)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Check hardcoded crisis words first
        if contains_crisis_keywords(request.message):
            return {"response": CRISIS_RESPONSE, "crisis_triggered": True}

        # --- RECONSTRUCT HISTORY INTO THE FORMAT THE CLIENT OBJECT EXPECTS ---
        formatted_contents = []
        for turn in request.history:
            # Map frontend names to Google API spec roles ("user" and "model")
            role = "user" if turn.sender == "user" else "model"
            formatted_contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=turn.text)])
            )
        
        # Append the current message to the end of the content chain
        formatted_contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=request.message)])
        )

        # New google-genai SDK text generation syntax with full thread context
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_contents, # Send full history + new message here
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
    # Access the dynamic PORT assigned by the hosting provider, fallback to 8001
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port)