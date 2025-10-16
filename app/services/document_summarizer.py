from typing import Dict, Any, Optional
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class DocumentSummarizer:
    """Generate document summaries using LLM"""

    def __init__(self):
        self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            try:
                self.client = OpenAI(api_key=api_key)
                print("✅ Summarizer: OpenAI initialized")
            except Exception as e:
                print(f"⚠️  Summarizer initialization failed: {e}")

    def summarize(self, text: str) -> Dict[str, Any]:
        """Generate document summary using LLM"""
        text = self._clean_text(text)

        if len(text) < 100:
            return {
                "summary": text,
                "method": "original",
                "length": len(text.split()),
                "original_length": len(text.split()),
            }

        if not self.client:
            return {
                "summary": "Summarization requires OpenAI API key.",
                "method": "error",
                "length": 0,
                "original_length": len(text.split()),
            }

        summary = self._generate_summary(text)

        if not summary:
            return {
                "summary": "Failed to generate summary.",
                "method": "error",
                "length": 0,
                "original_length": len(text.split()),
            }

        return {
            "summary": summary,
            "method": "llm",
            "length": len(summary.split()),
            "original_length": len(text.split()),
        }

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s.,!?;:()\-\'\"]+", "", text)
        return text.strip()

    def _generate_summary(self, text: str) -> Optional[str]:
        """Generate summary using LLM"""
        try:
            if len(text) > 3000:
                text = text[:3000] + "..."

            prompt = f"""Summarize this financial document in 2-3 concise sentences. Focus on:
- Key financial terms (amounts, dates, rates)
- Main parties involved
- Purpose or type of document

Document:
{text}

Summary:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial document analyst. Provide concise, accurate summaries.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=150,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"❌ Summarization error: {e}")
            return None