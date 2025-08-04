"""
Workflow de Certificado de Libertad de Gravamen Unificado.
Generar certificado unificado consultando Catastro y RPP simultáneamente.

Separation of Concerns: Responsabilidad específica de certificaciones
DRY: Reutiliza búsquedas y validaciones unificadas
KISS: Proceso directo de consulta y certificación
"""

from typing import Dict, Any


def create_certificado_libertad_gravamen_workflow():
    """
    Crear workflow de certificado de libertad de gravamen unificado.
    
    Returns:
        Dict: Configuración completa del workflow para MuniStream
    """
    
    return {
        "workflow_id": "certificado_libertad_gravamen_v1",
        "name": "Certificado de Libertad de Gravamen Unificado",
        "description": "Generar certificado unificado consultando Catastro y RPP simultáneamente",
        "version": "1.0.0",
        "category": "Certificación",
        "estimated_duration": "3-5 minutos",
        "steps": [
            {
                "step_id": "collect_search_criteria",
                "name": "Recopilar Criterios de Búsqueda",
                "step_type": "action",
                "description": "Recolección de criterios para búsqueda de la propiedad",
                "requires_citizen_input": True,
                "input_form": {
                    "title": "Certificado de Libertad de Gravamen",
                    "description": "Proporcione información para localizar la propiedad",
                    "fields": [
                        {
                            "id": "search_type",
                            "name": "search_type",
                            "label": "Tipo de Búsqueda",
                            "type": "select",
                            "required": True,
                            "options": ["Clave Catastral", "Folio Real", "Dirección", "Propietario"],
                            "helpText": "Seleccione el tipo de criterio de búsqueda"
                        },
                        {
                            "id": "clave_catastral",
                            "name": "clave_catastral",
                            "label": "Clave Catastral",
                            "type": "text",
                            "required": False,
                            "pattern": "^[0-9]{2}-[0-9]{3}-[0-9]{3}$",
                            "helpText": "Clave catastral si se conoce"
                        },
                        {
                            "id": "folio_real",
                            "name": "folio_real",
                            "label": "Folio Real",
                            "type": "text",
                            "required": False,
                            "helpText": "Número de folio real si se conoce"
                        },
                        {
                            "id": "direccion_busqueda",
                            "name": "direccion_busqueda",
                            "label": "Dirección",
                            "type": "text",
                            "required": False,
                            "helpText": "Dirección del inmueble"
                        },
                        {
                            "id": "propietario_busqueda",
                            "name": "propietario_busqueda",
                            "label": "Nombre del Propietario",
                            "type": "text",
                            "required": False,
                            "helpText": "Nombre del propietario actual"
                        },
                        {
                            "id": "solicitante_nombre",
                            "name": "solicitante_nombre",
                            "label": "Nombre del Solicitante",
                            "type": "text",
                            "required": True,
                            "helpText": "Nombre de quien solicita el certificado"
                        },
                        {
                            "id": "solicitante_identificacion",
                            "name": "solicitante_identificacion",
                            "label": "Identificación del Solicitante",
                            "type": "text",
                            "required": True,
                            "helpText": "Identificación oficial del solicitante"
                        }
                    ]
                },
                "next_steps": ["search_unified_records"]
            },
            {
                "step_id": "search_unified_records",
                "name": "Buscar Registros Unificados",
                "step_type": "integration",
                "description": "Búsqueda simultánea en Catastro y RPP",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/unified/search-property",
                    "method": "POST"
                },
                "next_steps": ["search_results_check"]
            },
            {
                "step_id": "search_results_check",
                "name": "Verificación de Resultados",
                "step_type": "conditional",
                "description": "Verificar si se encontró la propiedad",
                "conditions": [
                    {
                        "condition": "property_found == true",
                        "next_step": "verify_linking_status"
                    },
                    {
                        "default": True,
                        "next_step": "property_not_found"
                    }
                ]
            },
            {
                "step_id": "verify_linking_status",
                "name": "Verificar Estado de Vinculación",
                "step_type": "integration",
                "description": "Verificar que los registros estén correctamente vinculados",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/unified/verify-linking",
                    "method": "POST"
                },
                "next_steps": ["linking_status_check"]
            },
            {
                "step_id": "linking_status_check",
                "name": "Verificación de Estado de Vinculación",
                "step_type": "conditional",
                "description": "Verificar el estado de vinculación entre sistemas",
                "conditions": [
                    {
                        "condition": "linking_synchronized == true",
                        "next_step": "consult_catastral_status"
                    },
                    {
                        "default": True,
                        "next_step": "linking_inconsistency_found"
                    }
                ]
            },
            {
                "step_id": "consult_catastral_status",
                "name": "Consultar Estado Catastral",
                "step_type": "integration",
                "description": "Consultar estado y gravámenes en sistema catastral",
                "integration_config": {
                    "service": "puente_catastral_service",
                    "endpoint": "/api/catastro/consult-status",
                    "method": "POST"
                },
                "next_steps": ["consult_rpp_liens"]
            },
            {
                "step_id": "consult_rpp_liens",
                "name": "Consultar Gravámenes RPP",
                "step_type": "integration",
                "description": "Consultar gravámenes y anotaciones en RPP",
                "integration_config": {
                    "service": "puente_rpp_service",
                    "endpoint": "/api/rpp/consult-liens",
                    "method": "POST"
                },
                "next_steps": ["analyze_lien_status"]
            },
            {
                "step_id": "analyze_lien_status",
                "name": "Analizar Estado de Gravámenes",
                "step_type": "action",
                "description": "Analizar información de gravámenes de ambos sistemas",
                "next_steps": ["lien_analysis_result"]
            },
            {
                "step_id": "lien_analysis_result",
                "name": "Resultado de Análisis de Gravámenes",
                "step_type": "conditional",
                "description": "Evaluar si la propiedad está libre de gravámenes",
                "conditions": [
                    {
                        "condition": "liens_found == false",
                        "next_step": "calculate_certificate_fee"
                    },
                    {
                        "default": True,
                        "next_step": "generate_lien_report"
                    }
                ]
            },
            {
                "step_id": "calculate_certificate_fee",
                "name": "Calcular Costo del Certificado",
                "step_type": "action",
                "description": "Calcular costo del certificado de libertad de gravamen",
                "next_steps": ["process_payment"]
            },
            {
                "step_id": "process_payment",
                "name": "Procesar Pago",
                "step_type": "integration",
                "description": "Procesar pago del certificado",
                "integration_config": {
                    "service": "payment_gateway",
                    "endpoint": "/api/payments/process",
                    "method": "POST"
                },
                "next_steps": ["payment_verification"]
            },
            {
                "step_id": "payment_verification",
                "name": "Verificación de Pago",
                "step_type": "conditional",
                "description": "Verificar que el pago fue exitoso",
                "conditions": [
                    {
                        "condition": "payment_successful == true",
                        "next_step": "generate_clean_certificate"
                    },
                    {
                        "default": True,
                        "next_step": "payment_failed"
                    }
                ]
            },
            {
                "step_id": "generate_clean_certificate",
                "name": "Generar Certificado Libre de Gravamen",
                "step_type": "action",
                "description": "Generar certificado oficial de libertad de gravamen",
                "next_steps": ["sign_certificate"]
            },
            {
                "step_id": "generate_lien_report",
                "name": "Generar Reporte de Gravámenes",
                "step_type": "action",
                "description": "Generar reporte detallado de gravámenes encontrados",
                "next_steps": ["calculate_certificate_fee"]
            },
            {
                "step_id": "sign_certificate",
                "name": "Firmar Certificado",
                "step_type": "action",
                "description": "Aplicar firma digital al certificado",
                "next_steps": ["send_certificate"]
            },
            {
                "step_id": "send_certificate",
                "name": "Enviar Certificado",
                "step_type": "action",
                "description": "Enviar certificado al solicitante",
                "next_steps": ["certificado_emitido"]
            },
            # Pasos terminales
            {
                "step_id": "certificado_emitido",
                "name": "Certificado Emitido",
                "step_type": "terminal",
                "description": "Certificado de libertad de gravamen emitido exitosamente"
            },
            {
                "step_id": "property_not_found",
                "name": "Propiedad No Encontrada",
                "step_type": "terminal",
                "description": "No se pudo localizar la propiedad con los criterios proporcionados"
            },
            {
                "step_id": "linking_inconsistency_found",
                "name": "Inconsistencia de Vinculación Encontrada",
                "step_type": "terminal",
                "description": "Se encontraron inconsistencias entre los registros de Catastro y RPP"
            },
            {
                "step_id": "payment_failed",
                "name": "Pago Fallido",
                "step_type": "terminal",
                "description": "No se pudo procesar el pago del certificado"
            }
        ],
        "start_step_id": "collect_search_criteria"
    }