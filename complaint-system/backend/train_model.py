import os

import re

import pickle

import pandas as pd

import numpy as np

import nltk

from nltk.corpus import stopwords

from nltk.stem import WordNetLemmatizer

from nltk.tokenize import word_tokenize

for pkg in ["punkt", "stopwords", "wordnet", "omw-1.4", "punkt_tab"]:
    nltk.download(pkg, quiet=True)

stop_words = set(stopwords.words("english"))

lemmatizer = WordNetLemmatizer()


def preprocess_text(text: str) -> str:
    text = str(text).lower()

    text = re.sub(r"[^a-z\s]", "", text)

    tokens = word_tokenize(text)

    cleaned = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]

    return " ".join(cleaned)

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "ecommerce_consumer_complaints_5000.xlsx")

print("Loading dataset...")

df = pd.read_excel(DATASET_PATH)

print(f"Loaded {len(df)} rows")

print("Categories:", df["Category"].value_counts().to_dict())

print("Priorities:", df["Priority_Label"].value_counts().to_dict())

print("\nPreprocessing text (this may take a minute)...")

df["cleaned_text"] = df["Complaint_Text"].apply(preprocess_text)

from sklearn.pipeline import Pipeline

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split

from sklearn.metrics import classification_report

from sklearn.preprocessing import LabelEncoder

print("\nTraining Category classifier...")

cat_le = LabelEncoder()

y_cat = cat_le.fit_transform(df["Category"])

X = df["cleaned_text"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y_cat, test_size=0.2, stratify=y_cat, random_state=42

)

cat_pipeline = Pipeline([

    ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),

    ("clf", LogisticRegression(max_iter=1000, C=5.0, random_state=42)),

])

cat_pipeline.fit(X_train, y_train)

cat_acc = cat_pipeline.score(X_test, y_test)

print(f"Category Test Accuracy: {cat_acc*100:.2f}%")

print(classification_report(y_test, cat_pipeline.predict(X_test), target_names=cat_le.classes_))

print("\nTraining Priority classifier...")

prio_le = LabelEncoder()

y_prio = prio_le.fit_transform(df["Priority_Label"])

X_train2, X_test2, yp_train, yp_test = train_test_split(
    X, y_prio, test_size=0.2, stratify=y_prio, random_state=42

)

prio_pipeline = Pipeline([

    ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),

    ("clf", LogisticRegression(max_iter=1000, C=5.0, random_state=42)),

])

prio_pipeline.fit(X_train2, yp_train)

prio_acc = prio_pipeline.score(X_test2, yp_test)

print(f"Priority Test Accuracy: {prio_acc*100:.2f}%")

print(classification_report(yp_test, prio_pipeline.predict(X_test2), target_names=prio_le.classes_))

SAVE_DIR = os.path.dirname(__file__)

artifacts = {
    "category_model.pkl":   cat_pipeline,
    "category_encoder.pkl": cat_le,
    "priority_model.pkl":   prio_pipeline,
    "priority_encoder.pkl": prio_le,
}

for fname, obj in artifacts.items():
    path = os.path.join(SAVE_DIR, fname)

    with open(path, "wb") as f:
        pickle.dump(obj, f)

    print(f"Saved: {path}")

print("\nAll models saved successfully!")

print("Category classes:", list(cat_le.classes_))

print("Priority classes:", list(prio_le.classes_))
