from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from chatbot.dialogue_manager import DialogueManager
import json
import uvicorn

app = FastAPI()

app.chatbot = DialogueManager()
app.chatbot.create_chitchat_bot()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static")

@app.route("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/send_message')
async def send_message(request: Request):
    user_replic = await request.form()
    bot_replic = app.chatbot.generate_answer(user_replic["message"])
    reply = jsonable_encoder({"message" :  str(bot_replic)})
    return JSONResponse(reply)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5000,
        reload=True    
    )