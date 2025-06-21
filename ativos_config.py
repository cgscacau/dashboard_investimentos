# ativos_config.py
# Este arquivo serve como um "banco de dados" de consulta para as listas
# dos principais ativos dos mercados brasileiro e americano.

# Componentes do Ibovespa (aproximadamente 90 ativos)
# Fonte: B3, carteira teórica do IBOV.
IBOVESPA_TICKERS = [
    'RRRP3', 'ALPA4', 'ABEV3', 'AMER3', 'ASAI3', 'AZUL4', 'B3SA3', 'BIDI11',
    'BPAN4', 'BBSE3', 'BRML3', 'BBDC3', 'BBDC4', 'BRAP4', 'BBAS3', 'BRKM5',
    'BRFS3', 'BPAC11', 'CRFB3', 'CCRO3', 'CMIG4', 'CIEL3', 'COGN3', 'CPLE6',
    'CSAN3', 'CPFE3', 'CMIN3', 'CVCB3', 'CYRE3', 'DXCO3', 'ECOR3', 'ELET3',
    'ELET6', 'EMBR3', 'ENBR3', 'ENGI11', 'ENEV3', 'EGIE3', 'EQTL3', 'EZTC3',
    'FLRY3', 'GGBR4', 'GOAU4', 'GOLL4', 'NTCO3', 'SOMA3', 'HAPV3', 'HYPE3',
    'IGTI11', 'IRBR3', 'ITSA4', 'ITUB4', 'JBSS3', 'JHSF3', 'KLBN11', 'RENT3',
    'LWSA3', 'LREN3', 'MGLU3', 'MRFG3', 'CASH3', 'BEEF3', 'MRVE3', 'MULT3',
    'PCAR3', 'PETR3', 'PETR4', 'PRIO3', 'PETZ3', 'POSI3', 'QUAL3', 'RADL3',
    'RAIZ4', 'RDOR3', 'RAIL3', 'SBSP3', 'SANB11', 'SMTO3', 'CSNA3', 'SLCE3',
    'SUZB3', 'TAEE11', 'VIVT3', 'TIMS3', 'TOTS3', 'UGPA3', 'USIM5', 'VALE3',
    'VIIA3', 'VBBR3', 'WEGE3', 'YDUQ3'
]

# Componentes do S&P 100 (as 100 maiores empresas dos EUA)
# Fonte: Wikipedia / S&P Dow Jones Indices
SP100_TICKERS = [
    'AAPL', 'ABBV', 'ABT', 'ACN', 'ADBE', 'AIG', 'AMD', 'AMGN', 'AMT', 'AMZN',
    'AVGO', 'AXP', 'BA', 'BAC', 'BK', 'BKNG', 'BLK', 'BMY', 'BRK-B', 'C',
    'CAT', 'CHTR', 'CL', 'CMCSA', 'COF', 'COP', 'COST', 'CRM', 'CSCO', 'CVS',
    'CVX', 'D', 'DE', 'DHR', 'DIS', 'DOW', 'DUK', 'EMR', 'EXC', 'F', 'FDX',
    'GD', 'GE', 'GILD', 'GM', 'GOOG', 'GOOGL', 'GS', 'HD', 'HON', 'IBM',
    'INTC', 'JNJ', 'JPM', 'KHC', 'KO', 'LIN', 'LLY', 'LMT', 'LOW', 'MA',
    'MCD', 'MDLZ', 'MDT', 'META', 'MMM', 'MO', 'MRK', 'MS', 'MSFT', 'NEE',
    'NFLX', 'NKE', 'NOW', 'NVDA', 'ORCL', 'PEP', 'PFE', 'PG', 'PM', 'PYPL',
    'QCOM', 'RTX', 'SBUX', 'SCHW', 'SO', 'SPG', 'T', 'TGT', 'TMO',
    'TMUS', 'TSLA', 'TXN', 'UNH', 'UNP', 'UPS', 'USB', 'V', 'VZ', 'WBA',
    'WFC', 'WMT', 'XOM'
]

# ativos_config.py (adicionar ao final do arquivo)

# Lista curada de empresas brasileiras conhecidas por serem boas pagadoras de dividendos
BRAZIL_DIVIDEND_STOCKS = [
    'TAEE11', 'BBSE3', 'TRPL4', 'CMIG4', 'PETR4', 'VALE3', 'BBAS3', 'ITSA4',
    'EGIE3', 'CPLE6', 'SBSP3', 'SAPR4', 'CSMG3', 'AESB3', 'ALUP11', 'GGBR4',
    'CSNA3', 'UNIP6', 'BRAP4', 'CPFE3'
]

# ativos_config.py (adicionar ao final do arquivo)

# Lista curada de empresas americanas conhecidas por serem boas pagadoras de dividendos
# (baseado em Dividend Aristocrats e outras blue chips)
US_DIVIDEND_STOCKS = [
    'KO', 'PEP', 'PG', 'JNJ', 'MMM', 'CL', 'KMB', 'MCD', 'WMT', 'T',
    'VZ', 'IBM', 'XOM', 'CVX', 'ABBV', 'MO', 'PM', 'HD', 'LOW', 'NEE',
    'DUK', 'SO', 'O', 'SPG', 'AMT', 'CAT'
]