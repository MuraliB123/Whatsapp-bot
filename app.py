from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from pyngrok import ngrok
from utils import send_text_message
from dotenv import load_dotenv
import threading
import os
import uvicorn

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")
GREETED = False

@app.get("/webhook")
async def verify_token(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
    ):
    if hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Invalid verification token")

@app.post("/webhook")
async def webhook(request: Request):
    global GREETED
    data = await request.json()
    print("Received Webhook POST:")

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                if 'statuses' in value:
                    print("Received a status update, ignoring.")
                    continue

                messages = value.get("messages")
                if messages:
                    for message in messages:
                        sender = message.get("from")
                        msg_body = message.get("text", {}).get("body", "")
                        print(f"Message from {sender}: {msg_body}")

                        if not GREETED:
                            greeting_msg = "Hello Murali, I am Jarvis; your WhatsApp assistant from TMBC."
                            send_text_message(ACCESS_TOKEN, sender, greeting_msg)
                            GREETED = True
                            print("Sent greeting.")
                        else:
                            catalog_msg = (
                                "Welcome to Madras Branding Company! 🚀\n"
                                "We offer:\n"
                                "• Creative Direction\n"
                                "• Visual Design\n"
                                "• Branding\n"
                                "• Web & App Development\n"
                                "• 3D Design\n"
                                "• Video Production\n"
                                "Let us know what you're looking for, and we'll guide you!"
                            )
                            response = send_text_message(ACCESS_TOKEN, sender, catalog_msg)
                            print("Sent template message:")

    except Exception as e:
        print("Error processing message:", e)

    return JSONResponse(content={"status": "received"}, status_code=200)

@app.post("/send_messages")
async def send_messages(request: Request):
    try:
        data = await request.json()
        message_text = data['message']
        response = send_text_message(ACCESS_TOKEN, RECIPIENT_PHONE_NUMBER, message_text)
        return {"status": "success", "whatsapp_response": response}
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(e)})

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=5000)

if __name__ == '__main__':
    public_url = ngrok.connect(5000)
    print(f"Public URL: {public_url}")
    threading.Thread(target=run_server).start()
