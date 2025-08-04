"""
Workflow de Registro de Propiedad Nueva.
Registrar nueva propiedad simultáneamente en Catastro y RPP con vinculación automática.

Separation of Concerns: Responsabilidad específica de crear propiedades nuevas
DRY: Reutiliza validaciones y procesos de ambos sistemas
KISS: Flujo secuencial claro y directo
"""

from typing import Dict, Any


def create_registro_propiedad_nueva_workflow():
    """
    Crear workflow de registro de propiedad nueva con vinculación simultánea Catastro-RPP.
    
    Returns:
        Dict: Configuración completa del workflow para MuniStream
    """
    
    return {
        "workflow_id": "registro_propiedad_nueva_v1",
        "name": "Registro de Propiedad Nueva",
        "description": "Registrar nueva propiedad simultáneamente en Catastro y RPP con vinculación automática",
        "version": "1.0.0",
        "category": "Unificado",
        "estimated_duration": "15-20 minutos",
        "steps": [
            {
                "step_id": "collect_property_data",
                "name": "Recopilar Datos de Propiedad",
                "step_type": "action",
                "description": "Recolección completa de información de la nueva propiedad",
                "requires_citizen_input": True,
                "input_form": {
                    "title": "Registro de Nueva Propiedad",
                    "description": "Proporcione toda la información de la nueva propiedad",
                    "fields": [
                        {
                            "id": "propietario_nombre",
                            "name": "propietario_nombre",
                            "label": "Nombre del Propietario",
                            "type": "text",
                            "required": True,
                            "helpText": "Nombre completo del propietario de la nueva propiedad"
                        },
                        {
                            "id": "propietario_identificacion",
                            "name": "propietario_identificacion",
                            "label": "Identificación del Propietario",
                            "type": "text",
                            "required": True,
                            "pattern": "^[A-Z]{4}[0-9]{6}[A-Z0-9]{3}$",
                            "helpText": "RFC del propietario"
                        },
                        {
                            "id": "direccion_completa",
                            "name": "direccion_completa", 
                            "label": "Dirección Completa",
                            "type": "textarea",
                            "required": True,
                            "helpText": "Dirección completa del inmueble incluyendo colonia, CP, municipio"
                        },
                        {
                            "id": "coordenadas_gps",
                            "name": "coordenadas_gps",
                            "label": "Coordenadas GPS",
                            "type": "text",
                            "required": False,
                            "pattern": "^-?[0-9]+\\.[0-9]+,-?[0-9]+\\.[0-9]+$",
                            "placeholder": "19.432608,-99.133209",
                            "helpText": "Coordenadas GPS en formato latitud,longitud"
                        },
                        {
                            "id": "superficie_terreno",
                            "name": "superficie_terreno",
                            "label": "Superficie de Terreno (m²)",
                            "type": "number",
                            "required": True,
                            "validation": {"min": 1, "max": 100000}
                        },
                        {
                            "id": "superficie_construccion",
                            "name": "superficie_construccion",
                            "label": "Superficie de Construcción (m²)",
                            "type": "number",
                            "required": False,
                            "validation": {"min": 0, "max": 50000}
                        },
                        {
                            "id": "uso_suelo_actual",
                            "name": "uso_suelo_actual",
                            "label": "Uso de Suelo",
                            "type": "select",
                            "required": True,
                            "options": ["Habitacional", "Comercial", "Industrial", "Mixto", "Agrícola", "Baldío"]
                        },
                        {
                            "id": "zona_valor",
                            "name": "zona_valor",
                            "label": "Zona de Valor",
                            "type": "select",
                            "required": True,
                            "options": ["A", "B", "C", "D"],
                            "helpText": "Zona de valor catastral según ubicación"
                        },
                        {
                            "id": "origen_propiedad",
                            "name": "origen_propiedad",
                            "label": "Origen de la Propiedad",
                            "type": "select",
                            "required": True,
                            "options": ["Subdivisión", "Fusión", "Regularización", "Desarrollo nuevo", "Otro"],
                            "helpText": "Cómo se originó esta nueva propiedad"
                        },
                        {
                            "id": "plano_topografico",
                            "name": "plano_topografico",
                            "label": "Plano Topográfico",
                            "type": "file",
                            "required": True,
                            "helpText": "Plano topográfico certificado del terreno"
                        },
                        {
                            "id": "titulo_propiedad",
                            "name": "titulo_propiedad",
                            "label": "Título de Propiedad",
                            "type": "file",
                            "required": True,
                            "helpText": "Documento que acredita la propiedad del terreno"
                        }
                    ]
                },
                "next_steps": ["generate_shared_uuid"]
            },
            {
                "step_id": "generate_shared_uuid",
                "name": "Generar UUID Compartido",
                "step_type": "action",
                "description": "Generar identificador único para vinculación entre sistemas",
                "next_steps": ["validate_property_data"]
            },
            {
                "step_id": "validate_property_data",
                "name": "Validar Datos de Propiedad",
                "step_type": "action",
                "description": "Validación completa de toda la información proporcionada",
                "next_steps": ["property_validation_check"]
            },
            {
                "step_id": "property_validation_check",
                "name": "Verificación de Validación",
                "step_type": "conditional",
                "description": "Verificar si todos los datos son válidos",
                "next_steps": ["check_existing_records", "property_validation_failed"]
            },
            {
                "step_id": "check_existing_records",
                "name": "Verificar Registros Existentes",
                "step_type": "integration",
                "description": "Verificar que no existan registros duplicados en ambos sistemas",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/unified/check-duplicates",
                    "method": "POST"
                },
                "next_steps": ["duplicate_check"]
            },
            {
                "step_id": "duplicate_check",
                "name": "Verificación de Duplicados",
                "step_type": "conditional",
                "description": "Verificar si se encontraron registros duplicados",
                "conditions": [
                    {
                        "condition": "duplicates_found == false",
                        "next_step": "calculate_catastral_value"
                    },
                    {
                        "default": True,
                        "next_step": "duplicate_property_found"
                    }
                ]
            },
            {
                "step_id": "calculate_catastral_value",
                "name": "Calcular Valor Catastral",
                "step_type": "integration",
                "description": "Calcular valor catastral basado en zona y características",
                "integration_config": {
                    "service": "puente_catastral_service",
                    "endpoint": "/api/catastro/calculate-value",
                    "method": "POST"
                },
                "next_steps": ["generate_clave_catastral"]
            },
            {
                "step_id": "generate_clave_catastral",
                "name": "Generar Clave Catastral",
                "step_type": "integration",
                "description": "Generar nueva clave catastral para la propiedad",
                "integration_config": {
                    "service": "puente_catastral_service",
                    "endpoint": "/api/catastro/generate-clave",
                    "method": "POST"
                },
                "next_steps": ["create_catastral_record"]
            },
            {
                "step_id": "create_catastral_record",
                "name": "Crear Registro Catastral",
                "step_type": "integration",
                "description": "Crear registro completo en el sistema catastral",
                "integration_config": {
                    "service": "puente_catastral_service",
                    "endpoint": "/api/catastro/create-record",
                    "method": "POST"
                },
                "next_steps": ["generate_folio_real"]
            },
            {
                "step_id": "generate_folio_real",
                "name": "Generar Folio Real",
                "step_type": "integration",
                "description": "Generar nuevo folio real para la propiedad",
                "integration_config": {
                    "service": "puente_rpp_service",
                    "endpoint": "/api/rpp/generate-folio",
                    "method": "POST"
                },
                "next_steps": ["create_rpp_record"]
            },
            {
                "step_id": "create_rpp_record",
                "name": "Crear Registro RPP",
                "step_type": "integration",
                "description": "Crear registro completo en el sistema RPP",
                "integration_config": {
                    "service": "puente_rpp_service",
                    "endpoint": "/api/rpp/create-record",
                    "method": "POST"
                },
                "next_steps": ["establish_linking"]
            },
            {
                "step_id": "establish_linking",
                "name": "Establecer Vinculación",
                "step_type": "integration",
                "description": "Crear vinculación bidireccional en tabla de correspondencias",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/unified/establish-link",
                    "method": "POST"
                },
                "next_steps": ["linking_verification"]
            },
            {
                "step_id": "linking_verification",
                "name": "Verificación de Vinculación",
                "step_type": "conditional",
                "description": "Verificar que la vinculación se estableció correctamente",
                "conditions": [
                    {
                        "condition": "linking_established == true",
                        "next_step": "generate_unified_certificate"
                    },
                    {
                        "default": True,
                        "next_step": "rollback_all_records"
                    }
                ]
            },
            {
                "step_id": "generate_unified_certificate",
                "name": "Generar Cédula Única",
                "step_type": "action",
                "description": "Generar documento único con información completa de ambos sistemas",
                "next_steps": ["final_approval"]
            },
            {
                "step_id": "final_approval",
                "name": "Aprobación Final",
                "step_type": "approval",
                "description": "Aprobación final del supervisor para registro de nueva propiedad",
                "approval_config": {
                    "required_role": "property_supervisor",
                    "timeout_hours": 48,
                    "escalation_role": "property_manager"
                },
                "next_steps": ["final_approval_decision"]
            },
            {
                "step_id": "final_approval_decision",
                "name": "Decisión de Aprobación Final",
                "step_type": "conditional",
                "description": "Evaluar decisión de aprobación final",
                "conditions": [
                    {
                        "condition": "final_approval == true",
                        "next_step": "send_completion_notification"
                    },
                    {
                        "default": True,
                        "next_step": "rollback_all_records"
                    }
                ]
            },
            {
                "step_id": "send_completion_notification",
                "name": "Enviar Notificación de Finalización",
                "step_type": "action",
                "description": "Notificar al ciudadano sobre registro exitoso",
                "next_steps": ["registro_completado"]
            },
            {
                "step_id": "rollback_all_records",
                "name": "Revertir Todos los Registros",
                "step_type": "integration",
                "description": "Revertir creación de registros en ambos sistemas",
                "integration_config": {
                    "service": "puente_linking_service",
                    "endpoint": "/api/unified/rollback-all",
                    "method": "POST"
                },
                "next_steps": ["registro_failed"]
            },
            # Pasos terminales
            {
                "step_id": "registro_completado",
                "name": "Registro Completado",
                "step_type": "terminal",
                "description": "Nueva propiedad registrada exitosamente en ambos sistemas"
            },
            {
                "step_id": "property_validation_failed",
                "name": "Validación de Propiedad Fallida",
                "step_type": "terminal",
                "description": "Los datos de la propiedad proporcionados no son válidos"
            },
            {
                "step_id": "duplicate_property_found",
                "name": "Propiedad Duplicada Encontrada",
                "step_type": "terminal",
                "description": "Se encontró una propiedad existente con características similares"
            },
            {
                "step_id": "registro_failed",
                "name": "Registro Fallido",
                "step_type": "terminal",
                "description": "No se pudo completar el registro, todos los cambios fueron revertidos"
            }
        ],
        "start_step_id": "collect_property_data"
    }