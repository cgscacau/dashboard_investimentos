"""
Utilitários do Dashboard de Investimentos.

Este pacote contém funções auxiliares para:
- Busca e processamento de dados financeiros
- Cálculo de indicadores técnicos
- Normalização e transformação de dados
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
    'get_signal_interpretation'
]

__version__ = '2.0.0'

