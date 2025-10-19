"""Configurações centralizadas do dashboard."""

class Config:
    """Classe de configuração do aplicativo."""
    
    PERIODOS = {
        '1 mês': '1mo',
        '3 meses': '3mo',
        '6 meses': '6mo',
        '1 ano': '1y',
        '2 anos': '2y',
        '5 anos': '5y',
        'Máximo': 'max'
    }
    
    INDICADORES_TECNICOS = [
        'RSI',
        'MACD',
        'Bandas de Bollinger',
        'Médias Móveis (SMA/EMA)',
        'Volume'
    ]
    
    CACHE_TTL = 3600  # 1 hora em segundos
    
    TICKERS_BRASILEIROS_POPULARES = [
        'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 
        'ABEV3.SA', 'B3SA3.SA', 'MGLU3.SA', 'WEGE3.SA',
        'RENT3.SA', 'GGBR4.SA'
    ]
    
    TICKERS_INTERNACIONAIS_POPULARES = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
        'META', 'NVDA', 'JPM', 'V', 'WMT'
    ]
    
    # Setores em português
    SETORES_PORTUGUES = {
        'Technology': 'Tecnologia',
        'Financial Services': 'Serviços Financeiros',
        'Healthcare': 'Saúde',
        'Consumer Cyclical': 'Consumo Cíclico',
        'Consumer Defensive': 'Consumo Defensivo',
        'Industrials': 'Industrial',
        'Energy': 'Energia',
        'Basic Materials': 'Materiais Básicos',
        'Real Estate': 'Imobiliário',
        'Communication Services': 'Serviços de Comunicação',
        'Utilities': 'Utilidades Públicas'
    }
