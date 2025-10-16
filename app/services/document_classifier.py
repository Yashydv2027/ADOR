"""
Classify financial documents using keyword and pattern matching
"""
from typing import Dict, Any
import re


class DocumentClassifier:
    """Classify financial documents into predefined categories"""

    def __init__(self):
        self.categories = {
            'term_sheet': {
                'keywords': ['term sheet', 'termsheet', 'terms and conditions', 'product terms'],
                'patterns': [r'term\s*sheet', r'final\s*terms'],
                'weight': 1.0
            },
            'trade_confirmation': {
                'keywords': ['trade confirmation', 'trade date', 'settlement date', 'confirmation'],
                'patterns': [r'trade\s*confirmation', r'confirmation\s*of\s*trade'],
                'weight': 1.0
            },
            'trading_chat': {
                'keywords': ['chat', 'conversation', 'message', 'meeting'],
                'patterns': [r'\[\d{2}:\d{2}\]', r'\[\d{2}:\d{2}:\d{2}\]'],
                'weight': 0.9
            },
            'structured_note': {
                'keywords': ['structured note', 'structured product', 'capital protected',
                           'autocall', 'barrier', 'coupon'],
                'patterns': [r'structured\s+note', r'capital\s+protected'],
                'weight': 0.95
            },
            'contract': {
                'keywords': ['agreement', 'contract', 'isda', 'master agreement', 'parties'],
                'patterns': [r'this\s+agreement', r'master\s+agreement'],
                'weight': 0.85
            },
            'invoice': {
                'keywords': ['invoice', 'bill', 'payment due', 'total amount', 'invoice number'],
                'patterns': [r'invoice\s*#?\d+', r'payment\s+due'],
                'weight': 0.9
            },
            'research_report': {
                'keywords': ['analysis', 'research', 'recommendation', 'target price', 'outlook'],
                'patterns': [r'price\s+target', r'buy|sell|hold\s+recommendation'],
                'weight': 0.8
            },
            'general_financial': {
                'keywords': ['financial', 'finance', 'investment', 'portfolio'],
                'patterns': [],
                'weight': 0.5
            }
        }

    def classify(self, text: str, entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """Classify document based on text and entities"""
        text_lower = text.lower()
        scores = {}

        for category, config in self.categories.items():
            score = 0.0

            # Keyword matching
            keyword_matches = sum(1 for kw in config['keywords'] if kw in text_lower)
            score += keyword_matches * 0.3

            # Pattern matching
            pattern_matches = sum(1 for pattern in config['patterns']
                                if re.search(pattern, text_lower))
            score += pattern_matches * 0.5

            scores[category] = score * config['weight']

        # Adjust with entity hints
        if entities:
            scores = self._adjust_with_entities(scores, entities)

        # Get top category
        if not scores or max(scores.values()) == 0:
            return {
                'document_type': 'Unknown',
                'all_scores': {}
            }

        top_category = max(scores, key=scores.get)

        return {
            'document_type': self._format_category_name(top_category),
            'all_scores': {
                self._format_category_name(k): round(v, 2)
                for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
            }
        }

    def _adjust_with_entities(self, scores: Dict[str, float], entities: Dict[str, Any]) -> Dict[str, float]:
        """Adjust classification scores based on extracted entities"""

        if 'isin' in entities and entities['isin']:
            scores['structured_note'] += 0.5
            scores['trade_confirmation'] += 0.3

        if 'trade_references' in entities and entities['trade_references']:
            scores['trade_confirmation'] += 0.6

        if 'person' in entities and len(entities.get('person', [])) > 1:
            scores['trading_chat'] += 0.4

        if ('coupon' in entities and entities['coupon']) and \
           ('barrier' in entities and entities['barrier']):
            scores['structured_note'] += 0.6

        return scores

    def _format_category_name(self, category: str) -> str:
        """Format category name for display"""
        return category.replace('_', ' ').title()
