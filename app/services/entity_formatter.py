"""
Entity formatter - standardizes output format across all parsers
"""
from typing import Dict, Any, List
from datetime import datetime


class EntityFormatter:
    """Formats extracted entities into standardized output"""

    FINANCIAL_ENTITY_TYPES = [
        "counterparty",
        "notional",
        "isin",
        "underlying",
        "maturity",
        "coupon",
        "barrier",
        "trade_date",
        "currency",
        "interest_rate",
        "payment_frequency",
    ]

    def format(self, raw_result: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """
        Format raw extraction results into standardized output

        Args:
            raw_result: Raw results from parser (includes all features)
            filename: Original filename

        Returns:
            Formatted result with all analysis results
        """
        entities = raw_result.get("entities", {})
        classification = raw_result.get("classification", {})
        summary = raw_result.get("summary", {})
        topics = raw_result.get("topics", {})

        # Standardize entity structure
        formatted_entities = self._standardize_entities(entities)

        # Calculate statistics
        stats = self._calculate_stats(formatted_entities)

        return {
            "success": True,
            "metadata": {
                "filename": filename,
                "file_type": raw_result.get("file_type"),
                "extraction_method": raw_result.get("method"),
                "processed_at": datetime.utcnow().isoformat(),
                "entity_count": stats["total_entities"],
            },
            "classification": classification,
            "summary": summary,
            "topics": topics,
            "entities": formatted_entities,
            "statistics": stats,
        }

    def _standardize_entities(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert entities to standardized list format"""
        standardized = []

        for entity_type, values in entities.items():
            if not values:
                continue

            # Handle list or single values
            value_list = values if isinstance(values, list) else [values]

            for value in value_list:
                standardized.append({"type": entity_type, "value": str(value).strip()})

        return standardized

    def _calculate_stats(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics about extracted entities"""
        entity_types = {}

        for entity in entities:
            entity_type = entity["type"]
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

        return {"total_entities": len(entities), "entity_types": entity_types}
