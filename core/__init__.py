"""
DGS Auxiliary Engine - Core Module
동진중력시스템 핵심 모듈

Constitutional Foundation:
- 대화발현의도 헌법 (CIC)
- 동진블랙홀헌법령
- CRETA 5000PP
"""

from .dgs_core import DGSCore
from .constitutional import ConstitutionalValidator
from .difr import DIFR
from .rlt8_ostinato_engine import RLT8OstinatoEngine, bbap1_upgrade

__all__ = ["DGSCore", "ConstitutionalValidator", "DIFR", "RLT8OstinatoEngine", "bbap1_upgrade"]
__version__ = "1.0.0-alpha"
__owner__ = "동진"
