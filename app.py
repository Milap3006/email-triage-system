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
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode(errors="ignore")
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore")

                # 🔥 CLEAN TEXT
                body = body.replace("\r\n", " ").strip()

                # 🔥 VERY IMPORTANT (fallback)
                if not body or len(body) < 10:
                    body = msg.get("subject", "No content")

                # avoid duplicates
                if any(body == e["email"] for e in email_store):
                    continue

                result = triage_email(body)

                email_store.append({
                    "email": body,
                    "result": result
                })

                print("✅ Added:", body[:50])  # DEBUG

            mail.logout()

        except Exception as e:
            print("Error:", e)

        time.sleep(10)
