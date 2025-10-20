"""Módulo de comparação entre múltiplos ativos."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config import Config
from utils.data_fetcher import fetch_multiple_stocks, normalize_prices
from utils.formatters import formatar_moeda, formatar_percentual, obter_simbolo_moeda


def show():
    """Exibe a página de comparação."""
    
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; background: white; border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>⚖️</div>
            <h1 style='margin: 0; font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                Comparação de Ativos
            </h1>
            <p style='color: #64748b; font-size: 1.1rem; margin-top: 0.5rem;'>
                Compare múltiplos ativos lado a lado
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    **Como usar:**
    - Digite os códigos dos ativos separados por vírgula
    - Use .SA para ações brasileiras (ex: PETR4.SA, VALE3.SA)
    - Máximo de 5 ativos por comparação
    """)
    
    # Controles
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        tickers_input = st.text_input(
            "📊 Digite os códigos (separados por vírgula):",
            value="PETR4.SA, VALE3.SA, ITUB4.SA",
            help="Ex: PETR4.SA, VALE3.SA, ITUB4.SA",
            key="input_comparacao_tickers"
        )
    
    with col2:
        periodo_label = st.selectbox(
            "📅 Período:",
            list(Config.PERIODOS.keys()),
            index=3,
            key="select_comparacao_periodo"
        )
        periodo = Config.PERIODOS[periodo_label]
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        comparar = st.button("⚖️ Comparar", use_container_width=True, type="primary")
    
    # Checkbox para normalização
    normalizar = st.checkbox(
        "📈 Normalizar preços (base 100)",
        value=True,
        help="Facilita a comparação de ativos com preços muito diferentes"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Processar tickers
    tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
    
    if not tickers:
        st.warning("⚠️ Por favor, insira pelo menos um código de ativo.")
        return
    
    if len(tickers) > 5:
        st.warning("⚠️ Máximo de 5 ativos por comparação. Usando apenas os 5 primeiros.")
        tickers = tickers[:5]
    
    # Executar comparação
    if comparar or 'dados_comparacao' in st.session_state:
        if comparar:
            with st.spinner(f'🔄 Carregando dados de {len(tickers)} ativos...'):
                # Barra de progresso
                progresso_bar = st.progress(0)
                
                dados_dict = {}
                for i, ticker in enumerate(tickers):
                    from utils.data_fetcher import fetch_stock_data
                    dados = fetch_stock_data(ticker, periodo)
                    if dados is not None and not dados.empty:
                        dados_dict[ticker] = dados
                    progresso_bar.progress((i + 1) / len(tickers))
                
                progresso_bar.empty()
                
                if not dados_dict:
                    st.error("❌ Não foi possível obter dados para nenhum dos ativos informados.")
                    return
                
                st.session_state.dados_comparacao = dados_dict
                st.session_state.tickers_comparacao = list(dados_dict.keys())
        
        # Recuperar dados
        dados_dict = st.session_state.get('dados_comparacao', {})
        tickers_sucesso = st.session_state.get('tickers_comparacao', [])
        
        if not dados_dict:
            st.info("👆 Clique em 'Comparar' para começar a análise.")
            return
        
        # Verificar quais falharam
        tickers_falha = [t for t in tickers if t not in tickers_sucesso]
        
        if tickers_falha:
            st.warning(f"⚠️ Não foi possível obter dados para: {', '.join(tickers_falha)}")
        
        st.success(f"✅ Dados carregados para: {', '.join(tickers_sucesso)}")
        
        # === MÉTRICAS COMPARATIVAS ===
        st.markdown("### 📊 Métricas Comparativas")
        mostrar_metricas(dados_dict)
        
        # === GRÁFICO DE EVOLUÇÃO ===
        st.markdown("### 📈 Evolução de Preços")
        if normalizar:
            criar_grafico_normalizado(dados_dict)
        else:
            criar_grafico_absoluto(dados_dict)
        
        # === RETORNOS ===
        st.markdown("### 📊 Comparação de Retornos")
        criar_grafico_retornos(dados_dict)
        
        # === TABELA DETALHADA ===
        with st.expander("📋 Ver Tabela Detalhada", expanded=False):
            mostrar_tabela_detalhada(dados_dict)


def mostrar_metricas(dados_dict):
    """Mostra métricas comparativas."""
    
    metricas_lista = []
    
    for ticker, dados in dados_dict.items():
        if dados.empty:
            continue
        
        moeda = obter_simbolo_moeda(ticker)
        preco_inicial = float(dados['Close'].iloc[0])
        preco_final = float(dados['Close'].iloc[-1])
        variacao = ((preco_final - preco_inicial) / preco_inicial) * 100
        
        # Volatilidade
        retornos = dados['Close'].pct_change().dropna()
        volatilidade = retornos.std() * (252 ** 0.5) * 100
        
        metricas_lista.append({
            'Código': ticker,
            'Preço Inicial': formatar_moeda(preco_inicial, moeda),
            'Preço Atual': formatar_moeda(preco_final, moeda),
            'Variação': formatar_percentual(variacao),
            'Volatilidade': formatar_percentual(volatilidade)
        })
    
    if metricas_lista:
        df_metricas = pd.DataFrame(metricas_lista)
        st.dataframe(df_metricas, use_container_width=True, hide_index=True)


def criar_grafico_normalizado(dados_dict):
    """Cria gráfico com preços normalizados."""
    
    dados_norm = normalize_prices(dados_dict)
    
    if dados_norm.empty:
        st.warning("Não foi possível normalizar os dados.")
        return
    
    fig = go.Figure()
    
    cores = ['#667eea', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6']
    
    for i, ticker in enumerate(dados_norm.columns):
        fig.add_trace(go.Scatter(
            x=dados_norm.index,
            y=dados_norm[ticker],
            mode='lines',
            name=ticker,
            line=dict(color=cores[i % len(cores)], width=3)
        ))
    
    fig.update_layout(
        title='Comparação de Performance (Base 100)',
        yaxis_title='Valor Normalizado',
        xaxis_title='Data',
        height=600,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_absoluto(dados_dict):
    """Cria gráfico com preços absolutos."""
    
    fig = go.Figure()
    
    cores = ['#667eea', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6']
    
    for i, (ticker, dados) in enumerate(dados_dict.items()):
        if dados.empty:
            continue
        
        fig.add_trace(go.Scatter(
            x=dados.index,
            y=dados['Close'],
            mode='lines',
            name=ticker,
            line=dict(color=cores[i % len(cores)], width=3)
        ))
    
    fig.update_layout(
        title='Comparação de Preços Absolutos',
        yaxis_title='Preço',
        xaxis_title='Data',
        height=600,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_retornos(dados_dict):
    """Cria gráfico de barras com retornos."""
    
    retornos_data = {}
    
    for ticker, dados in dados_dict.items():
        if not dados.empty:
            preco_inicial = float(dados['Close'].iloc[0])
            preco_final = float(dados['Close'].iloc[-1])
            retorno = ((preco_final - preco_inicial) / preco_inicial) * 100
            retornos_data[ticker] = retorno
    
    if not retornos_data:
        st.warning("Não há dados de retorno para exibir.")
        return
    
    fig = go.Figure()
    
    tickers = list(retornos_data.keys())
    retornos = list(retornos_data.values())
    cores = ['#10b981' if r >= 0 else '#ef4444' for r in retornos]
    
    fig.add_trace(go.Bar(
        x=tickers,
        y=retornos,
        marker_color=cores,
        text=[formatar_percentual(r) for r in retornos],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Retornos no Período',
        yaxis_title='Retorno (%)',
        xaxis_title='Ativo',
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def mostrar_tabela_detalhada(dados_dict):
    """Mostra tabela comparativa detalhada."""
    
    comparacao = []
    
    for ticker, dados in dados_dict.items():
        if dados.empty:
            continue
        
        retornos = dados['Close'].pct_change().dropna()
        moeda = obter_simbolo_moeda(ticker)
        
        preco_inicial = float(dados['Close'].iloc[0])
        preco_final = float(dados['Close'].iloc[-1])
        variacao = ((preco_final - preco_inicial) / preco_inicial) * 100
        
        volatilidade = retornos.std() * (252 ** 0.5) * 100
        retorno_medio = retornos.mean() * 252 * 100
        
        # Sharpe Ratio
        sharpe = (retorno_medio - 10) / volatilidade if volatilidade != 0 else 0
        
        # Drawdown máximo
        cumulative = (1 + retornos).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        comparacao.append({
            'Código': ticker,
            f'Preço Inicial ({moeda})': f"{preco_inicial:.2f}",
            f'Preço Final ({moeda})': f"{preco_final:.2f}",
            'Variação (%)': formatar_percentual(variacao),
            'Retorno Anual (%)': formatar_percentual(retorno_medio),
            'Volatilidade (%)': formatar_percentual(volatilidade),
            'Sharpe Ratio': f"{sharpe:.2f}",
            'Drawdown Máx (%)': formatar_percentual(max_drawdown)
        })
    
    if comparacao:
        df_comparacao = pd.DataFrame(comparacao)
        st.dataframe(df_comparacao, use_container_width=True, hide_index=True)
    else:
        st.warning("Não há dados para exibir na tabela.")

