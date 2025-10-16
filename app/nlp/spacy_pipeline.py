import spacy
from typing import List, Dict, Any
import os

class SpacyNERPipeline:
    """Wrapper for spaCy NER models"""

    def __init__(self, model_name: str = "en_core_web_trf"):
        """
        Initialize spaCy pipeline

        Args:
            model_name: spaCy model to use (default: transformer-based)
        """
        self.model_name = model_name
        self.nlp = None
        self._load_model()

    def _load_model(self):
        """Load spaCy model"""
        try:
            self.nlp = spacy.load(self.model_name)
            print(f"✅ Loaded spaCy model: {self.model_name}")
        except OSError:
            print(f"⚠️  Model '{self.model_name}' not found. Downloading...")
            os.system(f"python -m spacy download {self.model_name}")
            self.nlp = spacy.load(self.model_name)

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        Args:
            text: Input text to process
        Returns:
            List of entities with type, text, start, end, and confidence
        """
        if not self.nlp:
            raise RuntimeError("spaCy model not loaded")

        doc = self.nlp(text)

        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': self._get_confidence(ent)
            })
        return entities
    
    def _get_confidence(self, ent) -> float:
        """
        Calculate confidence score for entity
        Uses various heuristics since spaCy doesn't provide direct confidence
        """
        # Base confidence by entity type
        confidence_map = {
            'ORG': 0.85,      # Organizations (companies)
            'PERSON': 0.80,    # Person names
            'MONEY': 0.90,     # Monetary values
            'DATE': 0.85,      # Dates
            'PERCENT': 0.88,   # Percentages
            'CARDINAL': 0.75,  # Numbers
            'GPE': 0.82,       # Geopolitical entities
            'PRODUCT': 0.78,   # Products
        }

        base_confidence = confidence_map.get(ent.label_, 0.70)

        # Adjust based on entity length (longer entities often more reliable)
        if len(ent.text) > 15:
            base_confidence += 0.05
        elif len(ent.text) < 3:
            base_confidence -= 0.10

        return min(0.95, max(0.50, base_confidence))

    def extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract and categorize financial entities
        Maps spaCy labels to financial entity types

        Returns:
            Dictionary of financial entity types
        """
        entities = self.extract_entities(text)

        financial_entities = {
            'counterparty': [],
            'person': [],
            'currency_amounts': [],
            'dates': [],
            'percentages': [],
            'numbers': [],
            'organizations': [],
            'locations': []
        }

        for ent in entities:
            label = ent['label']
            text = ent['text']

            # Map spaCy labels to financial categories
            if label == 'ORG':
                financial_entities['counterparty'].append(text)
                financial_entities['organizations'].append(text)
            elif label == 'PERSON':
                financial_entities['person'].append(text)
            elif label == 'MONEY':
                financial_entities['currency_amounts'].append(text)
            elif label == 'DATE':
                financial_entities['dates'].append(text)
            elif label == 'PERCENT':
                financial_entities['percentages'].append(text)
            elif label == 'CARDINAL':
                financial_entities['numbers'].append(text)
            elif label == 'GPE':
                financial_entities['locations'].append(text)

        # Remove empty categories
        return {k: v for k, v in financial_entities.items() if v}
