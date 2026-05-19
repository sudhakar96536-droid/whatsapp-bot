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
JOB_EXCEL_FILE = "job.xlsx"

# ============================================
# STORE USERS WAITING FOR PINCODE
# ============================================

waiting_for_pincode = {}
waiting_for_job_number = {}

# ============================================
# ONSITE COMPLAINT FLOW STORAGE
# ============================================

onsite_complaints = {}
warranty_registrations = {}

onsite_steps = [
    "name",
    "email",
    "alternate_phone",
    "state",
    "city",
    "pincode",
    "address1",
    "address2",
    "product_name",
    "product_serial_no",
    "warranty",
    "fault_type",
    "bill_no",
    "bill_date",
    "purchase_invoice"
]
warranty_steps = [
    "full_name",
    "email",
    "mobile_no",
    "product_model",
    "serial_no",
    "invoice_no",
    "invoice_copy",
    "purchase_date"
]

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
# TRACK COMPLAINT FROM EXCEL
# ============================================

def get_job_details(job_number):

    try:

        df = pd.read_excel(JOB_EXCEL_FILE)

        df["JOB_NO"] = df["JOB_NO"].astype(str)

        job_number = str(job_number).strip()

        result = df[df["JOB_NO"] == job_number]

        if not result.empty:

            return {
                "JOB_NO": result.iloc[0]["JOB_NO"],
                "JOB_DATE": result.iloc[0]["JOB_DATE"],
                "Location": result.iloc[0]["Location"],
                "CUSTOMER NAME": result.iloc[0]["CUSTOMER_NAME"],
                "Warranty": result.iloc[0]["Warranty"],
                "Product_Name": result.iloc[0]["Product_Name"],
                "Complaint": result.iloc[0]["Complaint"],
                "Status": result.iloc[0]["Status"]
            }

        return None

    except Exception as e:

        print("JOB EXCEL ERROR:")
        print(str(e))

        return None
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
                "text": "Welcome to ZEBRONICS ( Zebcare_Service ). We are delighted to assist you. Please choose the correct menu option."
            },
            "action": {
                "button": "Select Option",
                "sections": [
                    {
                        "title": "Main Menu",
                        "rows": [
                            {
                                "id": "opt1",
                                "title": "New Warranty Reg"
                            },
                            {
                                "id": "opt2",
                                "title": "Onsite Complaint Reg"
                            },
                            {
                                "id": "opt3",
                                "title": "Near Service Center"
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
                                "title": "Extend Warranty"
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
# SEND ONSITE COMPLAINT OPTIONS
# ============================================

def send_onsite_options(to):

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
            "type": "button",
            "body": {
                "text": "Onsite complaint registration method."
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "wa_form",
                            "title": "WhatsApp Form"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "web_form",
                            "title": "Website Form"
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print("ONSITE OPTIONS RESPONSE:")
    print(response.status_code)
    print(response.text)

# ============================================
# SEND WARRANTY OPTIONS
# ============================================

def send_warranty_options(to):

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
            "type": "button",
            "body": {
                "text": "New warranty registration method."
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "wa_warranty",
                            "title": "WhatsApp Form"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "web_warranty",
                            "title": "Website Form"
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print("WARRANTY OPTIONS RESPONSE:")
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
# ASK NEXT ONSITE QUESTION
# ============================================

def ask_next_onsite_question(sender):

    current_step_index = onsite_complaints[sender]["step"]

    if current_step_index < len(onsite_steps):

        current_field = onsite_steps[current_step_index]

        questions = {
            "name": "Please enter your Name",
            "email": "Please enter your Email",
            "alternate_phone": "Please enter Alternate Phone Number",
            "state": "Please enter State",
            "city": "Please enter City",
            "pincode": "Please enter Pincode",
            "address1": "Please enter Address Line 1",
            "address2": "Please enter Address Line 2",
            "product_name": "Please enter Product Name",
            "product_serial_no": "Please enter Product Serial Number",
            "warranty": "Please enter Warranty Details",
            "fault_type": "Please enter Fault Type",
            "bill_no": "Please enter Bill Number",
            "bill_date": "Please enter Bill Date",
            "purchase_invoice": "📎 Please upload Purchase Invoice\n\nSupported: jpg/jpeg/pdf\nMax size: 10MB"
        }

        send_message(sender, questions[current_field])

    else:

        data = onsite_complaints[sender]["data"]

        summary = f"""
✅ Onsite Complaint Submitted

👤 Name: {data.get('name')}
📧 Email: {data.get('email')}
📱 Alternate Phone: {data.get('alternate_phone')}
🌍 State: {data.get('state')}
🏙 City: {data.get('city')}
📍 Pincode: {data.get('pincode')}
🏠 Address1: {data.get('address1')}
🏠 Address2: {data.get('address2')}

🛒 Product Name: {data.get('product_name')}
🔢 Serial No: {data.get('product_serial_no')}
🛡 Warranty: {data.get('warranty')}
⚠ Fault Type: {data.get('fault_type')}
🧾 Bill No: {data.get('bill_no')}
📅 Bill Date: {data.get('bill_date')}
📎 Invoice Uploaded: Yes

Thank you!
Zebcare_Service
"""

        send_message(sender, summary)

        del onsite_complaints[sender]

# ============================================
# ASK NEXT WARRANTY QUESTION
# ============================================

def ask_next_warranty_question(sender):

    current_step_index = warranty_registrations[sender]["step"]

    if current_step_index < len(warranty_steps):

        current_field = warranty_steps[current_step_index]

        questions = {
            "full_name": "Please enter Full Name",
            "email": "Please enter Email Address",
            "mobile_no": "Please enter Mobile Number",
            "product_model": "Please enter Product Model",
            "serial_no": "Please enter Serial Number",
            "invoice_no": "Please enter Invoice Number",
            "invoice_copy": "📎 Please upload Invoice Copy\n\nSupported: jpg/jpeg/pdf\nMax size: 10MB",
            "purchase_date": "Please enter Purchase Date"
        }

        send_message(sender, questions[current_field])

    else:

        data = warranty_registrations[sender]["data"]

        summary = f"""
✅ Warranty Registration Info Submitted , We will Review & Confirm Shortly.

👤 Full Name: {data.get('full_name')}
📧 Email: {data.get('email')}
📱 Mobile No: {data.get('mobile_no')}
🛒 Product Model: {data.get('product_model')}
🔢 Serial No: {data.get('serial_no')}
🧾 Invoice No: {data.get('invoice_no')}
📎 Invoice Uploaded: Yes
📅 Purchase Date: {data.get('purchase_date')}

Thank you!
Zebcare_Service
"""

        send_message(sender, summary)

        del warranty_registrations[sender]
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
                # HANDLE INVOICE FILE UPLOAD
                # =================================

                if sender in onsite_complaints:

                    current_step_index = onsite_complaints[sender]["step"]

                    current_field = onsite_steps[current_step_index]

                    if current_field == "purchase_invoice":

                        if message["type"] == "image":

                            image_id = message["image"]["id"]

                            onsite_complaints[sender]["data"]["purchase_invoice"] = image_id

                            onsite_complaints[sender]["step"] += 1

                            ask_next_onsite_question(sender)

                            continue

                        elif message["type"] == "document":

                            document_id = message["document"]["id"]

                            onsite_complaints[sender]["data"]["purchase_invoice"] = document_id

                            onsite_complaints[sender]["step"] += 1

                            ask_next_onsite_question(sender)

                            continue

                        else:

                            send_message(
                                sender,
                                "❌ Please upload JPG/JPEG/PDF invoice only."
                            )

                            continue

                                # =================================
                # HANDLE WARRANTY FILE UPLOAD
                # =================================

                if sender in warranty_registrations:

                    current_step_index = warranty_registrations[sender]["step"]

                    current_field = warranty_steps[current_step_index]

                    if current_field == "invoice_copy":

                        if message["type"] == "image":

                            image_id = message["image"]["id"]

                            warranty_registrations[sender]["data"]["invoice_copy"] = image_id

                            warranty_registrations[sender]["step"] += 1

                            ask_next_warranty_question(sender)

                            continue

                        elif message["type"] == "document":

                            document_id = message["document"]["id"]

                            warranty_registrations[sender]["data"]["invoice_copy"] = document_id

                            warranty_registrations[sender]["step"] += 1

                            ask_next_warranty_question(sender)

                            continue

                        else:

                            send_message(
                                sender,
                                "❌ Please upload JPG/JPEG/PDF invoice only."
                            )

                            continue
                # =================================
                # TEXT MESSAGE
                # =================================

                if message["type"] == "text":

                    user_text = message["text"]["body"].strip()

                    print("USER MESSAGE:", user_text)

                    # =================================
                    # ONSITE COMPLAINT FLOW
                    # =================================

                    if sender in onsite_complaints:

                        current_step_index = onsite_complaints[sender]["step"]

                        current_field = onsite_steps[current_step_index]

                        onsite_complaints[sender]["data"][current_field] = user_text

                        onsite_complaints[sender]["step"] += 1

                        ask_next_onsite_question(sender)

                        continue

                    # =================================
                    # WARRANTY FLOW
                    # =================================

                    if sender in warranty_registrations:

                        current_step_index = warranty_registrations[sender]["step"]

                        current_field = warranty_steps[current_step_index]

                        warranty_registrations[sender]["data"][current_field] = user_text

                        warranty_registrations[sender]["step"] += 1

                        ask_next_warranty_question(sender)

                        continue
                    # =================================
                    # PINCODE FLOW
                    # =================================

                    if sender in waiting_for_pincode:

                        address, contact = get_service_center(user_text)

                        if address:

                            send_message(
                                sender,
                                f"✅ Nearest Zebronics Authorized Service Center\n\n📍 Address:\n{address}\n\n📞 Contact:\n{contact}\n\nThank you!\nZebcare_Service"
                            )

                        else:

                            send_message(
                                sender,
                                "❌ Service center not found for this pincode. Pls try again with any other pincode.\n\nThank you!\nZebcare_Service"
                            )

                        del waiting_for_pincode[sender]

                        continue

                                        # =================================
                    # TRACK COMPLAINT FLOW
                    # =================================

                    if sender in waiting_for_job_number:

                        job_data = get_job_details(user_text)

                        if job_data:

                            reply_message = f"""
✅ Complaint Status

📋 JOB NO: {job_data['JOB_NO']}
📅 JOB DATE: {job_data['JOB_DATE']}
📍 Location: {job_data['Location']}
👤 CUSTOMER NAME: {job_data['CUSTOMER NAME']}
🛡 Warranty: {job_data['Warranty']}
🛒 Product Name: {job_data['Product_Name']}
⚠ Complaint: {job_data['Complaint']}
📌 *Status: Pending & Remarks:* {job_data['Status']}

Thank you!
Zebcare_Service
"""

                            send_message(sender, reply_message)

                        else:

                            send_message(
                                sender,
                                "📌 *Status:* No Pending / Delivered\n\nThank you!\nZebcare_Service"
                            )

                        del waiting_for_job_number[sender]

                        continue
                    # =================================
                    # GREETINGS
                    # =================================

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

                    # =================================
                    # LIST REPLY
                    # =================================

                    if interactive["type"] == "list_reply":

                        selected_id = interactive["list_reply"]["id"]

                        selected_title = interactive["list_reply"]["title"]

                        print("SELECTED:", selected_id)

                        # =================================
                        # ONSITE COMPLAINT
                        # =================================

                        # =================================
                        # WARRANTY REGISTRATION
                        # =================================

                        if selected_id == "opt1":

                            send_warranty_options(sender)

                        elif selected_id == "opt2":

                            send_onsite_options(sender)

                        # =================================
                        # SERVICE CENTER
                        # =================================

                        elif selected_id == "opt3":

                            waiting_for_pincode[sender] = True

                            send_message(
                                sender,
                                "📍 Please enter your pincode to find nearest service center."
                            )

                                                # =================================
                        # TRACK COMPLAINT
                        # =================================

                        elif selected_id == "opt4":

                            waiting_for_job_number[sender] = True

                            send_message(
                                sender,
                                "📋 Please enter your full exact Job / Complaint Number."
                            )
                        # =================================
                        # OTHER OPTIONS
                        # =================================

                        else:

                            send_message(
                                sender,
                                f"✅ You selected: {selected_title}"
                            )

                    # =================================
                    # BUTTON REPLY
                    # =================================

                    elif interactive["type"] == "button_reply":

                        button_id = interactive["button_reply"]["id"]

                        print("BUTTON SELECTED:", button_id)

                        # =================================
                        # WHATSAPP FORM
                        # =================================

                        # =================================
                        # WHATSAPP WARRANTY FORM
                        # =================================

                        if button_id == "wa_warranty":

                            warranty_registrations[sender] = {
                                "step": 0,
                                "data": {}
                            }

                            ask_next_warranty_question(sender)

                        # =================================
                        # WEBSITE WARRANTY FORM
                        # =================================

                        elif button_id == "web_warranty":

                            send_message(
                                sender,
                                "Please register warranty using below website:\n\nhttps://support.zebronics.com/service-request/warranty-registration"
                            )
                            
                        elif button_id == "wa_form":

                            onsite_complaints[sender] = {
                                "step": 0,
                                "data": {}
                            }

                            ask_next_onsite_question(sender)

                        # =================================
                        # WEBSITE FORM
                        # =================================

                        elif button_id == "web_form":

                            send_message(
                                sender,
                                "Please register your complaint using below website:\n\nhttps://support.zebronics.com/service-request/"
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
