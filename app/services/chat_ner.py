from typing import Dict, Any, List
import re

from app.nlp.spacy_pipeline import SpacyNERPipeline
from app.utils.text_utils import TextProcessor
from app.utils.regex_patterns import FinancialPatterns


class ChatNER:
    """Extract financial entities from unstructured chat messages"""

    def __init__(self):
        self.ner_pipeline = SpacyNERPipeline()
        self.text_processor = TextProcessor()
        self.patterns = FinancialPatterns()

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract entities from chat text"""
        cleaned_text = self.text_processor.clean_text(text)

        # Extract using multiple methods
        ner_entities = self.ner_pipeline.extract_financial_entities(cleaned_text)
        pattern_entities = self.patterns.extract_all(cleaned_text)
        chat_entities = self._extract_chat_specific(cleaned_text)

        # Merge and deduplicate
        merged = self._merge_entities(ner_entities, pattern_entities, chat_entities)

        return self._post_process(merged, cleaned_text)

    def _extract_chat_specific(self, text: str) -> Dict[str, List[str]]:
        """Extract chat-specific financial entities"""
        entities = {}

        # ISIN codes
        isin_matches = self.patterns.ISIN.findall(text)
        if isin_matches:
            entities['isin'] = isin_matches

        # Notional amounts: "200 mio", "500 million"
        notional_pattern = re.compile(r'(\d+)\s*(mio|million|bn|billion)', re.IGNORECASE)
        notional_matches = notional_pattern.findall(text)
        if notional_matches:
            entities['notional'] = [f"{amount} {unit}" for amount, unit in notional_matches]

        # Interest rates: "estr+45bps", "libor+50"
        rate_pattern = re.compile(r'(\w+\s*[+\-]\s*\d+\s*bps)', re.IGNORECASE)
        rate_matches = rate_pattern.findall(text)
        if rate_matches:
            entities['interest_rate'] = rate_matches

        # Payment frequency
        freq_pattern = re.compile(r'\b(Quarterly|Monthly|Semi-annually|Annually)\b', re.IGNORECASE)
        freq_matches = freq_pattern.findall(text)
        if freq_matches:
            entities['payment_frequency'] = list(set(freq_matches))

        # Tenor: "2Y", "5Y", "10Y"
        tenor_pattern = re.compile(r'\b(\d+Y)\b')
        tenor_matches = tenor_pattern.findall(text)
        if tenor_matches:
            entities['tenor'] = tenor_matches

        # Underlying rates: "estr", "euribor", "libor"
        underlying_pattern = re.compile(r'\b(estr|euribor|libor|sofr)\b', re.IGNORECASE)
        underlying_matches = underlying_pattern.findall(text)
        if underlying_matches:
            entities['underlying'] = list(set([u.lower() for u in underlying_matches]))

        return entities

    def _merge_entities(self, *entity_dicts) -> Dict[str, List[str]]:
        """Merge and deduplicate entities from multiple sources"""
        merged = {}

        for entity_dict in entity_dicts:
            for entity_type, values in entity_dict.items():
                if entity_type not in merged:
                    merged[entity_type] = []

                if isinstance(values, list):
                    merged[entity_type].extend(values)
                else:
                    merged[entity_type].append(values)

        # Deduplicate
        for entity_type in merged:
            seen = set()
            deduped = []
            for item in merged[entity_type]:
                normalized = str(item).strip().lower()
                if normalized not in seen:
                    seen.add(normalized)
                    deduped.append(str(item).strip())
            merged[entity_type] = deduped

        return merged

    def _post_process(self, entities: Dict[str, List[str]], text: str) -> Dict[str, List[str]]:
        """Post-process and validate entities"""
        processed = {}

        for entity_type, values in entities.items():
            processed_values = []

            for value in values:
                # Skip very short values
                if len(value) < 2:
                    continue

                # Normalize
                normalized = self.text_processor.normalize_entity(value)

                # Expand counterparty abbreviations
                if entity_type == 'counterparty':
                    normalized = self._expand_abbreviations(normalized)

                # Validate ISIN format
                if entity_type == 'isin' and not self._validate_isin(normalized):
                    continue

                processed_values.append(normalized)

            if processed_values:
                processed[entity_type] = processed_values

        return processed

    def _expand_abbreviations(self, text: str) -> str:
        """Expand common bank abbreviations"""
        abbreviations = {
            'GS': 'Goldman Sachs',
            'MS': 'Morgan Stanley',
            'JPM': 'JPMorgan',
            'BAC': 'Bank of America',
            'C': 'Citigroup',
            'DB': 'Deutsche Bank',
            'UBS': 'UBS Group',
            'CS': 'Credit Suisse',
            'HSBC': 'HSBC Holdings',
            'BNP': 'BNP Paribas'
        }

        if text.upper() in abbreviations:
            return abbreviations[text.upper()]
        return text

    def _validate_isin(self, isin: str) -> bool:
        """Validate ISIN format: 2 letters + 9 alphanumeric + 1 digit"""
        if len(isin) != 12:
            return False
        if not isin[:2].isalpha():
            return False
        if not isin[2:11].isalnum():
            return False
        if not isin[11].isdigit():
            return False
        return True
