from flask import Flask, request, jsonify, render_template
from model import triage_email
import threading
import time

# 👇 import your gmail function
import imaplib
import email

app = Flask(__name__)

email_store = []

# =========================
# 🔥 AUTO EMAIL FETCH FUNCTION
# =========================
def fetch_emails_loop():

    EMAIL = "yeahfenil@gmail.com"
    PASSWORD = "rgzn vhoc bppc ojeo"

    while True:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(EMAIL, PASSWORD)
            mail.select("inbox")

            status, messages = mail.search(None, "ALL")
            email_ids = messages[0].split()

            latest = email_ids[-5:]

            for e_id in reversed(latest):
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

                if not body:
                    continue

                # Avoid duplicates
                if any(body == item["email"] for item in email_store):
                    continue

                result = triage_email(body)

                email_store.append({
                    "email": body,
                    "result": result
                })

            mail.logout()

        except Exception as e:
            print("Fetch error:", e)

        time.sleep(10)  # 🔥 fetch every 10 sec


# Start background thread
threading.Thread(target=fetch_emails_loop, daemon=True).start()


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/emails")
def get_emails():
    return jsonify(email_store)


if __name__ == "__main__":
    app.run(debug=True)