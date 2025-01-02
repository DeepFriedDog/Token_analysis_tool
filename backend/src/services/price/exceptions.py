class PriceDataError(Exception):
    """Custom exception for price data fetching errors"""
    def __init__(self, message: str, source: str, status_code: int = None):
        self.message = message
        self.source = source
        self.status_code = status_code
        super().__init__(self.message) 