import requests
import json

def send_text_message(access_token, recipient_phone_number, message_text):
    url = 'https://graph.facebook.com/v22.0/640731862450213/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': recipient_phone_number,
        'type': 'text',
        'text': {
            'body': message_text
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json() 
