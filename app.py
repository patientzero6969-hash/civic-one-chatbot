# app.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your chatbot router
from chatbot import router as chatbot_router

app = FastAPI(title="CrowCivic Chatbot API")

# Allow all origins (Hugging Face frontend will call this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your chatbot routes
app.include_router(chatbot_router)

@app.get("/")
def root():
    return {"message": "CrowCivic Chatbot API is running!"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=True)
