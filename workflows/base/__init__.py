"""
Base classes and utilities for PUENTE Catastral workflows.
Extends MuniStream workflow system with cadastral-specific functionality.
"""

from .catastral_steps import *
from .rpp_steps import *
from .document_types import *

__all__ = [
    'CatastralActionStep',
    'RPPActionStep', 
    'PropertyValidationStep',
    'FolioSearchStep',
    'ClaveSearchStep',
    'DocumentoCatastral',
    'DocumentoRPP',
    'CedulaUnica'
]