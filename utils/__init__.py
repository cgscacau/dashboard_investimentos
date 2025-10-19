"""
Utilitários do Dashboard de Investimentos.
"""

from .data_fetcher import (
    fetch_stock_data,
    fetch_multiple_stocks,
    get_stock_info,
    normalize_prices
)

from .indicators import (
    calculate_all_indicators,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    get_signal_interpretation
)

from .formatters import (
    formatar_moeda,
    formatar_percentual,
    traduzir_setor,
    formatar_numero_grande
)

__all__ = [
    # Data fetching
    'fetch_stock_data',
    'fetch_multiple_stocks',
    'get_stock_info',
    'normalize_prices',
    
    # Indicators
    'calculate_all_indicators',
    'calculate_rsi',
    'calculate_macd',
    'calculate_bollinger_bands',
    'get_signal_interpretation',
    
    # Formatters
    'formatar_moeda',
    'formatar_percentual',
    'traduzir_setor',
    'formatar_numero_grande'
]

__version__ = '2.0.0'
