# ADOR - Augmented Document Reader

## Overview
**ADOR (Augmented Document Reader)** is a proof-of-concept (PoC) application built to demonstrate how AI and Natural Language Processing (NLP) can be used to automatically extract financial entities from structured and unstructured documents. The project focuses primarily on the **Named Entity Recognition (NER)** capability of an AI-powered document reader.

This work was developed as part of the *CMI Architecture & Innovation AI Engineer assignment*, focusing on parsing and extracting financial entities using Python, open-source NLP models, and Large Language Models (LLMs).

---

## Objectives
The goal of this project is to design and implement a modular document reader capable of:
- Parsing financial documents in multiple formats (`.pdf`, `.docx`, chat logs, etc.).
- Extracting key financial entities such as `Counterparty`, `ISIN`, `Notional`, `Maturity`, and `Underlying`.
- Leveraging different approaches (rule-based, model-based, and LLM-based) depending on document type.
- Providing an API and a Streamlit-based user interface for user interaction.

---

## Architecture
The system architecture follows a modular design comprising the following components:

1. **Frontend (User Interface)**
   - Built using **Streamlit** for interactive document upload and visualization.
   - Allows users to select document type and desired operation (NER, summarization, etc.).

2. **Backend (API Layer)**
   - Developed with **FastAPI**, exposing endpoints for document processing.
   - Manages requests from the frontend and delegates tasks to the appropriate processing module.

3. **Processing Layer**
   - **Rule-based Parser:** Handles structured documents like `.docx` using predefined financial extraction rules.
   - **NER Model:** Uses an open-source transformer model (e.g., `spaCy`, `Hugging Face`) for unstructured text and chat data.
   - **LLM Integration:** Employs large language models or RAG (Retrieval-Augmented Generation) pipelines for verbose, unstructured `.pdf` documents.

4. **Deployment**
   - Containerized using **Docker** for reproducibility and scalability.
   - Environment variables managed through `.env` files.

---

## Features
- Named Entity Recognition (NER) for financial documents.
- Multi-format document parsing (PDF, DOCX, Chat).
- Streamlit UI for document upload and results display.
- FastAPI backend for REST-based integration.
- Extensible architecture allowing additional features like classification and summarization.

---

## Tech Stack
| Component | Technology |
|------------|-------------|
| Language | Python 3.10+ |
| Frameworks | FastAPI, Streamlit |
| NLP Libraries | spaCy, Transformers (Hugging Face) |
| Containerization | Docker |
| Data Formats | PDF, DOCX, TXT |
| Version Control | Git |

---

## Installation & Setup

### Prerequisites
Ensure you have the following installed:
- Python 3.10+
- pip
- Docker (optional for containerized deployment)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/ADOR.git
   cd ADOR
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # For Linux/Mac
   venv\Scripts\activate    # For Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI backend:
   ```bash
   python app/main.py
   ```

5. Launch the Streamlit interface:
   ```bash
   streamlit run streamlit_app.py
   ```


---


## Future Enhancements
- Fine-tuning domain-specific NER models.
- Integration with vector databases for advanced RAG pipelines.
- Adding document summarization and classification capabilities.
- Expanding multi-language support.

---

## Author
**Developed by:** *Yash Yadav*
**Role:** AI Engineer
---
