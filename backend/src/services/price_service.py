from decimal import Decimal, InvalidOperation, ROUND_DOWN

class PriceService:
    def calculate_technical_indicators(self, df):
        try:
            # Convert price data to Decimal
            prices = [Decimal(str(price)).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN) 
                     for price in df['close']]
            
            # Calculate support and resistance levels
            support_levels = [Decimal(str(level)).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN) 
                            for level in self._find_support_levels(prices)]
            
            resistance_levels = [Decimal(str(level)).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN) 
                               for level in self._find_resistance_levels(prices)]
            
            # Calculate RSI
            rsi = Decimal(str(self._calculate_rsi(prices))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            
            # Calculate volatility
            volatility = Decimal(str(self._calculate_volatility(prices))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            
            # Calculate Fibonacci levels
            fib_levels = self._calculate_fibonacci_levels(prices)
            
            return {
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'rsi': rsi,
                'volatility': volatility,
                'fibonacci_levels': fib_levels,
                'advanced_indicators': self._calculate_advanced_indicators(df)
            }
            
        except InvalidOperation as e:
            print(f"[Price Service] ❌ Decimal conversion error: {str(e)}")
            # Return safe default values
            return {
                'support_levels': [],
                'resistance_levels': [],
                'rsi': Decimal('50.0'),
                'volatility': Decimal('0.0'),
                'fibonacci_levels': [],
                'advanced_indicators': {
                    'macd': None,
                    'bollinger_bands': None,
                    'rsi': Decimal('50.0')
                }
            } 