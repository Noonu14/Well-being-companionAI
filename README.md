🌱 MindEase
Your AI Well-being Companion

MindEase is a responsive, full-stack web application designed to serve as a safe space for daily reflection and mindfulness guidance. By leveraging structured Cognitive Behavioral Therapy (CBT) principles, the companion actively listens, validates emotional states, and suggests low-barrier grounding techniques to help users navigate daily stress and anxiety.

Live Demo: [https://noonu14.github.io/Well-being-companionAI/](https://noonu14.github.io/Well-being-companionAI/)

✨ Features

- **Empathetic CBT Persona:** Programmed with strict system guardrails to deliver warm, validating, and concise responses (under 4–5 sentences) that prevent text fatigue.
- **Rolling Context Memory:** Tracks conversation state through an asynchronous frontend/backend payload architecture, allowing the AI to maintain natural thread continuity across long chat sessions.
- **Actionable Grounding Exercises:** Dynamically suggests low-barrier cognitive interventions such as guided journaling, physical grounding (walking), and the classic 5-4-3-2-1 sensory technique.
- **Multi-Layered Safety Interceptor:** Features a hardcoded backend regex keyword scanner. If crisis text is detected, the application instantly short-circuits—bypassing the AI completely—to serve immediate, unalterable local helpline data (e.g., AASRA, Vandrevala Foundation).
- **Production-Ready Error Handling:** Automatically intercepts API rate limits (HTTP 429) to gracefully transition into a supportive placeholder message rather than breaking the UI thread.

---

🛠️ Tech Stack

- **Frontend:** HTML5, CSS3 (Modern Flexbox/Grid UI, Sidebar Layout), Asynchronous JavaScript (Fetch API)
- **Hosting (Frontend):** GitHub Pages
- **Backend:** Python 3.11+, FastAPI (Uvicorn ASGI server), Pydantic (Data Validation)
- **Hosting (Backend):** Render
- **AI Engine:** Google GenAI SDK (`google-genai`), powered by the **Gemini 2.5 Flash** model

---

🏗️ Architecture Flow

```text
[ Frontend: GitHub Pages ] 
           │
      (JSON Payload with Chat History Array)
           ▼
 [ Backend FastAPI: Render ] ──► [ Crisis Regex Scanner ] ──► (Match? Serve Helplines)
           │
   (Validates & Type-Maps History)
           ▼
[ Google GenAI: Gemini 2.5 Flash ] ──► (Returns Concise CBT Response)
