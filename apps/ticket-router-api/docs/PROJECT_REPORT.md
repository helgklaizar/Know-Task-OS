# Project Report: Intelligent Support Assistant 🎧

## 1. Executive Summary
The project aims to create an automated support ticket routing system based on Machine Learning. The goal is to reduce the load on L1 support by automatically identifying the correct department (Billing, Tech, Sales, etc.) from the user's message text.

## 2. Data Collection Phase (Data Foundations)
- **Source:** Open HuggingFace dataset `bitext/Bitext-customer-support-llm-chatbot-training-dataset` was used.
- **Volume:** 5000 samples (optimized for rapid hypothesis testing).
- **Features:** `ticket_text` (text), `issue_type` (intent), `department` (target variable).
- **EDA Results:** Data was cleaned, revealing 11 unique departments. The average text length does not exceed 300 characters, which is ideal for TF-IDF vectorization.

## 3. Modeling Phase (Classic ML)
During Sprint 2, a classic machine learning model was trained.
- **Vectorization:** `TfidfVectorizer` (max_features=2000, n-grams=1..2, stop words removed). Converts text into numerical vectors.
- **Model:** `CatBoostClassifier` (by Yandex). Chosen for its high inference speed and out-of-the-box performance quality.
- **Training Parameters:** 100 iterations, `learning_rate=0.1`, tree depth `depth=6`.

### Evaluation Results
- **Accuracy:** 96.60% on the hold-out test set (1000 samples).
- **Metrics:** Precision for critical departments (`REFUND`, `PAYMENT`, `CONTACT`) reaches 99-100%.

## 4. Business Decision (Architecture Committee)
**Decision:** Abandon the implementation of heavyweight Deep Learning models (PyTorch, Transformers) at this stage.
**Justification:** 
1. CatBoost's accuracy (96.6%) more than satisfies the business requirements for a first-line router.
2. Using classic ML drastically reduces infrastructure costs (inference runs in milliseconds on a standard CPU; no GPU required).
3. Accelerated Time-to-Market.

## 5. Delivery Phase (MLOps)
The model and vectorizer are serialized (`.pkl` and `.cbm`). The next step is to wrap the system in a REST API service using **FastAPI**, which will allow it to be integrated into any existing CRM or helpdesk (Zendesk, Jira Service Desk).
