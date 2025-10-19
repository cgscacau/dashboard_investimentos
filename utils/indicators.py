"""Módulo para cálculo de indicadores técnicos."""

import pandas as pd
import pandas_ta as ta
import streamlit as st
from typing import Dict, Optional


@st.cache_data(ttl=3600, show_spinner=False)
def calculate_all_indicators(data: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    Calcula todos os indicadores técnicos.
    
    Args:
        data: DataFrame com dados OHLCV
        
    Returns:
        Dicionário com indicadores calculados
    """
    if data.empty or 'Close' not in data.columns:
        return {}
    
    indicators = {}
    
    try:
        # RSI
        indicators['RSI'] = ta.rsi(data['Close'], length=14)
        
        # MACD
        macd = ta.macd(data['Close'])
        if macd is not None and not macd.empty:
            indicators['MACD'] = macd['MACD_12_26_9']
            indicators['MACD_signal'] = macd['MACDs_12_26_9']
            indicators['MACD_hist'] = macd['MACDh_12_26_9']
        
        # Bandas de Bollinger
        bbands = ta.bbands(data['Close'], length=20)
        if bbands is not None and not bbands.empty:
            indicators['BB_upper'] = bbands['BBU_20_2.0']
            indicators['BB_middle'] = bbands['BBM_20_2.0']
            indicators['BB_lower'] = bbands['BBL_20_2.0']
        
        # Médias Móveis
        indicators['SMA_20'] = ta.sma(data['Close'], length=20)
        indicators['SMA_50'] = ta.sma(data['Close'], length=50)
        indicators['SMA_200'] = ta.sma(data['Close'], length=200)
        indicators['EMA_12'] = ta.ema(data['Close'], length=12)
        indicators['EMA_26'] = ta.ema(data['Close'], length=26)
        
        # Volume médio
        if 'Volume' in data.columns:
            indicators['Volume_SMA'] = ta.sma(data['Volume'], length=20)
        
    except Exception as e:
        st.warning(f"Erro ao calcular alguns indicadores: {str(e)}")
    
    return indicators


def calculate_rsi(data: pd.DataFrame, length: int = 14) -> Optional[pd.Series]:
    """Calcula o RSI."""
    try:
        return ta.rsi(data['Close'], length=length)
    except Exception:
        return None


def calculate_macd(data: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Calcula o MACD."""
    try:
        return ta.macd(data['Close'])
    except Exception:
        return None


def calculate_bollinger_bands(data: pd.DataFrame, length: int = 20) -> Optional[pd.DataFrame]:
    """Calcula as Bandas de Bollinger."""
    try:
        return ta.bbands(data['Close'], length=length)
    except Exception:
        return None


def get_signal_interpretation(indicators: Dict[str, pd.Series]) -> Dict[str, str]:
    """
    Interpreta os indicadores e gera sinais de compra/venda.
    
    Args:
        indicators: Dicionário com indicadores calculados
        
    Returns:
        Dicionário com interpretações dos sinais
    """
    signals = {}
    
    # RSI
    if 'RSI' in indicators and not indicators['RSI'].empty:
        last_rsi = indicators['RSI'].iloc[-1]
        if last_rsi < 30:
            signals['RSI'] = "🟢 Sobrevendido - Possível sinal de compra"
        elif last_rsi > 70:
            signals['RSI'] = "🔴 Sobrecomprado - Possível sinal de venda"
        else:
            signals['RSI'] = "🟡 Neutro"
    
    # MACD
    if 'MACD' in indicators and 'MACD_signal' in indicators:
        last_macd = indicators['MACD'].iloc[-1]
        last_signal = indicators['MACD_signal'].iloc[-1]
        
        if last_macd > last_signal:
            signals['MACD'] = "🟢 MACD acima do sinal - Tendência de alta"
        else:
            signals['MACD'] = "🔴 MACD abaixo do sinal - Tendência de baixa"
    
    # Médias Móveis
    if 'SMA_20' in indicators and 'SMA_50' in indicators:
        last_sma20 = indicators['SMA_20'].iloc[-1]
        last_sma50 = indicators['SMA_50'].iloc[-1]
        
        if last_sma20 > last_sma50:
            signals['SMA'] = "🟢 SMA 20 acima da SMA 50 - Tendência de alta"
        else:
            signals['SMA'] = "🔴 SMA 20 abaixo da SMA 50 - Tendência de baixa"
    
    return signals
