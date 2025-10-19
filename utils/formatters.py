"""Funções de formatação e tradução."""

from config import Config


def formatar_moeda(valor, moeda='R$'):
    """
    Formata valor como moeda.
    
    Args:
        valor: Valor numérico
        moeda: Símbolo da moeda
        
    Returns:
        String formatada
    """
    try:
        valor_float = float(valor)
        if abs(valor_float) >= 1_000_000_000:
            return f"{moeda} {valor_float/1_000_000_000:.2f}B"
        elif abs(valor_float) >= 1_000_000:
            return f"{moeda} {valor_float/1_000_000:.2f}M"
        elif abs(valor_float) >= 1_000:
            return f"{moeda} {valor_float/1_000:.2f}K"
        else:
            return f"{moeda} {valor_float:.2f}"
    except (ValueError, TypeError):
        return "N/A"


def formatar_percentual(valor, casas_decimais=2):
    """
    Formata valor como percentual.
    
    Args:
        valor: Valor numérico (ex: 0.05 para 5%)
        casas_decimais: Número de casas decimais
        
    Returns:
        String formatada
    """
    try:
        valor_float = float(valor)
        return f"{valor_float:.{casas_decimais}f}%"
    except (ValueError, TypeError):
        return "N/A"


def formatar_numero_grande(valor):
    """
    Formata números grandes com sufixos (K, M, B, T).
    
    Args:
        valor: Valor numérico
        
    Returns:
        String formatada
    """
    try:
        valor_float = float(valor)
        if abs(valor_float) >= 1_000_000_000_000:
            return f"{valor_float/1_000_000_000_000:.2f}T"
        elif abs(valor_float) >= 1_000_000_000:
            return f"{valor_float/1_000_000_000:.2f}B"
        elif abs(valor_float) >= 1_000_000:
            return f"{valor_float/1_000_000:.2f}M"
        elif abs(valor_float) >= 1_000:
            return f"{valor_float/1_000:.2f}K"
        else:
            return f"{valor_float:.2f}"
    except (ValueError, TypeError):
        return "N/A"


def traduzir_setor(setor_ingles):
    """
    Traduz nome do setor de inglês para português.
    
    Args:
        setor_ingles: Nome do setor em inglês
        
    Returns:
        Nome do setor em português
    """
    if not setor_ingles:
        return "N/A"
    
    return Config.SETORES_PORTUGUES.get(setor_ingles, setor_ingles)


def obter_simbolo_moeda(ticker):
    """
    Obtém o símbolo da moeda baseado no ticker.
    
    Args:
        ticker: Símbolo da ação
        
    Returns:
        Símbolo da moeda
    """
    if '.SA' in ticker:
        return 'R$'
    else:
        return '$'
