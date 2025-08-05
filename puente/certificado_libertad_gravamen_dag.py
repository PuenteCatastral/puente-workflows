"""
Workflow de Certificado de Libertad de Gravamen usando sintaxis DAG.
Proceso unificado que consulta gravámenes en RPP y Catastro simultáneamente.

Sintaxis similar a Airflow DAGs con context manager pattern.
"""

import sys
import os
from typing import Dict, Any
from datetime import datetime

# Importar clases base de MuniStream
sys.path.append('/Users/paw/Projects/Puente/munistream-workflow/backend')
from app.workflows.base import (
    ActionStep, ConditionalStep, TerminalStep, IntegrationStep, ValidationResult
)
from app.workflows.workflow import Workflow


# Funciones de validación
def validate_property_identifier(inputs: Dict[str, Any]) -> ValidationResult:
    """Validar identificadores de propiedad"""
    errors = []
    
    # Validar que al menos un identificador esté presente
    identifiers = ["folio_real", "clave_catastral", "direccion_inmueble"]
    if not any(inputs.get(field) for field in identifiers):
        errors.append("Debe proporcionar al menos un identificador del inmueble")
    
    # Validar formato de folio real
    folio_real = inputs.get("folio_real", "")
    if folio_real and not folio_real.startswith("FR-"):
        errors.append("El folio real debe tener formato FR-XXXXXX")
    
    # Validar formato de clave catastral
    clave_catastral = inputs.get("clave_catastral", "")
    if clave_catastral and len(clave_catastral.split("-")) != 3:
        errors.append("La clave catastral debe tener formato XX-XXX-XXX")
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


# Funciones de acción
def collect_property_data(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Recopilar datos de identificación de la propiedad"""
    return {
        "property_data_collected": True,
        "property_identifier": {
            "folio_real": inputs.get("folio_real"),
            "clave_catastral": inputs.get("clave_catastral"),
            "direccion": inputs.get("direccion_inmueble"),
            "colonia": inputs.get("colonia"),
            "delegacion": inputs.get("delegacion")
        },
        "certificate_purpose": inputs.get("proposito_certificado"),
        "timestamp": datetime.utcnow().isoformat()
    }


def search_property_unified(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Búsqueda unificada de la propiedad en ambos sistemas"""
    property_data = context.get("property_identifier", {})
    
    # Simular búsqueda en ambos sistemas
    rpp_found = bool(property_data.get("folio_real"))
    catastro_found = bool(property_data.get("clave_catastral"))
    
    return {
        "property_search_completed": True,
        "property_found": rpp_found or catastro_found,
        "rpp_record_found": rpp_found,
        "catastro_record_found": catastro_found,
        "unified_record": {
            "folio_real": property_data.get("folio_real", "FR-2024-56789"),
            "clave_catastral": property_data.get("clave_catastral", "09-234-567"),
            "direccion_completa": property_data.get("direccion"),
            "propietario_actual": "Juan Pérez López",
            "superficie_terreno": "120.50 m²",
            "superficie_construccion": "98.75 m²"
        },
        "search_timestamp": datetime.utcnow().isoformat()
    }


def query_rpp_liens(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Consultar gravámenes en RPP"""
    folio_real = context.get("unified_record", {}).get("folio_real")
    
    # Simular consulta de gravámenes RPP
    rpp_liens = [
        {
            "tipo": "Hipoteca",
            "acreedor": "Banco Nacional",
            "monto": 850000.00,
            "fecha_inscripcion": "2020-03-15",
            "estado": "vigente"
        }
    ]
    
    return {
        "rpp_liens_query_completed": True,
        "rpp_liens_found": len(rpp_liens) > 0,
        "rpp_liens": rpp_liens,
        "rpp_blocking_liens": False,  # Ningún gravamen impide certificación
        "query_timestamp": datetime.utcnow().isoformat()
    }


def query_catastro_liens(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Consultar gravámenes y adeudos catastrales"""
    clave_catastral = context.get("unified_record", {}).get("clave_catastral")
    
    # Simular consulta catastral
    catastro_liens = []
    pending_payments = 2450.00  # Adeudo predial
    
    return {
        "catastro_liens_query_completed": True,
        "catastro_liens_found": len(catastro_liens) > 0,
        "catastro_liens": catastro_liens,
        "pending_tax_payments": pending_payments,
        "catastro_blocking_liens": pending_payments > 5000,  # Solo bloquea si adeudo > 5000
        "query_timestamp": datetime.utcnow().isoformat()
    }


def consolidate_lien_results(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Consolidar resultados de consultas de gravámenes"""
    rpp_liens = context.get("rpp_liens", [])
    catastro_liens = context.get("catastro_liens", [])
    pending_payments = context.get("pending_tax_payments", 0)
    
    # Determinar si hay gravámenes que impidan certificación
    blocking_liens = (
        context.get("rpp_blocking_liens", False) or 
        context.get("catastro_blocking_liens", False)
    )
    
    total_liens = len(rpp_liens) + len(catastro_liens)
    
    return {
        "consolidation_completed": True,
        "total_liens_found": total_liens,
        "blocking_liens_exist": blocking_liens,
        "certification_possible": not blocking_liens,
        "consolidated_report": {
            "rpp_liens": rpp_liens,
            "catastro_liens": catastro_liens,
            "pending_tax_payments": pending_payments,
            "total_liens": total_liens,
            "property_status": "libre" if not blocking_liens else "gravado"
        },
        "consolidation_timestamp": datetime.utcnow().isoformat()
    }


def calculate_certificate_fees(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Calcular derechos del certificado"""
    base_fee = 450.00  # Derecho base por certificado
    urgency_fee = 225.00 if inputs.get("urgente", False) else 0.00
    
    total_fee = base_fee + urgency_fee
    
    return {
        "fee_calculation_completed": True,
        "fee_breakdown": {
            "derecho_base": base_fee,
            "derecho_urgencia": urgency_fee,
            "total": total_fee
        },
        "calculation_timestamp": datetime.utcnow().isoformat()
    }


def generate_certificate(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Generar certificado de libertad de gravamen"""
    unified_record = context.get("unified_record", {})
    consolidated_report = context.get("consolidated_report", {})
    
    certificate_number = f"CLG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "certificate_generated": True,
        "certificate_data": {
            "numero_certificado": certificate_number,
            "folio_real": unified_record.get("folio_real"),
            "clave_catastral": unified_record.get("clave_catastral"),
            "propietario": unified_record.get("propietario_actual"),
            "direccion": unified_record.get("direccion_completa"),
            "gravamenes_rpp": consolidated_report.get("rpp_liens", []),
            "gravamenes_catastro": consolidated_report.get("catastro_liens", []),
            "adeudo_predial": consolidated_report.get("pending_tax_payments", 0),
            "estatus_propiedad": consolidated_report.get("property_status"),
            "fecha_emision": datetime.utcnow().isoformat(),
            "vigencia": "30 días"
        },
        "generation_timestamp": datetime.utcnow().isoformat()
    }


# Funciones condicionales
def property_found(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que se encontró la propiedad"""
    return context.get("property_found", False)


def certification_possible(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que es posible emitir certificado"""
    return context.get("certification_possible", False)


def payment_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que el pago fue exitoso"""
    return context.get("payment_successful", False)


def create_certificado_libertad_gravamen_dag_workflow() -> Workflow:
    """Crear workflow de certificado usando sintaxis DAG"""
    
    # Usar sintaxis DAG con context manager
    with Workflow(
        workflow_id="certificado_libertad_gravamen_dag_v1",
        name="Certificado de Libertad de Gravamen (DAG)",
        description="Proceso unificado para obtener certificado de gravámenes usando sintaxis DAG"
    ) as workflow:
        
        # Definir operadores (se auto-registran)
        collect_property = ActionStep(
            step_id="collect_property_data",
            name="Recopilar Datos de la Propiedad",
            action=collect_property_data,
            description="Captura de identificadores de la propiedad para consulta",
            required_inputs=["proposito_certificado"],
            requires_citizen_input=True,
            input_form={
                "title": "Certificado de Libertad de Gravamen",
                "description": "Proporcione los datos de la propiedad para generar el certificado",
                "fields": [
                    {
                        "id": "folio_real",
                        "label": "Folio Real",
                        "type": "text",
                        "required": False,
                        "placeholder": "FR-XXXXXX"
                    },
                    {
                        "id": "clave_catastral",
                        "label": "Clave Catastral",
                        "type": "text",
                        "required": False,
                        "placeholder": "XX-XXX-XXX"
                    },
                    {
                        "id": "direccion_inmueble",
                        "label": "Dirección del Inmueble",
                        "type": "text",
                        "required": False
                    },
                    {
                        "id": "proposito_certificado",
                        "label": "Propósito del Certificado",
                        "type": "select",
                        "required": True,
                        "options": ["Trámite bancario", "Compraventa", "Herencia", "Litigio", "Otro"]
                    },
                    {
                        "id": "urgente",
                        "label": "¿Requiere trámite urgente?",
                        "type": "select",
                        "required": False,
                        "options": ["No", "Sí (costo adicional)"]
                    }
                ]
            }
        ).add_validation(validate_property_identifier)
        
        search_property = ActionStep(
            step_id="search_property_unified",
            name="Búsqueda Unificada de Propiedad",
            action=search_property_unified,
            description="Localizar la propiedad en registros RPP y catastrales"
        )
        
        property_check = ConditionalStep(
            step_id="property_found_check",
            name="Verificar Localización",
            description="Verificar que se localizó la propiedad"
        )
        
        query_rpp = ActionStep(
            step_id="query_rpp_liens",
            name="Consultar Gravámenes RPP",
            action=query_rpp_liens,
            description="Consulta de gravámenes en Registro Público de la Propiedad"
        )
        
        query_catastro = ActionStep(
            step_id="query_catastro_liens",
            name="Consultar Gravámenes Catastro",
            action=query_catastro_liens,
            description="Consulta de gravámenes y adeudos en sistema catastral"
        )
        
        consolidate = ActionStep(
            step_id="consolidate_lien_results",
            name="Consolidar Resultados",
            action=consolidate_lien_results,
            description="Consolidar resultados de consultas de gravámenes"
        )
        
        certification_check = ConditionalStep(
            step_id="certification_feasibility_check",
            name="Verificar Viabilidad de Certificación",
            description="Evaluar si es posible emitir el certificado"
        )
        
        calculate_fees = ActionStep(
            step_id="calculate_certificate_fees",
            name="Calcular Derechos",
            action=calculate_certificate_fees,
            description="Calcular costo del certificado"
        )
        
        process_payment = IntegrationStep(
            step_id="process_payment",
            name="Procesar Pago",
            service_name="payment_gateway",
            endpoint="https://api.payments.example/process-certificate",
            description="Procesar pago de derechos del certificado"
        )
        
        payment_check = ConditionalStep(
            step_id="payment_verification",
            name="Verificar Pago",
            description="Verificar que el pago fue procesado"
        )
        
        generate_cert = ActionStep(
            step_id="generate_certificate",
            name="Generar Certificado",
            action=generate_certificate,
            description="Generar certificado de libertad de gravamen"
        )
        
        # Pasos terminales
        success = TerminalStep(
            step_id="certificate_issued",
            name="Certificado Emitido",
            terminal_status="SUCCESS",
            description="Certificado de libertad de gravamen emitido exitosamente"
        )
        
        property_not_found = TerminalStep(
            step_id="property_not_found",
            name="Propiedad No Encontrada",
            terminal_status="FAILURE",
            description="No se pudo localizar la propiedad en los sistemas"
        )
        
        blocking_liens = TerminalStep(
            step_id="blocking_liens_found",
            name="Gravámenes Impiden Certificación",
            terminal_status="FAILURE",
            description="Existen gravámenes o adeudos que impiden la certificación"
        )
        
        payment_failed = TerminalStep(
            step_id="payment_failed",
            name="Pago Fallido",
            terminal_status="FAILURE",
            description="No se pudo procesar el pago de derechos"
        )
        
        # Definir flujo usando sintaxis tipo Airflow
        collect_property >> search_property >> property_check
        
        # Rutas condicionales usando when()
        property_check.when(property_found) >> query_rpp
        property_check.when(lambda i, c: not property_found(i, c)) >> property_not_found
        
        # Flujo paralelo de consultas (simulado secuencial)
        query_rpp >> query_catastro >> consolidate >> certification_check
        
        # Verificación de certificación
        certification_check.when(certification_possible) >> calculate_fees
        certification_check.when(lambda i, c: not certification_possible(i, c)) >> blocking_liens
        
        # Flujo de pago
        calculate_fees >> process_payment >> payment_check
        payment_check.when(payment_successful) >> generate_cert >> success
        payment_check.when(lambda i, c: not payment_successful(i, c)) >> payment_failed
    
    # El workflow se auto-construye y valida al salir del context manager
    return workflow


# Ejemplo de uso
if __name__ == "__main__":
    workflow = create_certificado_libertad_gravamen_dag_workflow()
    print(f"Workflow creado: {workflow.name}")
    print(f"ID: {workflow.workflow_id}")
    print(f"Total de pasos: {len(workflow.steps)}")
    print(f"Paso inicial: {workflow.start_step.name}")