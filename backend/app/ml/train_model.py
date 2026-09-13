from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "expense_dataset.csv"

MODEL_PATH = BASE_DIR / "app" / "ml" / "expense_classifier.joblib"


def train_model():
    # Load dataset
    data = pd.read_csv(DATA_PATH)

    print("Dataset loaded successfully.")
    print(f"Total records: {len(data)}")

    print("\nCategory distribution:")
    print(data["category"].value_counts())

    # Features and labels
    x = data["description"]
    y = data["category"]

    # Split dataset into training and testing
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    # ML pipeline:
    # TF-IDF -> Logistic Regression
    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )

    # Train model
    model.fit(x_train, y_train)

    # Test model
    predictions = model.predict(x_test)

    # Evaluate model
    accuracy = accuracy_score(y_test, predictions)

    print("\nModel Evaluation")
    print("----------------")
    print(f"Accuracy: {accuracy:.2%}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    # Save trained model
    joblib.dump(model, MODEL_PATH)

    print("\nModel saved successfully.")
    print(f"Saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
