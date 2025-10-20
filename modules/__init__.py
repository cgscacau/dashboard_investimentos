"""
Módulos de análise do Dashboard de Investimentos - Sistema de Ranking.
"""

from . import ranking_acoes
from . import ranking_fundos
from . import analise_detalhada
from . import comparacao

__all__ = [
    'ranking_acoes',
    'ranking_fundos',
    'analise_detalhada',
    'comparacao'
]

__version__ = '3.0.0'
