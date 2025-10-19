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
    calculate_sma,
    calculate_ema,
    get_signal_interpretation,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown
)

from .formatters import (
    formatar_moeda,
    formatar_percentual,
    traduzir_setor,
    formatar_numero_grande,
    obter_simbolo_moeda
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
    'calculate_sma',
    'calculate_ema',
    'get_signal_interpretation',
    'calculate_volatility',
    'calculate_sharpe_ratio',
    'calculate_max_drawdown',
    
    # Formatters
    'formatar_moeda',
    'formatar_percentual',
    'traduzir_setor',
    'formatar_numero_grande',
    'obter_simbolo_moeda'
]

__version__ = '2.0.0'
