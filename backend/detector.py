import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

class ScamDetectorV2:
    def __init__(self):
        # Improved dataset for V2
        self.training_data = [
            ("Your bank account has been compromised. Please share your OTP immediately.", "scam"),
            ("Your tax refund is pending. Verify your identity and send your card details.", "scam"),
            ("This is an urgent message from the IRS. You owe back taxes and must pay via gift card.", "scam"),
            ("Suspicious activity on your credit card. Press 1 to speak to an agent.", "scam"),
            ("Congratulations! You won a lottery. Pay the processing fee to claim.", "scam"),
            ("We are calling from social security administration... your number is suspended.", "scam"),
            ("Hi, are we still meeting at 2 PM?", "normal"),
            ("Can you send me the reports?", "normal"),
            ("I'll call you back in 5 minutes.", "normal"),
            ("Thank you for your order. It's on the way.", "normal"),
            ("Did you see the latest news?", "normal"),
            ("Happy birthday! See you tonight.", "normal")
        ]
        
        # More granular indicators
        self.scam_indicators = {
            "Time Pressure": [r"immediately", r"urgent", r"now", r"asap", r"deadline", r"few minutes"],
            "Financial Request": [r"bank", r"credit card", r"otp", r"gift card", r"wire transfer", r"payment", r"account"],
            "Identity Verification": [r"verify", r"identity", r"check", r"confirm your details", r"social security"],
            "Legal Threats": [r"irs", r"police", r"arrest", r"legal action", r"court", r"warrant"],
            "Unusual Gain": [r"won", r"prize", r"lottery", r"gift", r"vacation", r"reward"]
        }
        
        self.vectorizer = TfidfVectorizer() # Upgraded to TF-IDF
        self.model = MultinomialNB()
        self._train_model()

    def _train_model(self):
        texts, labels = zip(*self.training_data)
        X = self.vectorizer.fit_transform(texts)
        y = np.array(labels)
        self.model.fit(X, y)

    def analyze_text(self, text):
        if not text.strip():
            return {"score": 0, "indicators": [], "ml_confidence": 0}

        text_lower = text.lower()
        
        # --- LOGISTIC REGRESSION SIMULATION (Sigmoid Weights) ---
        weights = {
            "otp": 6.0, "pin": 5.0, "password": 5.0,
            "gift card": 6.0, "wire transfer": 6.0, "crypto": 5.0,
            "anydesk": 7.0, "teamviewer": 7.0, "rustdesk": 7.0,
            "bank": 3.0, "irs": 3.5, "police": 3.5, "social security": 4.0,
            "urgent": 2.5, "immediately": 2.5, "arrest": 5.0, "compromised": 3.5,
            "verify": 2.5, "blocked": 2.5, "unauthorized": 3.0, "refund": 3.0, "canceled": 3.0
        }
        
        total_threat_weight = 0
        detected_categories = []
        
        # 1. Rule-based Gewichtung
        for category, patterns in self.scam_indicators.items():
            matches = [p for p in patterns if re.search(p, text_lower)]
            if matches:
                detected_categories.append({
                    "category": category,
                    "matches": list(set(matches))
                })
                # Add weights for specific keywords found
                for word, weight in weights.items():
                    if word in text_lower:
                        total_threat_weight += weight

        # 2. Sigmoid Function (Logistic Regression Core)
        # Offset (Threshold) = 8.0 (Adjustable)
        # Scale (K) = 0.8 (Steepness of output)
        threshold = 8.0
        k = 0.8
        logistic_score = 100 / (1 + np.exp(-k * (total_threat_weight - threshold)))
        
        # 3. ML Model (Naive Bayes) fallback/blend
        X_test = self.vectorizer.transform([text])
        ml_prob = self.model.predict_proba(X_test)[0][1] * 100 
        
        # FINAL SCORE: Emphasize the Logistic Decisiveness
        final_score = max(logistic_score, ml_prob) if total_threat_weight > 0 else ml_prob
        
        # Hard Lock for "Ultra" Scam keywords
        if "otp" in text_lower or "gift card" in text_lower:
            final_score = max(final_score, 98.0)

        return {
            "score": round(final_score, 1),
            "indicators": detected_categories,
            "ml_confidence": round(ml_prob, 1),
            "threat_level": "SCAM DETECTED" if final_score > 80 else "CRITICAL" if final_score > 60 else "Monitoring"
        }
