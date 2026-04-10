import imaplib
import email
import requests
import json

EMAIL = "yeahfenil@gmail.com"
PASSWORD = "rgzn vhoc bppc ojeo"

API_URL = "http://127.0.0.1:5000/analyze"

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(EMAIL, PASSWORD)
mail.select("inbox")

status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()

latest_10 = email_ids[-10:]

count = 0

for e_id in reversed(latest_10):
    status, msg_data = mail.fetch(e_id, "(RFC822)")
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(errors="ignore").replace("\r\n", " ").strip()
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(errors="ignore").replace("\r\n", " ").strip()

    # Skip empty
    if not body:
        continue

    print("\n========================")
    print("EMAIL:")
    print(body[:150])

    # ❌ REMOVE ALL FILTERS → THIS WAS YOUR ISSUE

    try:
        response = requests.post(API_URL, json={"email": body})
        result = response.json()

        print("\nAI RESULT:")
        print(json.dumps(result, indent=2))

        count += 1
        if count == 5:
            break

    except Exception as e:
        print("Error:", e)

mail.logout()