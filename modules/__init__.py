"""
Módulos de análise do Dashboard de Investimentos.

Este pacote contém os módulos principais para análise de:
- Ações individuais
- Fundos de investimento
- Comparação entre múltiplos ativos
"""

from . import analise_acoes
from . import analise_fundos
from . import comparacao

__all__ = [
    'analise_acoes',
    'analise_fundos',
    'comparacao'
]

__version__ = '2.0.0'

