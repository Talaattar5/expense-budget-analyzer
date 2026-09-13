from pathlib import Path

import joblib

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "app" / "ml" / "expense_classifier.joblib"

model = joblib.load(MODEL_PATH)


FALLBACK_KEYWORDS = {
    "Transportation": [
        "uber",
        "taxi",
        "careem",
        "bus",
        "fuel",
        "gas station",
        "parking",
        "metro",
        "train",
    ],
    "Food": [
        "restaurant",
        "coffee",
        "burger",
        "pizza",
        "lunch",
        "dinner",
        "breakfast",
        "groceries",
        "food",
    ],
    "Shopping": [
        "clothes",
        "shoes",
        "mall",
        "shopping",
        "headphones",
        "bag",
        "watch",
    ],
    "Education": [
        "tuition",
        "course",
        "university",
        "textbook",
        "exam",
        "training",
    ],
    "Entertainment": [
        "netflix",
        "spotify",
        "cinema",
        "movie",
        "game",
        "gaming",
        "concert",
    ],
    "Bills": [
        "electricity",
        "water bill",
        "internet bill",
        "phone bill",
        "wifi",
        "utility",
    ],
}


def keyword_fallback(description: str) -> str:
    text = description.lower()

    for category, keywords in FALLBACK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "Other"


def classify_expense(description: str) -> dict:
    probabilities = model.predict_proba([description])[0]

    classes = model.classes_

    best_index = probabilities.argmax()

    predicted_category = classes[best_index]

    confidence = float(probabilities[best_index])

    used_fallback = False

    if confidence < 0.50:
        predicted_category = keyword_fallback(description)
        used_fallback = True

    return {
        "category": predicted_category,
        "confidence": round(confidence, 4),
        "used_fallback": used_fallback,
    }
