from transformers import pipeline

# Load model
classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-3"
)

# Labels
sender_labels = ["customer", "spam", "internal"]

intent_labels = [
    "customer complaint about product or service",
    "customer asking question",
    "customer requesting something",
    "customer giving feedback"
]

intent_map = {
    "customer complaint about product or service": "complaint",
    "customer asking question": "query",
    "customer requesting something": "request",
    "customer giving feedback": "feedback"
}

routing_map = {
    "complaint": "support",
    "query": "support",
    "request": "sales",
    "feedback": "admin"
}

# =========================
# 🔴 KEYWORDS
# =========================
complaint_keywords = [
    "refund", "issue", "problem", "error", "failed",
    "not working", "defective", "damaged", "unhappy",
    "not delivered", "not arrived", "late"
]

urgent_keywords = ["urgent", "asap", "immediately", "quickly"]

query_keywords = ["what", "how", "when", "where", "why", "?","details","information"]

request_keywords = ["change", "cancel", "upgrade", "send", "schedule", "arrange", "replace"]

feedback_keywords = ["great", "amazing", "happy", "good", "love", "smooth", "helpful"]

# =========================
# 🚫 SPAM DETECTION
# =========================
def detect_spam(email):
    spam_words = ["buy now", "free", "offer", "win", "earn money"]
    return any(word in email.lower() for word in spam_words)


# =========================
# 🧠 RULE INTENT + KEYWORDS
# =========================
def rule_based_intent(email):
    email_lower = email.lower()
    detected = []

    for word in complaint_keywords:
        if word in email_lower:
            detected.append(word)
    if detected:
        return "complaint", detected

    for word in query_keywords:
        if word in email_lower:
            detected.append(word)
    if detected:
        return "query", detected

    for word in feedback_keywords:
        if word in email_lower:
            detected.append(word)
    if detected:
        return "feedback", detected

    for word in request_keywords:
        if word in email_lower:
            detected.append(word)
    if detected:
        return "request", detected

    return None, detected


# =========================
# ⚡ URGENCY
# =========================
def detect_urgency(email):
    email_lower = email.lower()

    if any(word in email_lower for word in urgent_keywords):
        return "high"

    if any(word in email_lower for word in feedback_keywords):
        return "low"

    return "medium"


# =========================
# 🎯 CONFIDENCE (DYNAMIC)
# =========================
def calculate_confidence(email, detected_keywords, urgency, ai_score=None):

    score = 50

    # keyword strength
    score += len(detected_keywords) * 12

    # urgency boost
    if urgency == "high":
        score += 10
    elif urgency == "low":
        score -= 5

    # email length
    if len(email) > 100:
        score += 5

    # AI contribution
    if ai_score:
        score += int(ai_score * 100 * 0.2)

    return min(max(score, 30), 100)


# =========================
# 🔥 PRIORITY SCORE
# =========================
def calculate_priority(intent, urgency):
    score = 50

    if intent == "complaint":
        score += 30
    if urgency == "high":
        score += 20

    return min(score, 100)


# =========================
# 🚀 MAIN FUNCTION
# =========================
def triage_email(email):

    # 1️⃣ Spam
    if detect_spam(email):
        return {
            "sender_type": "spam",
            "intent": "spam",
            "urgency": "low",
            "routing": "admin",
            "confidence": 95,
            "priority_score": 10,
            "keywords": ["spam"],
            "reason": "Spam detected"
        }

    # 2️⃣ Rule-based intent
    intent_result, detected_keywords = rule_based_intent(email)

    # 3️⃣ Urgency
    urgency_result = detect_urgency(email)

    if intent_result:
        confidence = calculate_confidence(email, detected_keywords, urgency_result)
        reason = f"Detected keywords: {', '.join(detected_keywords)}"
    else:
        intent = classifier(email, intent_labels)
        intent_result = intent_map[intent["labels"][0]]
        confidence = calculate_confidence(email, [], urgency_result, intent["scores"][0])
        reason = "AI classification"

    # 4️⃣ Sender
    sender = classifier(email, sender_labels)
    sender_result = sender["labels"][0]

    # 5️⃣ Routing
    routing = routing_map[intent_result]

    # 6️⃣ Priority
    priority_score = calculate_priority(intent_result, urgency_result)

    return {
        "sender_type": sender_result,
        "intent": intent_result,
        "urgency": urgency_result,
        "routing": routing,
        "confidence": confidence,
        "priority_score": priority_score,
        "keywords": detected_keywords,
        "reason": reason
    }