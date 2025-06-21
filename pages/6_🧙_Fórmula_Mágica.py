# pages/6_🧙_Fórmula_Mágica.py

import streamlit as st
import pandas as pd
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Screener de Ações", layout="wide")

# --- FUNÇÕES DE SCRAPING E CÁLCULO ---

@st.cache_data(ttl=3600)
def scrape_fundamentus_full():
    url = "https://www.fundamentus.com.br/resultado.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        df = pd.read_html(response.text, decimal=',', thousands='.')[0]
        return df
    except Exception as e:
        st.error(f"Erro ao acessar o Fundamentus: {e}")
        return pd.DataFrame()

def clean_and_prepare_data(df):
    df_clean = df.copy()
    for col in df_clean.columns:
        if col == 'Papel': continue
        if df_clean[col].dtype == 'object':
            had_percent = df_clean[col].str.contains('%', na=False).any()
            df_clean[col] = df_clean[col].str.replace('%', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            if had_percent:
                df_clean[col] = df_clean[col] / 100
    # ✅ CORREÇÃO: Removido o filtro de liquidez fixo daqui para garantir que todos os ativos sejam processados.
    return df_clean

def rank_stocks(df, selected_indicators):
    ranking_direction = {'P/L': True, 'P/VP': True, 'Div.Yield': False, 'ROIC': False, 'ROE': False, 'Cresc. Rec.5a': False}
    rank_cols = []
    for indicator in selected_indicators:
        rank_col_name = f"Rank ({indicator})"
        df[rank_col_name] = df[indicator].rank(ascending=ranking_direction[indicator], na_option='bottom')
        rank_cols.append(rank_col_name)
    if rank_cols:
        df['🏆 Rank Final'] = df[rank_cols].sum(axis=1)
        df = df.sort_values(by='🏆 Rank Final')
    return df

# --- INTERFACE PRINCIPAL ---

st.title("💡 Screener de Ações Personalizado")
st.markdown("Crie seu próprio ranking de ações! Defina filtros, escolha seus indicadores favoritos e encontre as melhores oportunidades do mercado.")
st.info("Quanto menor o **'🏆 Rank Final'**, melhor a empresa segundo os seus critérios de ranking.")

INDICATOR_MAP = {
    'P/L 🔽': 'P/L', 'P/VP 🔽': 'P/VP', 'Div.Yield 🔼': 'Div.Yield', 
    'ROIC 🔼': 'ROIC', 'ROE 🔼': 'ROE', 'Cresc. Rec.5a 🔼': 'Cresc. Rec.5a'
}
INDICATOR_LABELS = list(INDICATOR_MAP.keys())

# ✅ MUDANÇA: Seção de filtros com Mínimo e Máximo
st.subheader("1. Filtre o Universo de Ações (Opcional)")
st.caption("Defina os intervalos desejados. Deixe os valores em 0 para não aplicar o filtro correspondente.")

with st.expander("Clique para abrir/fechar os filtros"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        min_dy = c1.number_input("DY (%) Mínimo", value=0.0, step=0.5, format="%.2f") / 100
        min_roic = c1.number_input("ROIC (%) Mínimo", value=0.0, step=1.0, format="%.2f") / 100
    with c2:
        max_dy = c2.number_input("DY (%) Máximo", value=0.0, step=0.5, format="%.2f") / 100
        max_roic = c2.number_input("ROIC (%) Máximo", value=0.0, step=1.0, format="%.2f") / 100
    with c3:
        min_pl = c3.number_input("P/L Mínimo", value=0.0, step=0.5, format="%.2f")
        min_pvp = c3.number_input("P/VP Mínimo", value=0.0, step=0.1, format="%.2f")
    with c4:
        max_pl = c4.number_input("P/L Máximo", value=0.0, step=1.0, format="%.2f")
        max_pvp = c4.number_input("P/VP Máximo", value=0.0, step=0.1, format="%.2f")

    # Filtro de liquidez separado para destaque
    min_liq = st.number_input("Liquidez Mínima (Negociação Média Diária em R$)", value=200000, step=50000, format="%d")

st.subheader("2. Selecione os Indicadores para o Ranking")
selected_labels = st.multiselect(
    "Escolha os indicadores que irão compor o 'Rank Final':",
    options=INDICATOR_LABELS,
    default=['P/L 🔽', 'Div.Yield 🔼', 'ROIC 🔼']
)

if st.button("Gerar Ranking de Ações"):
    selected_indicators = [INDICATOR_MAP[label] for label in selected_labels]
    if not selected_indicators:
        st.warning("Por favor, selecione pelo menos um indicador para gerar o ranking.")
    else:
        with st.spinner("Buscando e processando todos os dados do Fundamentus..."):
            raw_df = scrape_fundamentus_full()
        
        if not raw_df.empty:
            cleaned_df = clean_and_prepare_data(raw_df)
            
            # Aplicação dos filtros de forma mais completa
            filtered_df = cleaned_df.copy()
            if min_liq > 0: filtered_df = filtered_df[filtered_df['Liq.2meses'] >= min_liq]
            if min_dy > 0: filtered_df = filtered_df[filtered_df['Div.Yield'] >= min_dy]
            if max_dy > 0: filtered_df = filtered_df[filtered_df['Div.Yield'] <= max_dy]
            if min_pl > 0: filtered_df = filtered_df[filtered_df['P/L'] >= min_pl]
            if max_pl > 0: filtered_df = filtered_df[filtered_df['P/L'] <= max_pl]
            if min_pvp > 0: filtered_df = filtered_df[filtered_df['P/VP'] >= min_pvp]
            if max_pvp > 0: filtered_df = filtered_df[filtered_df['P/VP'] <= max_pvp]
            if min_roic > 0: filtered_df = filtered_df[filtered_df['ROIC'] >= min_roic]
            if max_roic > 0: filtered_df = filtered_df[filtered_df['ROIC'] <= max_roic]
            
            if filtered_df.empty:
                st.warning("Nenhuma empresa encontrada com os filtros definidos. Tente critérios menos restritivos.")
            else:
                ranked_df = rank_stocks(filtered_df, selected_indicators)
                display_cols = ['Papel', 'Cotação', '🏆 Rank Final'] + selected_indicators
                st.success(f"Ranking gerado com sucesso para {len(ranked_df)} ações!")
                st.dataframe(
                    ranked_df[display_cols].style.format({
                        'Cotação': 'R$ {:.2f}', 'Div.Yield': '{:.2%}', 'ROIC': '{:.2%}',
                        'ROE': '{:.2%}', 'Cresc. Rec.5a': '{:.2%}', 'P/L': '{:.2f}', 'P/VP': '{:.2f}'
                    }),
                    height=800, use_container_width=True, hide_index=True
                )
        else:
            st.error("Não foi possível carregar os dados do Fundamentus.")