"""Configurações centralizadas do dashboard."""

class Config:
    """Classe de configuração do aplicativo."""
    
    PERIODOS = {
        '1 mês': '1mo',
        '3 meses': '3mo',
        '6 meses': '6mo',
        '1 ano': '1y',
        '2 anos': '2y',
        '5 anos': '5y'
    }
    
    # Ações Brasileiras para análise
    ACOES_BRASILEIRAS = [
        'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA',
        'B3SA3.SA', 'MGLU3.SA', 'WEGE3.SA', 'RENT3.SA', 'GGBR4.SA',
        'SUZB3.SA', 'RAIL3.SA', 'VIVT3.SA', 'JBSS3.SA', 'RADL3.SA',
        'EMBR3.SA', 'CSAN3.SA', 'TOTS3.SA', 'PRIO3.SA', 'KLBN11.SA'
    ]
    
    # Ações Internacionais para análise
    ACOES_INTERNACIONAIS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
        'JPM', 'V', 'WMT', 'PG', 'JNJ', 'UNH', 'HD', 'MA',
        'DIS', 'NFLX', 'PYPL', 'ADBE', 'INTC'
    ]
    
    # Fundos/ETFs Brasileiros
    FUNDOS_BRASILEIROS = [
        'BOVA11.SA', 'IVVB11.SA', 'SMAL11.SA', 'HASH11.SA',
        'DIVO11.SA', 'XBOV11.SA', 'PIBB11.SA', 'ISUS11.SA',
        'BRAX11.SA', 'MATB11.SA'
    ]
    
    # ETFs Internacionais
    FUNDOS_INTERNACIONAIS = [
        'SPY', 'QQQ', 'VOO', 'IVV', 'VTI', 'DIA',
        'EEM', 'VEA', 'AGG', 'GLD'
    ]
    
    # Critérios de pontuação
    PESOS_RANKING = {
        'retorno': 0.30,           # 30% - Retorno no período
        'volatilidade': 0.20,      # 20% - Menor volatilidade é melhor
        'sharpe': 0.20,            # 20% - Índice Sharpe
        'tendencia': 0.15,         # 15% - Tendência (médias móveis)
        'momento': 0.15            # 15% - Momentum (RSI)
    }
    
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
