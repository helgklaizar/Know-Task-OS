<div align="center">
  <h1>🎧 Intelligent Support Assistant</h1>
  <p><strong>ML-driven customer support routing pipeline. Fast, lightweight, and precise.</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/CatBoost-MultiClass-orange.svg?style=for-the-badge" alt="CatBoost">
    <img src="https://img.shields.io/badge/FastAPI-API-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  </p>
</div>

---

> 🍏 **Part of the Mac AI Ecosystem Initiative**
> This project is part of a large-scale initiative to create missing hardcore tools and extensions for AI development natively on Apple Silicon.

## 📋 TL;DR
A production-ready Machine Learning system that automatically routes customer support tickets to the correct department (e.g., Billing, Technical, Sales, Delivery) using NLP and CatBoost. It achieves **96.6% accuracy** on the Bitext support dataset, replacing the need for expensive LLM inference for basic routing tasks.

## 🚀 Features
- **⚡️ Blazing Fast Inference:** Uses `TfidfVectorizer` + `CatBoostClassifier` instead of heavy Transformers, executing in milliseconds on standard CPUs.
- **🎯 High Accuracy:** 96.6% accuracy across 11 complex support departments (Refunds, Delivery, Invoices, etc.).
- **🌐 REST API Ready:** Fully wrapped in a FastAPI microservice.
- **🖥️ UI Dashboard:** Includes a Streamlit interface for non-technical users to test ticket routing.
- **🐳 Dockerized:** One-command deployment via `docker-compose`.

## 🕹 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/klaizar/ml-support-assistant.git
cd ml-support-assistant

# 2. Start the API using Docker
docker-compose up -d

# 3. Test the prediction
curl -X 'POST' \
  'http://localhost:8000/predict' \
  -H 'Content-Type: application/json' \
  -d '{"text": "Where is my package? It is late!"}'
# Expected Output: {"department": "DELIVERY", "confidence": 0.98}
```

## 🏗 Architecture
The pipeline is designed with a strict **Data -> Model -> API** topology.
1. **Data:** Raw tickets are parsed and cleaned (Regex, Lowercasing).
2. **Feature Engineering:** TF-IDF vectorization (n-grams=1..2).
3. **Model:** `CatBoost` gradient boosting, optimized for multi-class NLP tasks.
4. **Delivery:** `FastAPI` serves the serialized `.pkl` and `.cbm` models.

## 🗺 Roadmap
- [x] Data Scraping & EDA
- [x] Classic ML Pipeline (CatBoost)
- [x] REST API Microservice
- [x] Dockerization & Streamlit UI
- [ ] Phase 3: Transition to local LLMs (MLX/Mistral) for complex conversational intents.

## 🤝 Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. Please read the `CONTRIBUTING.md` for guidelines.
