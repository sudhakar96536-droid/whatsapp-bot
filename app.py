from flask import Flask, request
import requests
import os
import pandas as pd

app = Flask(__name__)

# ============================================
# ENV VARIABLES
# ============================================

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

EXCEL_FILE = "pin.xlsx"

# ============================================
# STORE USERS WAITING FOR PINCODE
# ============================================

waiting_for_pincode = {}

# ============================================
# HOME ROUTE
# ============================================

@app.route("/")
def home():
    return "WhatsApp Bot Running Successfully"

# ============================================
# READ EXCEL AND FIND PINCODE
# ============================================

def get_service_center(pincode):

    try:

        df = pd.read_excel(EXCEL_FILE)

        # Convert PINCODE column to string
        df["PINCODE"] = df["PINCODE"].astype(str)

        pincode = str(pincode).strip()

        result = df[df["PINCODE"] == pincode]

        if not result.empty:

            address = result.iloc[0]["Address"]
            contact = result.iloc[0]["Contact"]

            return address, contact

        return None, None

    except Exception as e:

        print("EXCEL ERROR:")
        print(str(e))

        return None, None

# ============================================
# SEND LIST MESSAGE
# ============================================

def send_list_message(to):

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

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
                "text": "Welcome to Zebronics. We are delighted to assist you. Please choose the correct menu option."
            },
            "action": {
                "button": "Select Option",
                "sections": [
                    {
                        "title": "Available Options",
                        "rows": [
                            {
                                "id": "opt1",
                                "title": "Product Registration"
                            },
                            {
                                "id": "opt2",
                                "title": "Onsite Complaint"
                            },
                            {
                                "id": "opt3",
                                "title": "Service Center"
                            },
                            {
                                "id": "opt4",
                                "title": "Track Complaint"
                            },
                            {
                                "id": "opt5",
                                "title": "Tech Support"
                            },
                            {
                                "id": "opt6",
                                "title": "Free Warranty"
                            },
                            {
                                "id": "opt7",
                                "title": "Extended Warranty"
                            }
                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print("LIST RESPONSE:")
    print(response.status_code)
    print(response.text)

# ============================================
# SEND TEXT MESSAGE
# ============================================

def send_message(to, message):

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print("TEXT RESPONSE:")
    print(response.status_code)
    print(response.text)

# ============================================
# WEBHOOK
# ============================================

@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # ========================================
    # WEBHOOK VERIFICATION
    # ========================================

    if request.method == "GET":

        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if verify_token == VERIFY_TOKEN:
            return challenge, 200

        return "Invalid Verify Token", 403

    # ========================================
    # HANDLE POST EVENTS
    # ========================================

    if request.method == "POST":

        data = request.json

        print("FULL WEBHOOK DATA:")
        print(data)

        try:

            entry = data["entry"][0]["changes"][0]["value"]

            # ====================================
            # STATUS EVENTS
            # ====================================

            if "statuses" in entry:

                for status_data in entry["statuses"]:

                    recipient = status_data.get("recipient_id")
                    status = status_data.get("status")

                    print(f"STATUS UPDATE => {recipient} : {status}")

            # ====================================
            # CHECK IF MESSAGES EXIST
            # ====================================

            if "messages" not in entry:
                return "ok", 200

            # ====================================
            # LOOP ALL MESSAGES
            # ====================================

            for message in entry["messages"]:

                sender = message["from"]

                print("MESSAGE FROM:", sender)

                # =================================
                # TEXT MESSAGE
                # =================================

                if message["type"] == "text":

                    user_text = message["text"]["body"].strip()

                    print("USER MESSAGE:", user_text)

                    # =============================
                    # CHECK PINCODE FLOW
                    # =============================

                    if sender in waiting_for_pincode:

                        address, contact = get_service_center(user_text)

                        if address:

                            send_message(
                                sender,
                                f"✅ Nearest Zebronics Authorized Service Center\n\n📍 Address:\n{address}\n\n📞 Contact:\n{contact}\n\nThank you!"
                            )

                        else:

                            send_message(
                                sender,
                                "❌ Sorry, service center not found for this pincode."
                            )

                        # Remove from waiting list
                        del waiting_for_pincode[sender]

                        continue

                    # =============================
                    # NORMAL GREETINGS
                    # =============================

                    user_text_lower = user_text.lower()

                    greetings = [
                        "hi",
                        "hello",
                        "hii",
                        "hey",
                        "start"
                    ]

                    if user_text_lower in greetings:

                        send_list_message(sender)

                    else:

                        send_message(
                            sender,
                            "Please type HI to start."
                        )

                # =================================
                # INTERACTIVE MESSAGE
                # =================================

                elif message["type"] == "interactive":

                    interactive = message["interactive"]

                    # =============================
                    # LIST REPLY
                    # =============================

                    if interactive["type"] == "list_reply":

                        selected_id = interactive["list_reply"]["id"]
                        selected_title = interactive["list_reply"]["title"]

                        print("SELECTED:", selected_id)
                        print("TITLE:", selected_title)

                        # =========================
                        # SERVICE CENTER FLOW
                        # =========================

                        if selected_id == "opt3":

                            waiting_for_pincode[sender] = True

                            send_message(
                                sender,
                                "📍 Please enter your pincode to find nearest service center."
                            )

                        # =========================
                        # OTHER OPTIONS
                        # =========================

                        else:

                            send_message(
                                sender,
                                f"✅ You selected: {selected_title}"
                            )

        except Exception as e:

            print("ERROR:")
            print(str(e))

        return "ok", 200

# ============================================
# RUN APP
# ============================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
