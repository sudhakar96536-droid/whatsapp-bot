from flask import Flask, request
import requests
import os

app = Flask(__name__)

ACCESS_TOKEN = "EAFwzEuhXDBoBRHqZBkZAwOzNLHoAyVCvNjWxAjw253aHQ5ZAvgnze5ZCdH5RkUIhOd1d309Fqoal6TfY3pc9a14SaS63ZAdBCPXR7wr8kS9oRG89l77bMaU1oEgT1eVQ1kbHhHg5FkKTPLTXYrJn8h5WtcZArTJfErhOZAZCgWHBsvoUpNb4OyATPi4SFejTVWVx0wZDZD"
PHONE_NUMBER_ID = "1122752727584250"
VERIFY_TOKEN = "hello123"


# 🔹 Send WhatsApp List Message (7 options)
def send_list_message(to):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "Welcome to Zebronics, We are delighted to assist you, pls choose correct menu options to proceed"
            },
            "action": {
                "button": "Select Option",
                "sections": [
                    {
                        "title": "Available Options",
                        "rows": [
                            {"id": "opt1", "title": "Product Registration"},
                            {"id": "opt2", "title": "Onsite Complaint"},
                            {"id": "opt3", "title": "Service Center"},
                            {"id": "opt4", "title": "Track Complaint"},
                            {"id": "opt5", "title": "Tech Support"},
                            {"id": "opt6", "title": "Free Warranty"},
                            {"id": "opt7", "title": "Extended Warranty"}
                        ]
                    }
                ]
            }
        }
    }

    requests.post(url, headers=headers, json=data)


# 🔹 Send Text Message
def send_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    requests.post(url, headers=headers, json=data)


# 🔹 Webhook
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # ✅ Verification
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Invalid token", 403

    # ✅ Handle Messages
    if request.method == "POST":
        data = request.json

        try:
            entry = data["entry"][0]["changes"][0]["value"]

            if "messages" not in entry:
                return "ok", 200

            message = entry["messages"][0]
            sender = message["from"]

            # 🔹 TEXT MESSAGE (Hi trigger)
            if message["type"] == "text":
                user_text = message["text"]["body"].strip().lower()

                if user_text == "hi":
                    send_list_message(sender)
                else:
                    send_message(sender, "Please type 'hi' to start.")

            # 🔹 BUTTON / LIST RESPONSE
            elif message["type"] == "interactive":
                selected_id = message["interactive"]["list_reply"]["id"]
                selected_title = message["interactive"]["list_reply"]["title"]

                send_message(sender, f"✅ You have selected {selected_title}")

        except Exception as e:
            print("Error:", e)

        return "ok", 200


# 🔹 Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)