"""Módulo para busca e processamento de dados financeiros."""

import streamlit as st
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(ticker: str, period: str = '1y') -> Optional[pd.DataFrame]:
    """
    Busca dados históricos de uma ação.
    
    Args:
        ticker: Símbolo da ação
        period: Período dos dados (1mo, 3mo, 6mo, 1y, 2y, 5y, max)
        
    Returns:
        DataFrame com dados históricos ou None em caso de erro
    """
    try:
        # Download com auto_adjust=True para evitar multi-index
        data = yf.download(
            ticker, 
            period=period, 
            progress=False,
            auto_adjust=True,
            threads=False
        )
        
        if data.empty:
            logger.warning(f"Nenhum dado encontrado para {ticker}")
            return None
        
        # Se ainda tiver multi-index, flatten
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        # Garantir que o índice seja datetime
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        
        # Adicionar coluna Adj Close se não existir
        if 'Adj Close' not in data.columns and 'Close' in data.columns:
            data['Adj Close'] = data['Close']
        
        return data
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados para {ticker}: {str(e)}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_multiple_stocks(tickers: List[str], period: str = '1y') -> Dict[str, pd.DataFrame]:
    """
    Busca dados de múltiplas ações.
    
    Args:
        tickers: Lista de símbolos de ações
        period: Período dos dados
        
    Returns:
        Dicionário com ticker como chave e DataFrame como valor
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ticker = {
            executor.submit(fetch_stock_data, ticker, period): ticker 
            for ticker in tickers
        }
        
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                data = future.result()
                if data is not None and not data.empty:
                    results[ticker] = data
            except Exception as e:
                logger.error(f"Erro ao processar {ticker}: {str(e)}")
                
    return results


@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_info(ticker: str) -> Optional[Dict]:
    """
    Obtém informações detalhadas sobre uma ação.
    
    Args:
        ticker: Símbolo da ação
        
    Returns:
        Dicionário com informações da ação ou None
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Adicionar dividend yield se não existir
        if 'dividendYield' not in info or info['dividendYield'] is None:
            # Tentar calcular manualmente
            dividends = stock.dividends
            if not dividends.empty and 'currentPrice' in info:
                ultimo_ano_dividendos = dividends.last('1Y').sum()
                preco_atual = info.get('currentPrice', info.get('regularMarketPrice', 0))
                if preco_atual > 0:
                    info['dividendYield'] = ultimo_ano_dividendos / preco_atual
        
        return info
    except Exception as e:
        logger.error(f"Erro ao obter informações de {ticker}: {str(e)}")
        return None


def normalize_prices(data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Normaliza preços de múltiplas ações para comparação.
    
    Args:
        data_dict: Dicionário com ticker e DataFrame
        
    Returns:
        DataFrame com preços normalizados (base 100)
    """
    normalized = pd.DataFrame()
    
    for ticker, data in data_dict.items():
        if not data.empty and 'Close' in data.columns:
            close_series = pd.to_numeric(data['Close'], errors='coerce')
            first_value = close_series.iloc[0]
            if pd.notna(first_value) and first_value != 0:
                normalized[ticker] = (close_series / first_value) * 100
            
    return normalized
