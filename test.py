from model import triage_email

test_data = [
    ("I want refund, this product is defective", "complaint"),
    ("My order has not arrived yet", "complaint"),
    ("I received damaged item", "complaint"),
    ("Payment deducted but no confirmation", "complaint"),
    ("Very poor service, I am unhappy", "complaint"),
    ("Repeated issue with product", "complaint"),

    ("What is my order status?", "query"),
    ("Do you offer international shipping?", "query"),
    ("Share warranty details", "query"),
    ("How to track my order?", "query"),
    ("How can I contact support?", "query"),
    ("What are your working hours?", "query"),

    ("Change my delivery address", "request"),
    ("Cancel my order", "request"),
    ("Upgrade my subscription", "request"),
    ("Send invoice", "request"),
    ("Schedule a call", "request"),
    ("Arrange replacement", "request"),

    ("Great service, very happy", "feedback"),
    ("Amazing product quality", "feedback"),
    ("Smooth experience", "feedback"),
    ("Helpful support team", "feedback"),
    ("App is very easy to use", "feedback"),
    ("Thanks for quick response", "feedback"),

    ("Buy now and get 70% off", "spam"),
    ("You won a gift card", "spam"),
    ("Earn money fast", "spam"),
    ("Exclusive deal click now", "spam"),
    ("You are lucky winner", "spam"),
    ("Free subscription offer", "spam"),
]

correct = 0
total = len(test_data)

for i, (email, expected) in enumerate(test_data):
    result = triage_email(email)
    predicted = result["intent"]

    print(f"\nEmail {i+1}: {email}")
    print("Expected:", expected)
    print("Predicted:", predicted)

    if predicted == expected:
        print("✅ Correct")
        correct += 1
    else:
        print("❌ Wrong")

accuracy = (correct / total) * 100

print("\n======================")
print(f"Accuracy: {accuracy:.2f}%")
print("======================")