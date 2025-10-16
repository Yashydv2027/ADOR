# app/services/pdf_llm.py
"""
LLM-based entity extraction for PDF documents
"""
from typing import Dict, Any, List
from io import BytesIO
import os
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv

from app.utils.text_utils import TextProcessor

load_dotenv()


class PdfLLM:
    """Extract financial entities from PDFs using LLM"""

    def __init__(self):
        self.text_processor = TextProcessor()
        self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            try:
                self.client = OpenAI(api_key=api_key)
                print(f"✅ OpenAI client initialized with model: {self.model}")
            except Exception as e:
                print(f"⚠️  OpenAI initialization failed: {e}")
        else:
            print("⚠️  No OpenAI API key found.")

    def extract(self, content: bytes) -> Dict[str, Any]:
        """Extract entities from PDF document"""
        text = self._extract_text_from_pdf(content)

        if not text:
            raise ValueError("Could not extract text from PDF")

        if self.client:
            entities = self._extract_with_llm(text)
        else:
            entities = self._extract_with_patterns(text)

        entities["_full_text"] = text
        return entities

    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF using pdfplumber"""
        text_parts = []

        try:
            with pdfplumber.open(BytesIO(content)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            for row in table:
                                if row:
                                    text_parts.append(
                                        " | ".join(
                                            [str(cell) if cell else "" for cell in row]
                                        )
                                    )

        except Exception as e:
            print(f"Error extracting PDF: {e}")
            raise

        full_text = "\n".join(text_parts)
        return self.text_processor.clean_text(full_text)

    def _extract_with_llm(self, text: str) -> Dict[str, Any]:
        """Extract entities using OpenAI GPT"""
        prompt = self._build_extraction_prompt(text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial document analyst. Extract ALL entity instances from documents.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
            )

            result_text = response.choices[0].message.content
            entities = self._parse_llm_response(result_text)

            print(
                f"✅ Extracted {sum(len(v) for v in entities.values())} total entities across {len(entities)} types"
            )
            return entities

        except Exception as e:
            print(f"LLM extraction error: {e}")
            return self._extract_with_patterns(text)

    def _build_extraction_prompt(self, text: str) -> str:
        """Build structured prompt for entity extraction"""
        if len(text) > 4000:
            text = text[:4000] + "\n... [truncated]"

        prompt = f"""Carefully analyze this financial document and extract ALL instances of these entities:

Document:
{text}

Extract ALL values (list multiple if found):

1. COUNTERPARTY: ALL company names, banks, investors, parties
2. NOTIONAL: ALL monetary amounts, investments, fees
3. ISIN: ISIN codes (12-character alphanumeric)
4. UNDERLYING: Instrument types (shares, bonds, preference shares)
5. MATURITY: Dates for maturity, expiry, closing, exit period
6. COUPON: Interest rates, dividend rates, IRR, returns
7. BARRIER: Thresholds, percentages, multipliers (2X, 10%, etc.)
8. TRADE_DATE: Transaction dates, issue dates
9. CURRENCY: Currencies (INR, USD, EUR, etc.)
10. PAYMENT_FREQUENCY: Payment schedule (quarterly, monthly)
11. STRIKE_PRICE: Strike prices

RULES:
- List EACH value on separate lines
- List every company/party separately
- List every rate/threshold separately
- If not found, write "Not found"

Format (repeat for multiple values):
COUNTERPARTY: [company 1]
COUNTERPARTY: [company 2]
NOTIONAL: [amount 1]
COUPON: [rate 1]
COUPON: [rate 2]
BARRIER: [threshold 1]
BARRIER: [threshold 2]

Extract everything you find."""

        return prompt

    def _parse_llm_response(self, response_text: str) -> Dict[str, List[str]]:
        """Parse LLM response - handles multiple values per entity type"""
        entities = {}
        lines = response_text.strip().split("\n")

        for line in lines:
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()

                    if value.lower() not in [
                        "not found",
                        "n/a",
                        "none",
                        "-",
                        "",
                        "not specified",
                    ]:
                        if key in ["counterparty", "issuer", "party", "investor"]:
                            entities.setdefault("counterparty", []).append(value)
                        elif key in ["notional", "principal", "amount", "investment"]:
                            entities.setdefault("notional", []).append(value)
                        elif key == "isin":
                            entities.setdefault("isin", []).append(value)
                        elif key in ["underlying", "reference", "asset", "instrument"]:
                            entities.setdefault("underlying", []).append(value)
                        elif key in ["maturity", "maturity_date", "expiry", "exit"]:
                            entities.setdefault("maturity", []).append(value)
                        elif key in [
                            "coupon",
                            "interest_rate",
                            "dividend",
                            "irr",
                            "return",
                        ]:
                            entities.setdefault("coupon", []).append(value)
                        elif key in ["barrier", "threshold", "multiplier"]:
                            entities.setdefault("barrier", []).append(value)
                        elif key in ["trade_date", "issue_date", "date"]:
                            entities.setdefault("trade_date", []).append(value)
                        elif key == "currency":
                            entities.setdefault("currency", []).append(value)
                        elif key in ["payment_frequency", "frequency"]:
                            entities.setdefault("payment_frequency", []).append(value)
                        elif key in ["strike_price", "strike"]:
                            entities.setdefault("strike_price", []).append(value)

        return entities

    def _extract_with_patterns(self, text: str) -> Dict[str, List[str]]:
        """Fallback: Extract entities using regex patterns"""
        from app.utils.regex_patterns import FinancialPatterns

        patterns = FinancialPatterns()
        entities = patterns.extract_all(text)

        return {k: v for k, v in entities.items() if v}
