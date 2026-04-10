from flask import Flask, jsonify, render_template
from model import triage_email
import threading
import time
import imaplib
import email
import os

app = Flask(__name__)

email_store = []

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

# =========================
# 📩 FETCH EMAILS LOOP
# =========================
def fetch_emails_loop():
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
                                body = payload.decode(errors="ignore").strip()
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore").strip()

                if not body:
                    continue

                # avoid duplicates
                if any(body == e["email"] for e in email_store):
                    continue

                result = triage_email(body)

                email_store.append({
                    "email": body,
                    "result": result
                })

            mail.logout()

        except Exception as e:
            print("Error:", e)

        time.sleep(10)

# start background thread
threading.Thread(target=fetch_emails_loop, daemon=True).start()

# =========================
# 🌐 ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/emails")
def get_emails():
    sorted_emails = sorted(
        email_store,
        key=lambda x: x["result"]["priority_score"],
        reverse=True
    )
    return jsonify(sorted_emails)

# =========================
# 🚀 RUN (RENDER FIX)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
