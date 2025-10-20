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
    
    # ========== AÇÕES BRASILEIRAS (EXPANDIDO) ==========
    ACOES_BRASILEIRAS = [
        # Petróleo e Gás
        'PETR3.SA', 'PETR4.SA', 'PRIO3.SA', 'RRRP3.SA', 'RECV3.SA',
        
        # Mineração e Siderurgia
        'VALE3.SA', 'GGBR4.SA', 'CSNA3.SA', 'USIM5.SA', 'GOAU4.SA',
        
        # Bancos
        'ITUB4.SA', 'BBDC4.SA', 'BBAS3.SA', 'SANB11.SA', 'BPAC11.SA',
        
        # Varejo
        'MGLU3.SA', 'LREN3.SA', 'ARZZ3.SA', 'VIIA3.SA', 'BHIA3.SA',
        'SOMA3.SA', 'PETZ3.SA', 'CRFB3.SA', 'ASAI3.SA', 'PCAR3.SA',
        
        # Alimentos e Bebidas
        'ABEV3.SA', 'JBSS3.SA', 'BRFS3.SA', 'MRFG3.SA', 'BEEF3.SA',
        'SMTO3.SA', 'SLCE3.SA',
        
        # Energia Elétrica
        'ELET3.SA', 'ELET6.SA', 'ENBR3.SA', 'CMIG4.SA', 'CPFE3.SA',
        'TAEE11.SA', 'CPLE6.SA', 'NEOE3.SA', 'AURE3.SA',
        
        # Construção Civil
        'CYRE3.SA', 'MRVE3.SA', 'EZTC3.SA', 'TEND3.SA', 'JHSF3.SA',
        
        # Papel e Celulose
        'SUZB3.SA', 'KLBN11.SA', 'RANI3.SA',
        
        # Telecomunicações
        'VIVT3.SA', 'TIMS3.SA',
        
        # Transporte e Logística
        'RAIL3.SA', 'AZUL4.SA', 'GOLL4.SA', 'EMBR3.SA', 'CCRO3.SA',
        
        # Saúde
        'RADL3.SA', 'HAPV3.SA', 'FLRY3.SA', 'GNDI3.SA', 'QUAL3.SA',
        
        # Educação
        'COGN3.SA', 'YDUQ3.SA', 'ANIM3.SA',
        
        # Tecnologia
        'TOTS3.SA', 'LWSA3.SA', 'MELI34.SA',
        
        # Seguros
        'BBSE3.SA', 'CXSE3.SA', 'PSSA3.SA',
        
        # Shoppings
        'BRML3.SA', 'MULT3.SA', 'IGTI11.SA',
        
        # Saneamento
        'SBSP3.SA', 'SAPR11.SA', 'CSMG3.SA',
        
        # Agronegócio
        'SLCE3.SA', 'AGRO3.SA',
        
        # Diversos
        'B3SA3.SA', 'WEGE3.SA', 'RENT3.SA', 'CSAN3.SA', 'UGPA3.SA',
        'RAIZ4.SA', 'IRBR3.SA', 'NTCO3.SA', 'CVCB3.SA', 'LAME4.SA',
        'BRAP4.SA', 'EQTL3.SA', 'TRPL4.SA', 'IGTA3.SA', 'SULA11.SA'
    ]
    
    # ========== AÇÕES INTERNACIONAIS (EXPANDIDO) ==========
    ACOES_INTERNACIONAIS = [
        # Tecnologia - FAANG + Big Tech
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
        'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM',
        'AVGO', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'SNPS', 'CDNS',
        
        # Software e Cloud
        'NOW', 'SNOW', 'DDOG', 'CRWD', 'ZS', 'OKTA', 'WDAY',
        'TEAM', 'MNDY', 'HUBS', 'ZM', 'DOCU', 'TWLO', 'NET',
        
        # E-commerce e Fintech
        'SHOP', 'SQ', 'PYPL', 'COIN', 'HOOD', 'SOFI', 'AFRM',
        
        # Semicondutores
        'TSM', 'ASML', 'MU', 'NXPI', 'MRVL', 'ON',
        
        # Bancos e Financeiras
        'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'SCHW',
        'AXP', 'USB', 'PNC', 'TFC',
        
        # Saúde e Farmacêuticas
        'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY',
        'AMGN', 'GILD', 'CVS', 'CI', 'LLY', 'MRK', 'MDT',
        
        # Biotecnologia
        'MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'ILMN',
        
        # Consumo - Varejo
        'WMT', 'HD', 'TGT', 'LOW', 'COST', 'NKE', 'SBUX',
        'MCD', 'DIS', 'CMCSA', 'CHTR',
        
        # Bens de Consumo
        'PG', 'KO', 'PEP', 'CL', 'MDLZ', 'PM', 'MO', 'EL',
        
        # Energia
        'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'OXY',
        
        # Energia Renovável
        'NEE', 'ENPH', 'SEDG', 'RUN', 'FSLR',
        
        # Industrial
        'BA', 'CAT', 'DE', 'GE', 'HON', 'MMM', 'UPS', 'FDX',
        
        # Automotivo
        'F', 'GM', 'RIVN', 'LCID', 'NIO', 'LI', 'XPEV',
        
        # Telecomunicações
        'T', 'VZ', 'TMUS',
        
        # Mídia e Entretenimento
        'NFLX', 'DIS', 'PARA', 'WBD', 'SPOT', 'RBLX',
        
        # Imóveis (REITs)
        'AMT', 'PLD', 'EQIX', 'PSA', 'DLR', 'O', 'VICI',
        
        # Viagens e Lazer
        'ABNB', 'BKNG', 'MAR', 'HLT', 'RCL', 'CCL', 'UAL', 'DAL',
        
        # Pagamentos
        'V', 'MA', 'PYPL', 'SQ', 'FIS', 'FISV', 'ADP',
        
        # Defesa
        'LMT', 'RTX', 'NOC', 'GD', 'BA',
        
        # Commodities e Materiais
        'FCX', 'NEM', 'GOLD', 'NUE', 'STLD',
        
        # Utilidades
        'NEE', 'DUK', 'SO', 'D', 'AEP'
    ]
    
    # ========== FUNDOS E ETFs BRASILEIROS (EXPANDIDO) ==========
    FUNDOS_BRASILEIROS = [
        # Índices Amplos
        'BOVA11.SA',   # Ibovespa
        'SMAL11.SA',   # Small Caps
        'PIBB11.SA',   # IBrX-100
        'BRAX11.SA',   # Brasil Amplo
        'XBOV11.SA',   # Ibovespa
        
        # Dividendos
        'DIVO11.SA',   # Dividendos
        'NDIV11.SA',   # Dividendos
        'XFIX11.SA',   # Dividendos
        
        # Setoriais
        'FIND11.SA',   # Financeiro
        'MATB11.SA',   # Materiais Básicos
        'UTIL11.SA',   # Utilidades
        'ICON11.SA',   # Consumo
        'ISUS11.SA',   # Sustentabilidade
        'ECOO11.SA',   # Carbono
        
        # Internacional
        'HASH11.SA',   # NASDAQ
        'IVVB11.SA',   # S&P 500
        'WRLD11.SA',   # Global
        'ESGB11.SA',   # ESG Global
        'GOLD11.SA',   # Ouro
        
        # Renda Fixa
        'B5P211.SA',   # Títulos Públicos
        'IMAB11.SA',   # IMA-B
        'IB5M11.SA',   # IPCA 5 anos
        'FIXA11.SA',   # Renda Fixa
        
        # Imobiliário
        'HGLG11.SA',   # FII Logística
        'VISC11.SA',   # FII Shoppings
        'XPML11.SA',   # FII Multimercado
        'KNCR11.SA',   # FII Lajes Corporativas
        'MXRF11.SA',   # FII Renda
        'HGRU11.SA',   # FII Híbrido
        
        # Criptomoedas
        'QBTC11.SA',   # Bitcoin
        'ETHE11.SA',   # Ethereum
        'CRPT11.SA',   # Cripto Index
        
        # Multimercado
        'DEVA11.SA',   # Dólar
        'EURP11.SA'    # Euro
    ]
    
    # ========== ETFs INTERNACIONAIS (EXPANDIDO) ==========
    FUNDOS_INTERNACIONAIS = [
        # Índices Amplos EUA
        'SPY',    # S&P 500
        'VOO',    # S&P 500 (Vanguard)
        'IVV',    # S&P 500 (iShares)
        'QQQ',    # NASDAQ-100
        'DIA',    # Dow Jones
        'VTI',    # Total Stock Market
        'SCHB',   # Broad Market
        'ITOT',   # Total Market
        
        # Growth
        'VUG',    # Large Cap Growth
        'IWF',    # Russell 1000 Growth
        'VONG',   # Russell 1000 Growth
        'SCHG',   # Large Cap Growth
        
        # Value
        'VTV',    # Large Cap Value
        'IWD',    # Russell 1000 Value
        'VONV',   # Russell 1000 Value
        'SCHV',   # Large Cap Value
        
        # Small Cap
        'IWM',    # Russell 2000
        'VB',     # Small Cap
        'IJR',    # S&P Small Cap
        'SCHA',   # Small Cap
        
        # Mid Cap
        'IJH',    # S&P Mid Cap
        'VO',     # Mid Cap
        'MDY',    # Mid Cap SPDR
        
        # Setoriais
        'XLK',    # Technology
        'XLF',    # Financial
        'XLE',    # Energy
        'XLV',    # Healthcare
        'XLY',    # Consumer Discretionary
        'XLP',    # Consumer Staples
        'XLI',    # Industrial
        'XLB',    # Materials
        'XLU',    # Utilities
        'XLRE',   # Real Estate
        'XLC',    # Communication
        
        # Tecnologia Específicos
        'VGT',    # Tech
        'SOXX',   # Semiconductors
        'SMH',    # Semiconductors
        'HACK',   # Cybersecurity
        'CLOU',   # Cloud Computing
        'FINX',   # Fintech
        'ARKK',   # Innovation
        'ARKW',   # Next Gen Internet
        'ARKG',   # Genomics
        
        # Internacional
        'EEM',    # Emerging Markets
        'VWO',    # Emerging Markets
        'IEMG',   # Emerging Markets
        'VEA',    # Developed Markets
        'IEFA',   # Developed Markets
        'EFA',    # EAFE
        'VGK',    # Europe
        'EWJ',    # Japan
        'FXI',    # China
        'EWZ',    # Brazil
        'INDA',   # India
        
        # Bonds (Títulos)
        'AGG',    # Aggregate Bond
        'BND',    # Total Bond
        'TLT',    # 20+ Year Treasury
        'IEF',    # 7-10 Year Treasury
        'SHY',    # 1-3 Year Treasury
        'LQD',    # Corporate Bond
        'HYG',    # High Yield
        'EMB',    # Emerging Markets Bond
        
        # Commodities
        'GLD',    # Gold
        'SLV',    # Silver
        'USO',    # Oil
        'DBA',    # Agriculture
        'DBC',    # Commodities
        'PDBC',   # Commodities
        
        # Dividendos
        'VYM',    # High Dividend
        'SCHD',   # Dividend
        'DVY',    # Dividend
        'SDY',    # Dividend Aristocrats
        'NOBL',   # Dividend Aristocrats
        'VIG',    # Dividend Growth
        
        # ESG
        'ESGU',   # ESG USA
        'ESGD',   # ESG International
        'ESGE',   # ESG Emerging
        'SUSL',   # ESG Leaders
        
        # Específicos
        'ARKF',   # Fintech
        'ICLN',   # Clean Energy
        'TAN',    # Solar
        'LIT',    # Lithium
        'JETS',   # Airlines
        'XHB',    # Homebuilders
        'ITB',    # Homebuilders
        'XRT',    # Retail
        'BOTZ',   # Robotics
        'ROBO',   # Robotics
        'DRIV',   # Autonomous Vehicles
        'ESPO',   # Gaming
        'NERD'    # Gaming
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
        'Utilities': 'Utilidades Públicas',
        'Financial': 'Financeiro',
        'Consumer Discretionary': 'Consumo Discricionário',
        'Consumer Staples': 'Consumo Básico',
        'Information Technology': 'Tecnologia da Informação'
    }
