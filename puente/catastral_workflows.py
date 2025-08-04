"""
Módulo principal de workflows catastrales PUENTE.
Imports centralizados siguiendo principios DRY.

Separation of Concerns: Punto de entrada único para todos los workflows
DRY: Importaciones centralizadas evitando duplicación
KISS: Estructura simple de imports y exports
"""

# Importaciones de workflows específicos
from .actualizacion_catastral_unificada import create_actualizacion_catastral_unificada_workflow
from .inscripcion_escritura_unificada import create_inscripcion_escritura_unificada_workflow
from .registro_propiedad_nueva import create_registro_propiedad_nueva_workflow
from .certificado_libertad_gravamen import create_certificado_libertad_gravamen_workflow
from .avaluo_catastral_unificado import create_avaluo_catastral_unificado_workflow


# Exportaciones para munistream.yaml
__all__ = [
    'create_actualizacion_catastral_unificada_workflow',
    'create_inscripcion_escritura_unificada_workflow', 
    'create_registro_propiedad_nueva_workflow',
    'create_certificado_libertad_gravamen_workflow',
    'create_avaluo_catastral_unificado_workflow'
]