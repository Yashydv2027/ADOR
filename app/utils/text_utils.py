import re
from typing import List

class TextProcessor:
    """Text cleaning and normalization utilities"""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text
        - Remove extra whitespace
        - Normalize line breaks
        - Remove special characters (optional)
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)

        return text

    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def chunk_text(text: str, max_length: int = 1000, overlap: int = 100) -> List[str]:
        """
        Chunk text into overlapping segments for processing

        Args:
            text: Input text
            max_length: Maximum chunk length in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + max_length

            # Try to break at sentence boundary
            if end < text_len:
                # Look for sentence end within last 100 chars
                chunk = text[start:end]
                last_period = chunk.rfind('.')
                last_question = chunk.rfind('?')
                last_exclaim = chunk.rfind('!')

                break_point = max(last_period, last_question, last_exclaim)
                if break_point > len(chunk) - 100:
                    end = start + break_point + 1

            chunks.append(text[start:end].strip())
            start = end - overlap

        return chunks

    @staticmethod
    def normalize_entity(entity_text: str) -> str:
        """Normalize extracted entity text"""
        # Remove extra whitespace
        entity_text = re.sub(r'\s+', ' ', entity_text)

        # Capitalize properly for names
        if entity_text.isupper() and len(entity_text) > 3:
            entity_text = entity_text.title()

        return entity_text.strip()
