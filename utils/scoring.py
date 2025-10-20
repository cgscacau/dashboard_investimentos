"""Sistema de pontuação e ranking de ativos."""

import pandas as pd
import numpy as np
from config import Config


def calcular_score_ativo(dados, info=None):
    """
    Calcula o score total de um ativo baseado em múltiplos critérios.
    
    Args:
        dados: DataFrame com dados históricos
        info: Dicionário com informações fundamentalistas (opcional)
        
    Returns:
        Dict com scores individuais e score total
    """
    if dados.empty or len(dados) < 20:
        return None
    
    scores = {}
    
    try:
        # 1. Score de Retorno (0-100)
        retorno = ((dados['Close'].iloc[-1] - dados['Close'].iloc[0]) / dados['Close'].iloc[0]) * 100
        scores['retorno'] = normalizar_score(retorno, -50, 100)
        scores['retorno_valor'] = retorno
        
        # 2. Score de Volatilidade (0-100, menor é melhor)
        retornos = dados['Close'].pct_change().dropna()
        volatilidade = retornos.std() * np.sqrt(252) * 100
        scores['volatilidade'] = 100 - normalizar_score(volatilidade, 0, 100)
        scores['volatilidade_valor'] = volatilidade
        
        # 3. Score de Sharpe Ratio (0-100)
        retorno_medio = retornos.mean() * 252
        sharpe = (retorno_medio - 0.10) / (volatilidade / 100) if volatilidade > 0 else 0
        scores['sharpe'] = normalizar_score(sharpe, -2, 4)
        scores['sharpe_valor'] = sharpe
        
        # 4. Score de Tendência (0-100)
        sma_20 = dados['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = dados['Close'].rolling(window=50).mean().iloc[-1] if len(dados) >= 50 else sma_20
        preco_atual = dados['Close'].iloc[-1]
        
        tendencia_score = 0
        if preco_atual > sma_20:
            tendencia_score += 50
        if preco_atual > sma_50:
            tendencia_score += 50
        
        scores['tendencia'] = tendencia_score
        scores['tendencia_sinal'] = "Alta" if tendencia_score >= 75 else "Baixa" if tendencia_score <= 25 else "Neutra"
        
        # 5. Score de Momentum/RSI (0-100)
        delta = dados['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_atual = rsi.iloc[-1]
        
        # RSI ideal entre 40-60
        if 40 <= rsi_atual <= 60:
            momento_score = 100
        elif 30 <= rsi_atual < 40 or 60 < rsi_atual <= 70:
            momento_score = 70
        elif rsi_atual < 30 or rsi_atual > 70:
            momento_score = 40
        else:
            momento_score = 50
        
        scores['momento'] = momento_score
        scores['rsi_valor'] = rsi_atual
        
        # 6. Score Total Ponderado
        pesos = Config.PESOS_RANKING
        score_total = (
            scores['retorno'] * pesos['retorno'] +
            scores['volatilidade'] * pesos['volatilidade'] +
            scores['sharpe'] * pesos['sharpe'] +
            scores['tendencia'] * pesos['tendencia'] +
            scores['momento'] * pesos['momento']
        )
        
        scores['total'] = round(score_total, 2)
        
        # 7. Classificação
        if score_total >= 80:
            scores['classificacao'] = "⭐⭐⭐⭐⭐ Excelente"
            scores['cor'] = "#10b981"
        elif score_total >= 70:
            scores['classificacao'] = "⭐⭐⭐⭐ Muito Bom"
            scores['cor'] = "#22c55e"
        elif score_total >= 60:
            scores['classificacao'] = "⭐⭐⭐ Bom"
            scores['cor'] = "#84cc16"
        elif score_total >= 50:
            scores['classificacao'] = "⭐⭐ Regular"
            scores['cor'] = "#eab308"
        else:
            scores['classificacao'] = "⭐ Fraco"
            scores['cor'] = "#ef4444"
        
        return scores
        
    except Exception as e:
        return None


def normalizar_score(valor, min_val, max_val):
    """
    Normaliza um valor para escala 0-100.
    
    Args:
        valor: Valor a normalizar
        min_val: Valor mínimo esperado
        max_val: Valor máximo esperado
        
    Returns:
        Score normalizado entre 0 e 100
    """
    if valor <= min_val:
        return 0
    elif valor >= max_val:
        return 100
    else:
        return ((valor - min_val) / (max_val - min_val)) * 100


def rankear_ativos(lista_tickers, periodo='1y', progresso_callback=None):
    """
    Rankeia uma lista de ativos baseado em seus scores.
    
    Args:
        lista_tickers: Lista de códigos de ativos
        periodo: Período de análise
        progresso_callback: Função callback para atualizar progresso
        
    Returns:
        DataFrame com ranking completo
    """
    from utils.data_fetcher import fetch_stock_data, get_stock_info
    
    resultados = []
    total = len(lista_tickers)
    
    for i, ticker in enumerate(lista_tickers):
        if progresso_callback:
            progresso_callback(i + 1, total, ticker)
        
        try:
            # Buscar dados
            dados = fetch_stock_data(ticker, periodo)
            
            if dados is None or dados.empty:
                continue
            
            # Calcular score
            scores = calcular_score_ativo(dados)
            
            if scores is None:
                continue
            
            # Buscar informações adicionais
            info = get_stock_info(ticker)
            
            # Montar resultado
            resultado = {
                'ticker': ticker,
                'nome': info.get('longName', ticker) if info else ticker,
                'setor': info.get('sector', 'N/A') if info else 'N/A',
                'preco': float(dados['Close'].iloc[-1]),
                'score_total': scores['total'],
                'classificacao': scores['classificacao'],
                'cor': scores['cor'],
                'retorno': scores['retorno_valor'],
                'volatilidade': scores['volatilidade_valor'],
                'sharpe': scores['sharpe_valor'],
                'tendencia': scores['tendencia_sinal'],
                'rsi': scores['rsi_valor'],
                'score_retorno': scores['retorno'],
                'score_volatilidade': scores['volatilidade'],
                'score_sharpe': scores['sharpe'],
                'score_tendencia': scores['tendencia'],
                'score_momento': scores['momento']
            }
            
            resultados.append(resultado)
            
        except Exception as e:
            continue
    
    # Criar DataFrame e ordenar
    if not resultados:
        return pd.DataFrame()
    
    df = pd.DataFrame(resultados)
    df = df.sort_values('score_total', ascending=False).reset_index(drop=True)
    df['ranking'] = range(1, len(df) + 1)
    
    return df

