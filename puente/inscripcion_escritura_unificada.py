"""
Workflow de Inscripción de Escritura Unificada.
Inscribir escritura pública con sincronización automática bidireccional al Catastro.

Separation of Concerns: Responsabilidad específica de inscripción de escrituras
DRY: Reutiliza patrones de vinculación y sincronización
KISS: Flujo lineal y comprensible
"""

from typing import Dict, Any


def create_inscripcion_escritura_unificada_workflow():
    """
    Crear workflow de inscripción de escritura con sincronización automática al Catastro.
    
    Returns:
        Dict: Configuración completa del workflow para MuniStream
    """
    
    return {
        "workflow_id": "inscripcion_escritura_unificada_v1",
        "name": "Inscripción de Escritura Unificada",
        "description": "Inscribir escritura pública con sincronización automática bidireccional al Catastro",
        "version": "1.0.0",
        "category": "RPP",
        "estimated_duration": "10-15 minutos",
        "steps": [
            {
                "step_id": "collect_escritura_data",
                "name": "Recopilar Datos de Escritura",
                "step_type": "action",
                "description": "Recolección de información de la escritura pública",
                "requires_citizen_input": True,
                "input_form": {
                    "title": "Inscripción de Escritura Pública",
                    "description": "Proporcione los datos de la escritura a inscribir",
                    "fields": [
                        {
                            "id": "numero_escritura",
                            "name": "numero_escritura",
                            "label": "Número de Escritura",
                            "type": "text",
                            "required": True,
                            "pattern": "^[0-9]+$",
                            "helpText": "Número de la escritura pública"
                        },
                        {
                            "id": "notario",
                            "name": "notario",
                            "label": "Notario Autorizante",
                            "type": "text",
                            "required": True,
                            "helpText": "Nombre completo del notario que autorizó la escritura"
                        },
                        {
                            "id": "fecha_escritura",
                            "name": "fecha_escritura",
                            "label": "Fecha de Escritura",
                            "type": "date",
                            "required": True,
                            "helpText": "Fecha en que se otorgó la escritura"
                        },
                        {
                            "id": "tipo_operacion",
                            "name": "tipo_operacion",
                            "label": "Tipo de Operación",
                            "type": "select",
                            "required": True,
                            "options": ["Compraventa", "Donación", "Herencia", "Adjudicación", "Permuta"],
                            "helpText": "Tipo de acto jurídico realizado"
                        },
                        {
                            "id": "valor_operacion",
                            "name": "valor_operacion",
                            "label": "Valor de la Operación",
                            "type": "number",
                            "required": True,
                            "validation": {"min": 1000},
                            "helpText": "Valor económico de la operación en pesos"
                        },
                        {
                            "id": "comprador_nombre",
                            "name": "comprador_nombre",
                            "label": "Nombre del Adquirente",
                            "type": "text",
                            "required": True,
                            "helpText": "Nombre completo de quien adquiere la propiedad"
                        },
                        {
                            "id": "vendedor_nombre",
                            "name": "vendedor_nombre",
                            "label": "Nombre del Transmitente",
                            "type": "text",
                            "required": True,
                            "helpText": "Nombre completo de quien transmite la propiedad"
                        },
                        {
                            "id": "descripcion_inmueble",
                            "name": "descripcion_inmueble",
                            "label": "Descripción del Inmueble",
                            "type": "textarea",
                            "required": True,
                            "helpText": "Descripción detallada del inmueble según escritura"
                        },
                        {
                            "id": "escritura_document",
                            "name": "escritura_document",
                            "label": "Documento de Escritura",
                            "type": "file",
                            "required": True,
                            "helpText": "Archivo PDF de la escritura pública"
                        }
                    ]
                },
                "next_steps": ["validate_escritura_data"]
            },
            {
                "step_id": "validate_escritura_data",
                "name": "Validar Datos de Escritura",
                "step_type": "action",
                "description": "Validación de la información de la escritura",
                "next_steps": ["escritura_validation_check"]
            },
            {
                "step_id": "escritura_validation_check",
                "name": "Verificación de Validación de Escritura",
                "step_type": "conditional",
                "description": "Verificar si los datos de la escritura son válidos",
                "next_steps": ["auto_link_catastro", "escritura_validation_failed"]
            },
            {
                "step_id": "auto_link_catastro",
                "name": "Vinculación Automática con Catastro",
                "step_type": "integration",
                "description": "Búsqueda y vinculación automática del registro en el Catastro",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/rpp-catastro/auto-link",
                    "method": "POST"
                },
                "next_steps": ["linking_decision_rpp"]
            },
            {
                "step_id": "linking_decision_rpp",
                "name": "Decisión de Vinculación RPP",
                "step_type": "conditional",
                "description": "Evaluar resultado de la vinculación con Catastro",
                "conditions": [
                    {
                        "condition": "linking_score >= 0.95",
                        "next_step": "inscribe_escritura"
                    },
                    {
                        "condition": "linking_score >= 0.70",
                        "next_step": "manual_linking_review_rpp"
                    },
                    {
                        "default": True,
                        "next_step": "create_catastral_record"
                    }
                ]
            },
            {
                "step_id": "inscribe_escritura",
                "name": "Inscribir Escritura en RPP",
                "step_type": "integration",
                "description": "Registrar la escritura en el sistema RPP",
                "integration_config": {
                    "service": "puente_rpp_service",
                    "endpoint": "/api/rpp/inscribe-escritura",
                    "method": "POST"
                },
                "next_steps": ["sync_with_catastro"]
            },
            {
                "step_id": "sync_with_catastro",
                "name": "Sincronizar con Catastro",
                "step_type": "integration",
                "description": "Sincronizar inscripción con el sistema catastral",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/rpp-catastro/sync",
                    "method": "POST"
                },
                "next_steps": ["sync_verification_rpp"]
            },
            {
                "step_id": "sync_verification_rpp",
                "name": "Verificar Sincronización RPP",
                "step_type": "conditional",
                "description": "Verificar que la sincronización con Catastro fue exitosa",
                "conditions": [
                    {
                        "condition": "sync_successful == true",
                        "next_step": "generate_inscription_certificate"
                    },
                    {
                        "default": True,
                        "next_step": "rollback_inscription"
                    }
                ]
            },
            {
                "step_id": "generate_inscription_certificate",
                "name": "Generar Certificado de Inscripción",
                "step_type": "action",
                "description": "Generar certificado oficial de inscripción",
                "next_steps": ["send_inscription_notification"]
            },
            {
                "step_id": "send_inscription_notification",
                "name": "Enviar Notificación de Inscripción",
                "step_type": "action",
                "description": "Notificar al ciudadano sobre la inscripción exitosa",
                "next_steps": ["inscripcion_completada"]
            },
            {
                "step_id": "create_catastral_record",
                "name": "Crear Registro Catastral",
                "step_type": "integration",
                "description": "Crear registro básico en Catastro para nueva vinculación",
                "integration_config": {
                    "service": "puente_catastral_service",
                    "endpoint": "/api/catastro/create-basic-record",
                    "method": "POST"
                },
                "next_steps": ["inscribe_escritura"]
            },
            {
                "step_id": "rollback_inscription",
                "name": "Revertir Inscripción",
                "step_type": "integration",
                "description": "Revertir inscripción por fallo en sincronización",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/rpp-catastro/rollback",
                    "method": "POST"
                },
                "next_steps": ["inscription_sync_failed"]
            },
            {
                "step_id": "manual_linking_review_rpp",
                "name": "Revisión Manual de Vinculación RPP",
                "step_type": "approval",
                "description": "Revisión manual requerida para vinculación RPP-Catastro",
                "approval_config": {
                    "required_role": "rpp_analyst",
                    "timeout_hours": 24,
                    "escalation_role": "rpp_supervisor"
                },
                "next_steps": ["manual_review_decision_rpp"]
            },
            {
                "step_id": "manual_review_decision_rpp",
                "name": "Decisión de Revisión Manual RPP",
                "step_type": "conditional",
                "description": "Evaluar decisión de la revisión manual RPP",
                "conditions": [
                    {
                        "condition": "manual_approval == true",
                        "next_step": "inscribe_escritura"
                    },
                    {
                        "default": True,
                        "next_step": "create_catastral_record"
                    }
                ]
            },
            # Pasos terminales
            {
                "step_id": "inscripcion_completada",
                "name": "Inscripción Completada",
                "step_type": "terminal",
                "description": "Inscripción de escritura y sincronización catastral completadas exitosamente"
            },
            {
                "step_id": "escritura_validation_failed",
                "name": "Validación de Escritura Fallida",
                "step_type": "terminal",
                "description": "Los datos de la escritura proporcionados no son válidos"
            },
            {
                "step_id": "inscription_sync_failed",
                "name": "Fallo de Sincronización de Inscripción",
                "step_type": "terminal",
                "description": "No se pudo sincronizar con el Catastro, inscripción revertida"
            }
        ],
        "start_step_id": "collect_escritura_data"
    }