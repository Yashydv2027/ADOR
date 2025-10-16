from typing import Dict, Any, List
import os
from openai import OpenAI
from dotenv import load_dotenv


class DocumentQA:
    """Question Answering system for financial documents using LLM"""

    def __init__(self):
        self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.document_text = None
        self.conversation_history = []
        self.entities = {}
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize OpenAI client"""
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key and api_key != "your_openai_api_key_here":
            try:
                self.client = OpenAI(api_key=api_key)
                print("✅ Q&A: OpenAI client initialized")
            except Exception as e:
                print(f"Q&A initialization failed: {e}")
        else:
            print("Q&A: No valid OpenAI API key")

    def set_context(self, document_text: str, entities: Dict[str, Any] = None):
        """Set document context for Q&A"""
        self.document_text = document_text
        self.entities = entities or {}
        self.conversation_history = []

    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask a question about the document"""
        if not self.client:
            return {
                "answer": "Q&A requires OpenAI API key. Please configure OPENAI_API_KEY in .env file.",
                "sources": [],
                "error": "OpenAI not configured",
            }

        if not self.document_text:
            return {
                "answer": "No document context available. Please upload a document first.",
                "sources": [],
                "error": "No context",
            }

        try:
            # Truncate document if too long
            context = (
                self.document_text[:4000]
                if len(self.document_text) > 4000
                else self.document_text
            )

            # Build messages with context
            messages = [
                {
                    "role": "system",
                    "content": "You are a financial document analyst. Answer questions accurately based only on the provided document context. If information is not in the document, say so clearly.",
                },
                {
                    "role": "user",
                    "content": f"""Document Context:
{context}

{self._format_entities_for_context()}

Question: {question}

Answer based only on the document above.""",
                },
            ]

            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=300
            )

            answer = response.choices[0].message.content.strip()

            # Store in history
            self.conversation_history.append({
                "question": question,
                "answer": answer
            })

            return {
                "answer": answer,
                "sources": self._extract_relevant_sections(question, context),
                "conversation_id": len(self.conversation_history),
            }

        except Exception as e:
            print(f"❌ Q&A Error: {e}")
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "error": str(e),
            }

    def ask_multiple(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Ask multiple questions"""
        return [self.ask_question(q) for q in questions]

    def get_suggested_questions(self) -> List[str]:
        """Generate suggested questions based on entities"""
        if not self.document_text:
            return []

        suggestions = []

        # Entity-based suggestions
        if self.entities:
            if self.entities.get("counterparty"):
                suggestions.append("Who are the counterparties?")
            if self.entities.get("notional"):
                suggestions.append("What is the notional amount?")
            if self.entities.get("maturity"):
                suggestions.append("What is the maturity date?")
            if self.entities.get("coupon"):
                suggestions.append("What is the coupon rate?")
            if self.entities.get("isin"):
                suggestions.append("What is the ISIN?")

        # Default suggestions if no entities
        if not suggestions:
            suggestions = [
                "What is this document about?",
                "Who are the parties involved?",
                "What are the key terms?",
                "What are the important dates?",
                "What are the financial amounts?",
            ]

        return suggestions[:5]

    def _format_entities_for_context(self) -> str:
        """Format extracted entities for context"""
        if not self.entities:
            return ""

        lines = ["Extracted Information:"]
        for entity_type, values in self.entities.items():
            if values:
                if isinstance(values, list):
                    lines.append(f"- {entity_type.title()}: {', '.join(map(str, values))}")
                else:
                    lines.append(f"- {entity_type.title()}: {values}")

        return "\n".join(lines) if len(lines) > 1 else ""

    def _extract_relevant_sections(self, question: str, context: str) -> List[str]:
        """Extract relevant text sections for the question"""
        sentences = context.split(".")
        question_words = set(question.lower().split())

        relevant = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            sentence_words = set(sentence.lower().split())
            overlap = len(question_words.intersection(sentence_words))

            if overlap >= 2:
                relevant.append(sentence + ".")

        return relevant[:3]

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history.copy()
