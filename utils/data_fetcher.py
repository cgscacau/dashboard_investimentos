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
        data = yf.download(ticker, period=period, progress=False)
        
        if data.empty:
            logger.warning(f"Nenhum dado encontrado para {ticker}")
            return None
            
        # Garantir que o índice seja datetime
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
            
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
                if data is not None:
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
            normalized[ticker] = (data['Close'] / data['Close'].iloc[0]) * 100
            
    return normalized
