# app/api/endpoints.py
"""
Main API endpoints for document extraction - FIXED
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import os

from app.services.docx_parser import DocxParser
from app.services.chat_ner import ChatNER
from app.services.pdf_llm import PdfLLM
from app.services.entity_formatter import EntityFormatter
from app.services.document_classifier import DocumentClassifier
from app.services.document_summarizer import DocumentSummarizer
from app.services.topic_modeller import TopicModeller

router = APIRouter(prefix="/api/v1", tags=["extraction"])


@router.post("/extract")
async def extract_entities(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Extract financial entities from uploaded document"""
    try:
        content = await file.read()
        filename = file.filename.lower()

        # Extract entities based on file type
        if filename.endswith('.docx'):
            parser = DocxParser()
            entities = parser.parse(content)
            extraction_method = "rule-based"

        elif filename.endswith('.txt'):
            text = content.decode('utf-8', errors='ignore')
            ner = ChatNER()
            entities = ner.extract(text)
            extraction_method = "ner-model"

        elif filename.endswith('.pdf'):
            pdf_parser = PdfLLM()
            entities = pdf_parser.extract(content)
            extraction_method = "llm-extraction"
            text = entities.pop('_full_text', '')

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Supported: DOCX, TXT, PDF"
            )

        # Extract full text
        if filename.endswith('.docx'):
            from docx import Document
            from io import BytesIO
            doc = Document(BytesIO(content))
            text = '\n'.join([para.text for para in doc.paragraphs])
        elif filename.endswith('.txt'):
            text = content.decode('utf-8', errors='ignore')

        # Classify document
        classifier = DocumentClassifier()
        classification = classifier.classify(text, entities)

        # Generate summary
        summarizer = DocumentSummarizer()
        summary_result = summarizer.summarize(text)

        # Extract topics
        topic_modeller = TopicModeller()
        topics = topic_modeller.extract_topics(text)

        # Format and return result - FIXED: Added filename parameter
        formatter = EntityFormatter()
        result = formatter.format({
            'file_type': filename.split('.')[-1].upper(),
            'method': extraction_method,
            'entities': entities,
            'classification': classification,
            'summary': summary_result,
            'topics': topics
        }, file.filename)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'ADOR API is running'}
