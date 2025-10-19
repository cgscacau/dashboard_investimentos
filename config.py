# config.py
class Config:
    PERIODOS = {
        '1 mês': '1mo',
        '3 meses': '3mo',
        '6 meses': '6mo',
        '1 ano': '1y',
        '2 anos': '2y',
        '5 anos': '5y',
        'Máximo': 'max'
    }
    
    INDICADORES_TECNICOS = ['RSI', 'MACD', 'Bollinger Bands', 'SMA', 'EMA']
    
    CACHE_TTL = 3600  # 1 hora
