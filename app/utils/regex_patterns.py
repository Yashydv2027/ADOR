import re

class FinancialPatterns:
    """Compiled regex patterns for financial entities"""

    # ISIN pattern: 2 letter country code + 9 alphanumeric + 1 check digit
    ISIN = re.compile(r'\b[A-Z]{2}[A-Z0-9]{9}[0-9]\b')

    # Currency amounts: $1,234.56 or EUR 1234.56
    CURRENCY = re.compile(r'(?:USD|EUR|GBP|JPY|\$|€|£)\s*[\d,]+\.?\d*(?:M|K|B)?', re.IGNORECASE)

    # Dates: Multiple formats
    DATE = re.compile(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{2}[-/]\d{2}|'
                      r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b',
                      re.IGNORECASE)

    # Percentages
    PERCENTAGE = re.compile(r'\b\d+\.?\d*\s*%')

    # Notional amounts (looking for keywords)
    NOTIONAL_KEYWORDS = re.compile(r'(?:notional|principal|amount):\s*([\d,]+\.?\d*)', re.IGNORECASE)

    # Coupon rate
    COUPON_KEYWORDS = re.compile(r'(?:coupon|interest\s+rate):\s*(\d+\.?\d*\s*%)', re.IGNORECASE)

    # Maturity
    MATURITY_KEYWORDS = re.compile(r'(?:maturity|expiry|expiration):\s*([^\n]+)', re.IGNORECASE)

    # Counterparty (company names pattern)
    COUNTERPARTY_KEYWORDS = re.compile(r'(?:counterparty|party|issuer):\s*([A-Z][a-zA-Z\s&,\.]+(?:Inc|LLC|Ltd|Corp|AG|SA|plc)?)',re.IGNORECASE)

    # Underlying asset
    UNDERLYING_KEYWORDS = re.compile(r'(?:underlying|reference|asset):\s*([^\n]+)', re.IGNORECASE)

    # Barrier level
    BARRIER_KEYWORDS = re.compile(r'(?:barrier|strike|trigger):\s*([\d,]+\.?\d*)', re.IGNORECASE)

    @classmethod
    def extract_all(cls, text: str) -> dict:
        """
        Extract all matching patterns from text

        Returns:
            Dictionary of entity type -> list of matches
        """
        return {
            'isin': cls.ISIN.findall(text),
            'currency_amounts': cls.CURRENCY.findall(text),
            'dates': cls.DATE.findall(text),
            'percentages': cls.PERCENTAGE.findall(text),
            'notional': cls.NOTIONAL_KEYWORDS.findall(text),
            'coupon': cls.COUPON_KEYWORDS.findall(text),
            'maturity': cls.MATURITY_KEYWORDS.findall(text),
            'counterparty': cls.COUNTERPARTY_KEYWORDS.findall(text),
            'underlying': cls.UNDERLYING_KEYWORDS.findall(text),
            'barrier': cls.BARRIER_KEYWORDS.findall(text),
        }
