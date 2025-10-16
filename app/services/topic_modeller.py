# app/services/topic_modeller.py
"""
LLM-Based Topic Modelling for Financial Documents
"""
from typing import Dict, Any, List
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class TopicModeller:
    """Extract topics using LLM (GPT-4o-mini)"""

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
                print("✅ Topic Modeller: OpenAI initialized")
            except Exception as e:
                print(f"⚠️  Topic Modeller failed: {e}")

    def extract_topics(self, text: str, max_topics: int = 5) -> Dict[str, Any]:
        """Extract topics from document using LLM"""
        if not self.client:
            return self._fallback_topics()

        try:
            text_sample = text[:3000] if len(text) > 3000 else text

            prompt = f"""Analyze this financial document and extract {max_topics} main topics.

Document:
{text_sample}

Return valid JSON with this structure:
{{
  "topics": [
    {{
      "name": "Topic Name",
      "relevance": 0.95,
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "description": "Brief description"
    }}
  ],
  "overall_theme": "One sentence main theme"
}}

Focus on financial topics: structured products, trading, derivatives, investment, risk management, etc.
Relevance: 0-1 scale."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial document analyst. Return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            topics = result.get('topics', [])
            overall_theme = result.get('overall_theme', 'Financial document')

            all_keywords = []
            for topic in topics:
                all_keywords.extend(topic.get('keywords', []))
            top_keywords = list(dict.fromkeys(all_keywords))[:10]

            return {
                'topics': topics[:max_topics],
                'top_keywords': top_keywords,
                'overall_theme': overall_theme,
                'num_topics': len(topics),
                'method': 'llm'
            }

        except Exception as e:
            print(f"❌ Topic extraction error: {e}")
            return self._fallback_topics()

    def _fallback_topics(self) -> Dict[str, Any]:
        """Fallback topics if LLM fails"""
        return {
            'topics': [
                {
                    'name': 'Financial Document',
                    'relevance': 0.7,
                    'keywords': ['financial', 'document', 'terms'],
                    'description': 'General financial document'
                }
            ],
            'top_keywords': ['financial', 'document', 'terms'],
            'overall_theme': 'Financial document',
            'num_topics': 1,
            'method': 'fallback'
        }
