"""
Workflow de Actualización Catastral Unificada.
Actualizar registro catastral con sincronización automática bidireccional al RPP.

Separation of Concerns: Un único workflow con responsabilidad específica
DRY: Reutiliza componentes base y configuraciones comunes
KISS: Estructura simple y clara
"""

from typing import Dict, Any, List
from datetime import datetime


def create_actualizacion_catastral_unificada_workflow():
    """
    Crear workflow de actualización catastral con sincronización automática al RPP.
    
    Returns:
        Dict: Configuración completa del workflow para MuniStream
    """
    
    return {
        "workflow_id": "actualizacion_catastral_unificada_v1",
        "name": "Actualización Catastral Unificada",
        "description": "Actualizar registro catastral con sincronización automática bidireccional al RPP",
        "version": "1.0.0",
        "category": "Catastral",
        "estimated_duration": "5-10 minutos",
        "steps": [
            {
                "step_id": "collect_catastral_data",
                "name": "Recopilar Datos Catastrales",
                "step_type": "action",
                "description": "Recolección de información catastral del ciudadano",
                "requires_citizen_input": True,
                "input_form": {
                    "title": "Actualización de Registro Catastral",
                    "description": "Proporcione los datos del inmueble a actualizar",
                    "fields": [
                        {
                            "id": "clave_catastral",
                            "name": "clave_catastral",
                            "label": "Clave Catastral",
                            "type": "text",
                            "required": True,
                            "pattern": "^[0-9]{2}-[0-9]{3}-[0-9]{3}$",
                            "placeholder": "09-123-456",
                            "helpText": "Formato: XX-XXX-XXX"
                        },
                        {
                            "id": "nombre_propietario",
                            "name": "nombre_propietario", 
                            "label": "Nombre del Propietario",
                            "type": "text",
                            "required": True,
                            "maxLength": 200,
                            "helpText": "Nombre completo del propietario actual"
                        },
                        {
                            "id": "direccion_inmueble",
                            "name": "direccion_inmueble",
                            "label": "Dirección del Inmueble",
                            "type": "textarea",
                            "required": True,
                            "helpText": "Dirección completa del inmueble"
                        },
                        {
                            "id": "superficie_terreno",
                            "name": "superficie_terreno",
                            "label": "Superficie de Terreno (m²)",
                            "type": "number",
                            "required": True,
                            "validation": {"min": 1, "max": 100000},
                            "helpText": "Superficie del terreno en metros cuadrados"
                        },
                        {
                            "id": "superficie_construccion",
                            "name": "superficie_construccion",
                            "label": "Superficie de Construcción (m²)",
                            "type": "number",
                            "required": False,
                            "validation": {"min": 0, "max": 50000},
                            "helpText": "Superficie construida en metros cuadrados"
                        },
                        {
                            "id": "uso_suelo",
                            "name": "uso_suelo",
                            "label": "Uso de Suelo",
                            "type": "select",
                            "required": True,
                            "options": ["Habitacional", "Comercial", "Industrial", "Mixto", "Baldío"],
                            "helpText": "Uso actual del inmueble"
                        },
                        {
                            "id": "motivo_actualizacion",
                            "name": "motivo_actualizacion",
                            "label": "Motivo de Actualización",
                            "type": "select",
                            "required": True,
                            "options": [
                                "Cambio de propietario",
                                "Modificación física del inmueble", 
                                "Corrección de datos",
                                "Actualización de valor catastral",
                                "Cambio de uso de suelo"
                            ],
                            "helpText": "Razón por la cual se solicita la actualización"
                        }
                    ]
                },
                "next_steps": ["validate_catastral_data"]
            },
            {
                "step_id": "validate_catastral_data",
                "name": "Validar Datos Catastrales",
                "step_type": "action",
                "description": "Validación de la información catastral proporcionada",
                "required_inputs": ["clave_catastral", "nombre_propietario", "direccion_inmueble"],
                "next_steps": ["catastral_validation_check"]
            },
            {
                "step_id": "catastral_validation_check",
                "name": "Verificación de Validación Catastral",
                "step_type": "conditional",
                "description": "Verificar si los datos catastrales son válidos",
                "next_steps": ["auto_link_rpp", "catastral_validation_failed"]
            },
            {
                "step_id": "auto_link_rpp",
                "name": "Vinculación Automática con RPP",
                "step_type": "integration",
                "description": "Búsqueda y vinculación automática del registro en el RPP",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/catastro-rpp/auto-link",
                    "method": "POST",
                    "timeout": 30
                },
                "next_steps": ["linking_decision"]
            },
            {
                "step_id": "linking_decision",
                "name": "Decisión de Vinculación",
                "step_type": "conditional", 
                "description": "Evaluar resultado de la vinculación automática",
                "conditions": [
                    {
                        "condition": "linking_score >= 0.95",
                        "next_step": "update_catastral_record"
                    },
                    {
                        "condition": "linking_score >= 0.70",
                        "next_step": "manual_linking_review"
                    },
                    {
                        "default": True,
                        "next_step": "create_rpp_record"
                    }
                ]
            },
            {
                "step_id": "update_catastral_record",
                "name": "Actualizar Registro Catastral",
                "step_type": "integration",
                "description": "Actualizar la información en el sistema catastral",
                "integration_config": {
                    "service": "puente_catastral_service",
                    "endpoint": "/api/catastro/update-record",
                    "method": "POST"
                },
                "next_steps": ["sync_with_rpp"]
            },
            {
                "step_id": "sync_with_rpp",
                "name": "Sincronizar con RPP", 
                "step_type": "integration",
                "description": "Sincronizar cambios catastrales con el RPP",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/catastro-rpp/sync",
                    "method": "POST"
                },
                "next_steps": ["sync_verification"]
            },
            {
                "step_id": "sync_verification",
                "name": "Verificar Sincronización",
                "step_type": "conditional",
                "description": "Verificar que la sincronización fue exitosa",
                "conditions": [
                    {
                        "condition": "sync_successful == true",
                        "next_step": "generate_unified_certificate"
                    },
                    {
                        "default": True,
                        "next_step": "rollback_changes"
                    }
                ]
            },
            {
                "step_id": "generate_unified_certificate",
                "name": "Generar Cédula Unificada",
                "step_type": "action",
                "description": "Generar documento unificado con información de Catastro y RPP",
                "next_steps": ["send_notification"]
            },
            {
                "step_id": "send_notification",
                "name": "Enviar Notificación",
                "step_type": "action",
                "description": "Notificar al ciudadano sobre la actualización exitosa",
                "next_steps": ["actualizacion_completada"]
            },
            {
                "step_id": "create_rpp_record",
                "name": "Crear Registro en RPP",
                "step_type": "integration",
                "description": "Crear registro básico en RPP para nueva vinculación",
                "integration_config": {
                    "service": "puente_rpp_service",
                    "endpoint": "/api/rpp/create-basic-record",
                    "method": "POST"
                },
                "next_steps": ["update_catastral_record"]
            },
            {
                "step_id": "rollback_changes",
                "name": "Revertir Cambios",
                "step_type": "integration",
                "description": "Revertir cambios por fallo en sincronización",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/catastro-rpp/rollback",
                    "method": "POST"
                },
                "next_steps": ["sync_failed"]
            },
            {
                "step_id": "manual_linking_review",
                "name": "Revisión Manual de Vinculación",
                "step_type": "approval",
                "description": "Revisión manual requerida para vinculación con score intermedio",
                "approval_config": {
                    "required_role": "catastral_analyst",
                    "timeout_hours": 24,
                    "escalation_role": "catastral_supervisor"
                },
                "next_steps": ["manual_review_decision"]
            },
            {
                "step_id": "manual_review_decision",
                "name": "Decisión de Revisión Manual",
                "step_type": "conditional",
                "description": "Evaluar decisión de la revisión manual",
                "conditions": [
                    {
                        "condition": "manual_approval == true",
                        "next_step": "update_catastral_record"
                    },
                    {
                        "default": True,
                        "next_step": "create_rpp_record"
                    }
                ]
            },
            # Pasos terminales
            {
                "step_id": "actualizacion_completada",
                "name": "Actualización Completada",
                "step_type": "terminal",
                "description": "Actualización catastral y sincronización RPP completadas exitosamente"
            },
            {
                "step_id": "catastral_validation_failed",
                "name": "Validación Catastral Fallida",
                "step_type": "terminal",
                "description": "Los datos catastrales proporcionados no son válidos"
            },
            {
                "step_id": "sync_failed",
                "name": "Fallo de Sincronización",
                "step_type": "terminal", 
                "description": "No se pudo sincronizar con el RPP, cambios revertidos"
            }
        ],
        "start_step_id": "collect_catastral_data"
    }