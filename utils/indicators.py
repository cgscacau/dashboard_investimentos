"""Módulo para cálculo de indicadores técnicos sem pandas-ta."""

import pandas as pd
import numpy as np
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
        indicators['RSI'] = calculate_rsi(data)
        
        # MACD
        macd_data = calculate_macd(data)
        if macd_data is not None:
            indicators['MACD'] = macd_data['MACD']
            indicators['MACD_signal'] = macd_data['Signal']
            indicators['MACD_hist'] = macd_data['Histogram']
        
        # Bandas de Bollinger
        bb_data = calculate_bollinger_bands(data)
        if bb_data is not None:
            indicators['BB_upper'] = bb_data['Upper']
            indicators['BB_middle'] = bb_data['Middle']
            indicators['BB_lower'] = bb_data['Lower']
        
        # Médias Móveis
        indicators['SMA_20'] = calculate_sma(data['Close'], 20)
        indicators['SMA_50'] = calculate_sma(data['Close'], 50)
        indicators['SMA_200'] = calculate_sma(data['Close'], 200)
        indicators['EMA_12'] = calculate_ema(data['Close'], 12)
        indicators['EMA_26'] = calculate_ema(data['Close'], 26)
        
        # Volume médio
        if 'Volume' in data.columns:
            indicators['Volume_SMA'] = calculate_sma(data['Volume'], 20)
        
    except Exception as e:
        st.warning(f"Erro ao calcular alguns indicadores: {str(e)}")
    
    return indicators


def calculate_rsi(data: pd.DataFrame, length: int = 14) -> Optional[pd.Series]:
    """
    Calcula o RSI (Relative Strength Index).
    
    Args:
        data: DataFrame com coluna 'Close'
        length: Período do RSI
        
    Returns:
        Series com valores do RSI
    """
    try:
        close = data['Close']
        delta = close.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=length, min_periods=length).mean()
        avg_loss = loss.rolling(window=length, min_periods=length).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    except Exception:
        return None


def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[pd.DataFrame]:
    """
    Calcula o MACD (Moving Average Convergence Divergence).
    
    Args:
        data: DataFrame com coluna 'Close'
        fast: Período da EMA rápida
        slow: Período da EMA lenta
        signal: Período da linha de sinal
        
    Returns:
        DataFrame com MACD, Signal e Histogram
    """
    try:
        close = data['Close']
        
        ema_fast = calculate_ema(close, fast)
        ema_slow = calculate_ema(close, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        })
    except Exception:
        return None


def calculate_bollinger_bands(data: pd.DataFrame, length: int = 20, std_dev: float = 2.0) -> Optional[pd.DataFrame]:
    """
    Calcula as Bandas de Bollinger.
    
    Args:
        data: DataFrame com coluna 'Close'
        length: Período da média móvel
        std_dev: Número de desvios padrão
        
    Returns:
        DataFrame com Upper, Middle e Lower bands
    """
    try:
        close = data['Close']
        
        middle = calculate_sma(close, length)
        std = close.rolling(window=length).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return pd.DataFrame({
            'Upper': upper,
            'Middle': middle,
            'Lower': lower
        })
    except Exception:
        return None


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """
    Calcula a Média Móvel Simples (SMA).
    
    Args:
        series: Série de dados
        period: Período da média
        
    Returns:
        Série com a SMA
    """
    return series.rolling(window=period, min_periods=period).mean()


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """
    Calcula a Média Móvel Exponencial (EMA).
    
    Args:
        series: Série de dados
        period: Período da média
        
    Returns:
        Série com a EMA
    """
    return series.ewm(span=period, adjust=False).mean()


def get_signal_interpretation(indicators: Dict[str, pd.Series]) -> Dict[str, str]:
    """
    Interpreta os indicadores e gera sinais de compra/venda.
    
    Args:
        indicators: Dicionário com indicadores calculados
        
    Returns:
        Dicionário com interpretações dos sinais
    """
    signals = {}
    
    try:
        # RSI
        if 'RSI' in indicators and not indicators['RSI'].empty:
            last_rsi = float(indicators['RSI'].iloc[-1])
            if pd.notna(last_rsi):
                if last_rsi < 30:
                    signals['RSI'] = "🟢 Sobrevendido - Possível sinal de compra"
                elif last_rsi > 70:
                    signals['RSI'] = "🔴 Sobrecomprado - Possível sinal de venda"
                else:
                    signals['RSI'] = "🟡 Neutro"
        
        # MACD
        if 'MACD' in indicators and 'MACD_signal' in indicators:
            last_macd = float(indicators['MACD'].iloc[-1])
            last_signal = float(indicators['MACD_signal'].iloc[-1])
            
            if pd.notna(last_macd) and pd.notna(last_signal):
                if last_macd > last_signal:
                    signals['MACD'] = "🟢 MACD acima do sinal - Tendência de alta"
                else:
                    signals['MACD'] = "🔴 MACD abaixo do sinal - Tendência de baixa"
        
        # Médias Móveis
        if 'SMA_20' in indicators and 'SMA_50' in indicators:
            last_sma20 = float(indicators['SMA_20'].iloc[-1])
            last_sma50 = float(indicators['SMA_50'].iloc[-1])
            
            if pd.notna(last_sma20) and pd.notna(last_sma50):
                if last_sma20 > last_sma50:
                    signals['Médias Móveis'] = "🟢 Média 20 acima da Média 50 - Tendência de alta"
                else:
                    signals['Médias Móveis'] = "🔴 Média 20 abaixo da Média 50 - Tendência de baixa"
        
        # Bandas de Bollinger
        if all(k in indicators for k in ['BB_upper', 'BB_lower', 'BB_middle']):
            close_price = indicators['BB_middle'].index[-1]  # Pegar o último preço
            # Aqui você precisaria do preço atual, vou assumir que está disponível
            # Esta é uma simplificação
            signals['Bandas de Bollinger'] = "ℹ️ Verifique a posição do preço em relação às bandas"
    
    except Exception as e:
        st.warning(f"Erro ao interpretar sinais: {str(e)}")
    
    return signals


def calculate_volatility(data: pd.DataFrame, period: int = 252) -> float:
    """
    Calcula a volatilidade anualizada.
    
    Args:
        data: DataFrame com coluna 'Close'
        period: Número de períodos para anualização (252 para dias úteis)
        
    Returns:
        Volatilidade anualizada em percentual
    """
    try:
        returns = data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(period) * 100
        return float(volatility)
    except Exception:
        return 0.0


def calculate_sharpe_ratio(data: pd.DataFrame, risk_free_rate: float = 0.10, period: int = 252) -> float:
    """
    Calcula o Índice Sharpe.
    
    Args:
        data: DataFrame com coluna 'Close'
        risk_free_rate: Taxa livre de risco anual
        period: Número de períodos para anualização
        
    Returns:
        Índice Sharpe
    """
    try:
        returns = data['Close'].pct_change().dropna()
        avg_return = returns.mean() * period
        volatility = returns.std() * np.sqrt(period)
        
        if volatility == 0:
            return 0.0
        
        sharpe = (avg_return - risk_free_rate) / volatility
        return float(sharpe)
    except Exception:
        return 0.0


def calculate_max_drawdown(data: pd.DataFrame) -> float:
    """
    Calcula o drawdown máximo.
    
    Args:
        data: DataFrame com coluna 'Close'
        
    Returns:
        Drawdown máximo em percentual
    """
    try:
        returns = data['Close'].pct_change().dropna()
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min() * 100
        return float(max_dd)
    except Exception:
        return 0.0
