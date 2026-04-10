def triage_email(email):

    email_lower = email.lower()

    keywords = []

    # =====================
    # SPAM
    # =====================
    spam_words = ["buy now", "free", "offer", "win", "earn"]

    if any(word in email_lower for word in spam_words):
        return {
            "sender_type": "spam",
            "intent": "spam",
            "urgency": "low",
            "routing": "admin",
            "confidence": 95,
            "priority_score": 10,
            "keywords": ["spam"],
            "reason": "Spam keywords detected"
        }

    # =====================
    # INTENT DETECTION
    # =====================
    intent = "query"

    if any(word in email_lower for word in ["refund", "issue", "problem", "not working", "defective"]):
        intent = "complaint"
        keywords.append("issue")

    elif any(word in email_lower for word in ["change", "cancel", "upgrade", "send", "schedule"]):
        intent = "request"
        keywords.append("action")

    elif any(word in email_lower for word in ["great", "amazing", "happy", "good"]):
        intent = "feedback"
        keywords.append("positive")

    elif "?" in email_lower:
        intent = "query"
        keywords.append("question")

    # =====================
    # URGENCY
    # =====================
    urgency = "medium"

    if any(word in email_lower for word in ["urgent", "asap", "immediately"]):
        urgency = "high"

    elif intent == "feedback":
        urgency = "low"

    # =====================
    # ROUTING
    # =====================
    routing_map = {
        "complaint": "support",
        "query": "support",
        "request": "sales",
        "feedback": "admin"
    }

    routing = routing_map[intent]

    # =====================
    # CONFIDENCE (DYNAMIC)
    # =====================
    confidence = 60 + len(keywords) * 10

    if urgency == "high":
        confidence += 10

    confidence = min(confidence, 95)

    # =====================
    # PRIORITY
    # =====================
    priority = 50

    if intent == "complaint":
        priority += 30
    if urgency == "high":
        priority += 20

    priority = min(priority, 100)

    return {
        "sender_type": "customer",
        "intent": intent,
        "urgency": urgency,
        "routing": routing,
        "confidence": confidence,
        "priority_score": priority,
        "keywords": keywords,
        "reason": f"Detected keywords: {', '.join(keywords)}"
    }
