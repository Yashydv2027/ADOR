import os
from typing import Tuple, Optional
from io import BytesIO
import magic  # python-magic for file type detection


class FileHandler:
    """Handles file type detection and content extraction"""

    SUPPORTED_TYPES = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt",
    }

    @staticmethod
    def detect_file_type(content: bytes, filename: str) -> str:
        """
        Detect file type from content and filename

        Args:
            content: File content as bytes
            filename: Original filename

        Returns:
            File type: 'pdf', 'docx', or 'txt'
        """
        # Try extension first
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            return "pdf"
        elif ext == ".docx":
            return "docx"
        elif ext == ".txt":
            return "txt"

        # Fallback to magic number detection
        try:
            mime = magic.from_buffer(content, mime=True)
            return FileHandler.SUPPORTED_TYPES.get(mime, "unknown")
        except:
            return "unknown"

    @staticmethod
    def validate_file_size(content: bytes, max_size_mb: int = 50) -> bool:
        """Validate file size is within limits"""
        size_mb = len(content) / (1024 * 1024)
        return size_mb <= max_size_mb

    @staticmethod
    def read_text_file(content: bytes) -> str:
        """Read text content from bytes"""
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
                try:
                    return content.decode(encoding)
                except:
                    continue
            raise ValueError("Unable to decode text file")
