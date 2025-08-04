"""
Workflow de Avalúo Catastral Unificado.
Generar avalúo catastral considerando información completa de Catastro y RPP.

Separation of Concerns: Responsabilidad específica de valuación de propiedades
DRY: Reutiliza búsquedas, validaciones y procesos de pago
KISS: Flujo claro con decisiones bien definidas
"""

from typing import Dict, Any


def create_avaluo_catastral_unificado_workflow():
    """
    Crear workflow de avalúo catastral unificado con información RPP.
    
    Returns:
        Dict: Configuración completa del workflow para MuniStream
    """
    
    return {
        "workflow_id": "avaluo_catastral_unificado_v1",
        "name": "Avalúo Catastral Unificado",
        "description": "Generar avalúo catastral considerando información completa de Catastro y RPP",
        "version": "1.0.0",
        "category": "Valuación",
        "estimated_duration": "15-30 minutos",
        "steps": [
            {
                "step_id": "collect_avaluo_request",
                "name": "Recopilar Solicitud de Avalúo",
                "step_type": "action",
                "description": "Recolección de información para solicitud de avalúo",
                "requires_citizen_input": True,
                "input_form": {
                    "title": "Solicitud de Avalúo Catastral",
                    "description": "Proporcione información para realizar el avalúo",
                    "fields": [
                        {
                            "id": "clave_catastral_avaluo",
                            "name": "clave_catastral_avaluo",
                            "label": "Clave Catastral",
                            "type": "text",
                            "required": True,
                            "pattern": "^[0-9]{2}-[0-9]{3}-[0-9]{3}$",
                            "helpText": "Clave catastral del inmueble a valuar"
                        },
                        {
                            "id": "proposito_avaluo",
                            "name": "proposito_avaluo",
                            "label": "Propósito del Avalúo",
                            "type": "select",
                            "required": True,
                            "options": [
                                "Compraventa",
                                "Crédito hipotecario",
                                "Herencia",
                                "Donación",
                                "Actualización catastral",
                                "Expropiación",
                                "Seguros",
                                "Otros"
                            ],
                            "helpText": "Para qué se utilizará el avalúo"
                        },
                        {
                            "id": "solicitante_avaluo",
                            "name": "solicitante_avaluo",
                            "label": "Nombre del Solicitante",
                            "type": "text",
                            "required": True,
                            "helpText": "Nombre de quien solicita el avalúo"
                        },
                        {
                            "id": "tipo_avaluo",
                            "name": "tipo_avaluo",
                            "label": "Tipo de Avalúo",
                            "type": "select",
                            "required": True,
                            "options": [
                                "Físico (con inspección)",
                                "Documental (sin inspección)",
                                "Masivo automatizado"
                            ],
                            "helpText": "Tipo de avalúo solicitado"
                        },
                        {
                            "id": "urgencia_avaluo",
                            "name": "urgencia_avaluo",
                            "label": "Nivel de Urgencia",
                            "type": "select",
                            "required": True,
                            "options": ["Normal (5-7 días)", "Urgente (2-3 días)", "Express (24 horas)"],
                            "helpText": "Tiempo requerido para entrega"
                        }
                    ]
                },
                "next_steps": ["search_property_records"]
            },
            {
                "step_id": "search_property_records",
                "name": "Buscar Registros de Propiedad",
                "step_type": "integration",
                "description": "Búsqueda de información completa en Catastro y RPP",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/unified/search-for-valuation",
                    "method": "POST"
                },
                "next_steps": ["property_records_check"]
            },
            {
                "step_id": "property_records_check",
                "name": "Verificación de Registros",
                "step_type": "conditional",
                "description": "Verificar si se encontraron los registros necesarios",
                "conditions": [
                    {
                        "condition": "records_complete == true",
                        "next_step": "gather_market_data"
                    },
                    {
                        "default": True,
                        "next_step": "incomplete_records_found"
                    }
                ]
            },
            {
                "step_id": "gather_market_data",
                "name": "Recopilar Datos de Mercado",
                "step_type": "integration",
                "description": "Obtener información de mercado inmobiliario de la zona",
                "integration_config": {
                    "service": "market_data_service",
                    "endpoint": "/api/market/zone-analysis",
                    "method": "POST"
                },
                "next_steps": ["schedule_inspection_decision"]
            },
            {
                "step_id": "schedule_inspection_decision",
                "name": "Decisión de Inspección",
                "step_type": "conditional",
                "description": "Determinar si se requiere inspección física",
                "conditions": [
                    {
                        "condition": "tipo_avaluo == 'Físico (con inspección)'",
                        "next_step": "schedule_physical_inspection"
                    },
                    {
                        "default": True,
                        "next_step": "perform_desktop_valuation"
                    }
                ]
            },
            {
                "step_id": "schedule_physical_inspection",
                "name": "Programar Inspección Física",
                "step_type": "action",
                "description": "Programar visita de inspector valuador",
                "next_steps": ["conduct_physical_inspection"]
            },
            {
                "step_id": "conduct_physical_inspection",
                "name": "Realizar Inspección Física",
                "step_type": "approval",
                "description": "Inspección física del inmueble por valuador certificado",
                "approval_config": {
                    "required_role": "certified_appraiser",
                    "timeout_hours": 72,
                    "escalation_role": "senior_appraiser"
                },
                "next_steps": ["inspection_completion_check"]
            },
            {
                "step_id": "inspection_completion_check",
                "name": "Verificación de Inspección",
                "step_type": "conditional",
                "description": "Verificar que la inspección se completó",
                "conditions": [
                    {
                        "condition": "inspection_completed == true",
                        "next_step": "perform_comprehensive_valuation"
                    },
                    {
                        "default": True,
                        "next_step": "inspection_failed"
                    }
                ]
            },
            {
                "step_id": "perform_desktop_valuation",
                "name": "Realizar Valuación Documental",
                "step_type": "integration",
                "description": "Valuación basada en información documental y datos de mercado",
                "integration_config": {
                    "service": "valuation_engine",
                    "endpoint": "/api/valuation/desktop",
                    "method": "POST"
                },
                "next_steps": ["calculate_final_value"]
            },
            {
                "step_id": "perform_comprehensive_valuation",
                "name": "Realizar Valuación Integral",
                "step_type": "integration",
                "description": "Valuación considerando inspección física y todos los datos disponibles",
                "integration_config": {
                    "service": "valuation_engine",
                    "endpoint": "/api/valuation/comprehensive",
                    "method": "POST"
                },
                "next_steps": ["calculate_final_value"]
            },
            {
                "step_id": "calculate_final_value",
                "name": "Calcular Valor Final",
                "step_type": "action",
                "description": "Calcular valor final considerando todos los factores",
                "next_steps": ["valuation_review"]
            },
            {
                "step_id": "valuation_review",
                "name": "Revisión de Valuación",
                "step_type": "approval",
                "description": "Revisión técnica del avalúo por supervisor",
                "approval_config": {
                    "required_role": "valuation_supervisor",
                    "timeout_hours": 24,
                    "escalation_role": "valuation_manager"
                },
                "next_steps": ["review_decision"]
            },
            {
                "step_id": "review_decision",
                "name": "Decisión de Revisión",
                "step_type": "conditional",
                "description": "Evaluar si el avalúo fue aprobado",
                "conditions": [
                    {
                        "condition": "valuation_approved == true",
                        "next_step": "generate_appraisal_report"
                    },
                    {
                        "default": True,
                        "next_step": "valuation_requires_correction"
                    }
                ]
            },
            {
                "step_id": "generate_appraisal_report",
                "name": "Generar Reporte de Avalúo",
                "step_type": "action",
                "description": "Generar reporte oficial de avalúo",
                "next_steps": ["calculate_service_fee"]
            },
            {
                "step_id": "calculate_service_fee",
                "name": "Calcular Costo del Servicio",
                "step_type": "action",
                "description": "Calcular costo del avalúo según tipo y urgencia",
                "next_steps": ["process_avaluo_payment"]
            },
            {
                "step_id": "process_avaluo_payment",
                "name": "Procesar Pago de Avalúo",
                "step_type": "integration",
                "description": "Procesar pago del servicio de avalúo",
                "integration_config": {
                    "service": "payment_gateway",
                    "endpoint": "/api/payments/process",
                    "method": "POST"
                },
                "next_steps": ["avaluo_payment_verification"]
            },
            {
                "step_id": "avaluo_payment_verification",
                "name": "Verificación de Pago de Avalúo",
                "step_type": "conditional",
                "description": "Verificar que el pago fue exitoso",
                "conditions": [
                    {
                        "condition": "payment_successful == true",
                        "next_step": "sign_appraisal_report"
                    },
                    {
                        "default": True,
                        "next_step": "avaluo_payment_failed"
                    }
                ]
            },
            {
                "step_id": "sign_appraisal_report",
                "name": "Firmar Reporte de Avalúo",
                "step_type": "action",
                "description": "Aplicar firmas digitales al reporte de avalúo",
                "next_steps": ["update_catastral_value"]
            },
            {
                "step_id": "update_catastral_value",
                "name": "Actualizar Valor Catastral",
                "step_type": "integration",
                "description": "Actualizar valor catastral en el sistema con el nuevo avalúo",
                "integration_config": {
                    "service": "puente_catastral_service",
                    "endpoint": "/api/catastro/update-value",
                    "method": "POST"
                },
                "next_steps": ["send_appraisal_report"]
            },
            {
                "step_id": "send_appraisal_report",
                "name": "Enviar Reporte de Avalúo",
                "step_type": "action",
                "description": "Enviar reporte final al solicitante",
                "next_steps": ["avaluo_completado"]
            },
            {
                "step_id": "valuation_requires_correction",
                "name": "Corrección de Valuación Requerida",
                "step_type": "action",
                "description": "Realizar correcciones solicitadas en la valuación",
                "next_steps": ["calculate_final_value"]
            },
            # Pasos terminales
            {
                "step_id": "avaluo_completado",
                "name": "Avalúo Completado",
                "step_type": "terminal",
                "description": "Avalúo catastral unificado completado exitosamente"
            },
            {
                "step_id": "incomplete_records_found",
                "name": "Registros Incompletos",
                "step_type": "terminal",
                "description": "No se encontró información suficiente para realizar el avalúo"
            },
            {
                "step_id": "inspection_failed",
                "name": "Inspección Fallida",
                "step_type": "terminal",
                "description": "No se pudo completar la inspección física del inmueble"
            },
            {
                "step_id": "avaluo_payment_failed",
                "name": "Pago de Avalúo Fallido",
                "step_type": "terminal",
                "description": "No se pudo procesar el pago del servicio de avalúo"
            }
        ],
        "start_step_id": "collect_avaluo_request"
    }