from typing import Dict, Any
from app.utils.file_handler import FileHandler
from app.services.docx_parser import DocxParser
from app.services.chat_ner import ChatNER
from app.services.pdf_llm import PdfLLM

class DocumentRouter:
    """Routes documents to appropriate processing pipeline"""

    def __init__(self):
        self.file_handler = FileHandler()
        self.docx_parser = DocxParser()
        self.chat_ner = ChatNER()
        self.pdf_llm = PdfLLM()

    def route(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Route document to appropriate parser based on file type

        Args:
            content: File content as bytes
            filename: Original filename

        Returns:
            Dictionary containing extracted entities and metadata
        """
        # Detect file type
        file_type = self.file_handler.detect_file_type(content, filename)

        # Validate file size
        if not self.file_handler.validate_file_size(content):
            raise ValueError("File size exceeds maximum limit (50MB)")

        # Route to appropriate parser
        if file_type == 'docx':
            return self._process_docx(content, filename)
        elif file_type == 'txt':
            return self._process_chat(content, filename)
        elif file_type == 'pdf':
            return self._process_pdf(content, filename)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _process_docx(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Process DOCX using rule-based parser"""
        entities = self.docx_parser.parse(content)
        return {
            'file_type': 'docx',
            'filename': filename,
            'method': 'rule-based',
            'entities': entities
        }

    def _process_chat(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Process chat text using NER model"""
        text = self.file_handler.read_text_file(content)
        entities = self.chat_ner.extract(text)
        return {
            'file_type': 'txt',
            'filename': filename,
            'method': 'ner_model',
            'entities': entities
        }

    def _process_pdf(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Process PDF using LLM extraction"""
        entities = self.pdf_llm.extract(content)
        return {
            'file_type': 'pdf',
            'filename': filename,
            'method': 'llm_rag',
            'entities': entities
        }