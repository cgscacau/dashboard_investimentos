"""Módulo de análise de fundos de investimento."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config import Config
from utils.data_fetcher import fetch_stock_data, get_stock_info
from utils.formatters import formatar_moeda, formatar_percentual, obter_simbolo_moeda


def show():
    """Exibe a página de análise de fundos."""
    st.title("💼 Análise de Fundos de Investimento")
    
    st.info("""
    **Como usar:**
    - Para fundos brasileiros, use o código com sufixo .SA (ex: HASH11.SA para ETFs)
    - Para fundos internacionais, use o código direto (ex: SPY, QQQ)
    """)
    
    # Sidebar com controles
    with st.sidebar:
        st.header("Configurações")
        
        ticker = st.text_input(
            "Digite o código do fundo:",
            value="HASH11.SA",
            help="Ex: HASH11.SA (ETF brasileiro) ou SPY (ETF americano)"
        ).upper()
        
        periodo_label = st.selectbox(
            "Período de análise:",
            options=list(Config.PERIODOS.keys()),
            index=3
        )
        periodo = Config.PERIODOS[periodo_label]
    
    # Buscar dados
    with st.spinner(f"Carregando dados de {ticker}..."):
        dados = fetch_stock_data(ticker, periodo)
    
    if dados is None or dados.empty:
        st.error(f"❌ Não foi possível obter dados para o fundo {ticker}")
        st.info("💡 Verifique se o código está correto.")
        return
    
    # Normalizar dados
    dados = normalizar_dados(dados)
    moeda = obter_simbolo_moeda(ticker)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        preco_atual = float(dados['Close'].iloc[-1])
        preco_inicial = float(dados['Close'].iloc[0])
        variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100
        
        with col1:
            st.metric("Valor Atual", formatar_moeda(preco_atual, moeda))
        
        with col2:
            st.metric("Rentabilidade", formatar_percentual(variacao), 
                     delta=formatar_percentual(variacao))
        
        with col3:
            volatilidade = calcular_volatilidade_anual(dados)
            st.metric("Volatilidade Anual", formatar_percentual(volatilidade))
        
        with col4:
            sharpe = calcular_sharpe_ratio(dados)
            st.metric("Índice Sharpe", f"{sharpe:.2f}")
    
    except (ValueError, TypeError, IndexError) as e:
        st.error(f"❌ Erro ao processar métricas: {str(e)}")
        return
    
    # Gráfico de evolução
    criar_grafico_evolucao(dados, ticker, moeda)
    
    # Gráfico de retornos
    criar_grafico_retornos(dados, ticker)
    
    # Análise de performance
    with st.expander("📊 Análise de Performance"):
        mostrar_analise_performance(dados, moeda)
    
    # Estatísticas
    with st.expander("📈 Estatísticas Detalhadas"):
        mostrar_estatisticas_fundo(dados, moeda)
    
    # Informações do fundo
    with st.expander("ℹ️ Informações do Fundo"):
        mostrar_info_fundo(ticker)


def normalizar_dados(dados):
    """Normaliza o DataFrame."""
    if dados.empty:
        return dados
    
    if isinstance(dados.columns, pd.MultiIndex):
        dados.columns = dados.columns.get_level_values(0)
    
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in dados.columns:
            dados[col] = pd.to_numeric(dados[col], errors='coerce')
    
    dados = dados.dropna(subset=['Close'])
    return dados


def calcular_volatilidade_anual(dados):
    """Calcula a volatilidade anualizada."""
    try:
        retornos = dados['Close'].pct_change().dropna()
        volatilidade = retornos.std() * (252 ** 0.5) * 100
        return float(volatilidade)
    except Exception:
        return 0.0


def calcular_sharpe_ratio(dados, taxa_livre_risco=0.10):
    """Calcula o Índice Sharpe."""
    try:
        retornos = dados['Close'].pct_change().dropna()
        retorno_medio = retornos.mean() * 252
        volatilidade = retornos.std() * (252 ** 0.5)
        
        if volatilidade == 0:
            return 0
        
        sharpe = (retorno_medio - taxa_livre_risco) / volatilidade
        return float(sharpe)
    except Exception:
        return 0


def criar_grafico_evolucao(dados, ticker, moeda):
    """Cria gráfico de evolução do fundo."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dados.index,
        y=dados['Close'],
        mode='lines',
        name='Valor da Cota',
        line=dict(color='blue', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 100, 255, 0.1)'
    ))
    
    # Adicionar média móvel 50
    sma_50 = dados['Close'].rolling(window=50).mean()
    fig.add_trace(go.Scatter(
        x=dados.index,
        y=sma_50,
        mode='lines',
        name='Média 50 dias',
        line=dict(color='red', width=1, dash='dash')
    ))
    
    fig.update_layout(
        title=f'Evolução do Valor - {ticker}',
        yaxis_title=f'Valor ({moeda})',
        xaxis_title='Data',
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_retornos(dados, ticker):
    """Cria gráfico de distribuição de retornos."""
    retornos = dados['Close'].pct_change().dropna() * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=retornos,
        nbinsx=50,
        name='Retornos Diários',
        marker_color='blue',
        opacity=0.7
    ))
    
    fig.update_layout(
        title=f'Distribuição de Retornos Diários - {ticker}',
        xaxis_title='Retorno (%)',
        yaxis_title='Frequência',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def mostrar_analise_performance(dados, moeda):
    """Mostra análise de performance do fundo."""
    retornos = dados['Close'].pct_change().dropna()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retornos")
        st.write(f"**Retorno Diário Médio:** {formatar_percentual(retornos.mean()*100, 3)}")
        st.write(f"**Retorno Mensal Médio:** {formatar_percentual(retornos.mean()*21*100)}")
        st.write(f"**Retorno Anual (252 dias):** {formatar_percentual(retornos.mean()*252*100)}")
        
        # Melhor e pior dia
        melhor_dia = retornos.max() * 100
        pior_dia = retornos.min() * 100
        st.write(f"**Melhor Dia:** +{formatar_percentual(melhor_dia)}")
        st.write(f"**Pior Dia:** {formatar_percentual(pior_dia)}")
    
    with col2:
        st.subheader("Risco")
        st.write(f"**Volatilidade Diária:** {formatar_percentual(retornos.std()*100, 3)}")
        st.write(f"**Volatilidade Mensal:** {formatar_percentual(retornos.std()*(21**0.5)*100)}")
        st.write(f"**Volatilidade Anual:** {formatar_percentual(retornos.std()*(252**0.5)*100)}")
        
        # Drawdown
        cumulative = (1 + retornos).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        st.write(f"**Drawdown Máximo:** {formatar_percentual(max_drawdown)}")


def mostrar_estatisticas_fundo(dados, moeda):
    """Mostra estatísticas detalhadas do fundo."""
    st.subheader("Estatísticas de Preço")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Mínimo:** {formatar_moeda(dados['Close'].min(), moeda)}")
        st.write(f"**Máximo:** {formatar_moeda(dados['Close'].max(), moeda)}")
        amplitude = dados['Close'].max() - dados['Close'].min()
        st.write(f"**Amplitude:** {formatar_moeda(amplitude, moeda)}")
    
    with col2:
        st.write(f"**Média:** {formatar_moeda(dados['Close'].mean(), moeda)}")
        st.write(f"**Mediana:** {formatar_moeda(dados['Close'].median(), moeda)}")
        st.write(f"**Desvio Padrão:** {formatar_moeda(dados['Close'].std(), moeda)}")
    
    with col3:
        percentil_25 = dados['Close'].quantile(0.25)
        percentil_75 = dados['Close'].quantile(0.75)
        st.write(f"**Percentil 25%:** {formatar_moeda(percentil_25, moeda)}")
        st.write(f"**Percentil 75%:** {formatar_moeda(percentil_75, moeda)}")
        st.write(f"**IQR:** {formatar_moeda(percentil_75 - percentil_25, moeda)}")


def mostrar_info_fundo(ticker):
    """Mostra informações do fundo."""
    info = get_stock_info(ticker)
    
    if info:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'longName' in info:
                st.write(f"**Nome:** {info['longName']}")
            if 'fundFamily' in info:
                st.write(f"**Família:** {info['fundFamily']}")
            if 'category' in info:
                st.write(f"**Categoria:** {info['category']}")
        
        with col2:
            if 'totalAssets' in info and info['totalAssets']:
                try:
                    from utils.formatters import formatar_numero_grande
                    assets = formatar_numero_grande(info['totalAssets'])
                    moeda = obter_simbolo_moeda(ticker)
                    st.write(f"**Patrimônio:** {moeda} {assets}")
                except (ValueError, TypeError):
                    pass
            
            if 'ytdReturn' in info and info['ytdReturn']:
                try:
                    ytd = float(info['ytdReturn']) * 100
                    st.write(f"**Retorno no Ano:** {formatar_percentual(ytd)}")
                except (ValueError, TypeError):
                    pass
            
            if 'threeYearAverageReturn' in info and info['threeYearAverageReturn']:
                try:
                    three_year = float(info['threeYearAverageReturn']) * 100
                    st.write(f"**Retorno Médio 3 Anos:** {formatar_percentual(three_year)}")
                except (ValueError, TypeError):
                    pass
    else:
        st.info("Informações do fundo não disponíveis.")
