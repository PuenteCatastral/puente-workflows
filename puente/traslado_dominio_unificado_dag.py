"""
Workflow de Traslado de Dominio Unificado usando sintaxis DAG.
Proceso completo que actualiza la titularidad en RPP y Catastro simultáneamente.

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
def validate_transfer_data(inputs: Dict[str, Any]) -> ValidationResult:
    """Validar datos básicos del traslado"""
    errors = []
    
    required_fields = [
        "tipo_traslado", "propietario_actual_nombre", "propietario_actual_rfc",
        "nuevo_propietario_nombre", "nuevo_propietario_rfc", "nuevo_propietario_curp",
        "documento_soporte", "fecha_documento", "valor_operacion"
    ]
    
    for field in required_fields:
        if not inputs.get(field):
            errors.append(f"Campo requerido faltante: {field}")
    
    # Validar que al menos un identificador de inmueble esté presente
    identifiers = ["folio_real", "clave_catastral", "direccion_inmueble"]
    if not any(inputs.get(field) for field in identifiers):
        errors.append("Debe proporcionar al menos un identificador del inmueble")
    
    # Validar RFC
    rfc_actual = inputs.get("propietario_actual_rfc", "")
    rfc_nuevo = inputs.get("nuevo_propietario_rfc", "")
    
    if rfc_actual and len(rfc_actual) not in [12, 13]:
        errors.append("RFC del propietario actual debe tener 12 o 13 caracteres")
    
    if rfc_nuevo and len(rfc_nuevo) not in [12, 13]:
        errors.append("RFC del nuevo propietario debe tener 12 o 13 caracteres")
    
    # Validar CURP
    curp = inputs.get("nuevo_propietario_curp", "")
    if curp and len(curp) != 18:
        errors.append("CURP debe tener 18 caracteres")
    
    # Validar valor de operación
    try:
        valor = float(inputs.get("valor_operacion", 0))
        if valor <= 0:
            errors.append("El valor de la operación debe ser mayor a 0")
    except ValueError:
        errors.append("El valor de la operación debe ser numérico")
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_rfc(inputs: Dict[str, Any]) -> ValidationResult:
    """Validar formato de RFC"""
    errors = []
    
    rfc = inputs.get("nuevo_propietario_rfc", "")
    if rfc and not rfc.replace(" ", "").isalnum():
        errors.append("RFC contiene caracteres inválidos")
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


# Funciones de acción
def collect_transfer_data(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Recopilar y estructurar datos del traslado"""
    return {
        "transfer_data_collected": True,
        "transfer_type": inputs.get("tipo_traslado"),
        "property_identifier": {
            "folio_real": inputs.get("folio_real"),
            "clave_catastral": inputs.get("clave_catastral"),
            "direccion": inputs.get("direccion_inmueble")
        },
        "current_owner": {
            "nombre": inputs.get("propietario_actual_nombre"),
            "rfc": inputs.get("propietario_actual_rfc")
        },
        "new_owner": {
            "nombre": inputs.get("nuevo_propietario_nombre"),
            "rfc": inputs.get("nuevo_propietario_rfc"),
            "curp": inputs.get("nuevo_propietario_curp")
        },
        "supporting_document": {
            "numero": inputs.get("documento_soporte"),
            "fecha": inputs.get("fecha_documento")
        },
        "operation_value": float(inputs.get("valor_operacion", 0)),
        "timestamp": datetime.utcnow().isoformat()
    }


def search_property_records(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Buscar registros de la propiedad en ambos sistemas"""
    property_data = context.get("property_identifier", {})
    
    # Simular búsqueda unificada
    rpp_found = bool(property_data.get("folio_real"))
    catastro_found = bool(property_data.get("clave_catastral"))
    
    return {
        "property_search_completed": True,
        "property_found": rpp_found or catastro_found,
        "rpp_record_found": rpp_found,
        "catastro_record_found": catastro_found,
        "rpp_record": {
            "folio_real": property_data.get("folio_real", "FR-2024-12345"),
            "propietario_registral": context.get("current_owner", {}).get("nombre"),
            "estado": "activo"
        } if rpp_found else None,
        "catastro_record": {
            "clave_catastral": property_data.get("clave_catastral", "09-123-456"),
            "propietario_catastral": context.get("current_owner", {}).get("nombre"),
            "estado": "vigente"
        } if catastro_found else None,
        "search_timestamp": datetime.utcnow().isoformat()
    }


def verify_current_ownership(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Verificar que el propietario actual coincida en ambos sistemas"""
    current_owner = context.get("current_owner", {}).get("nombre", "")
    rpp_owner = context.get("rpp_record", {}).get("propietario_registral", "")
    catastro_owner = context.get("catastro_record", {}).get("propietario_catastral", "")
    
    # Normalizar nombres para comparación
    current_normalized = current_owner.upper().strip()
    rpp_normalized = rpp_owner.upper().strip()
    catastro_normalized = catastro_owner.upper().strip()
    
    ownership_verified = (
        current_normalized == rpp_normalized and 
        current_normalized == catastro_normalized
    )
    
    return {
        "ownership_verification_completed": True,
        "ownership_verified": ownership_verified,
        "current_owner_declared": current_owner,
        "rpp_owner_registered": rpp_owner,
        "catastro_owner_registered": catastro_owner,
        "verification_timestamp": datetime.utcnow().isoformat()
    }


def check_property_liens(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Verificar gravámenes y limitaciones de dominio"""
    folio_real = context.get("rpp_record", {}).get("folio_real")
    
    # Simular consulta de gravámenes
    liens_found = []
    blocking_liens = False
    
    return {
        "liens_check_completed": True,
        "blocking_liens_found": blocking_liens,
        "liens_found": liens_found,
        "property_status": "libre" if not blocking_liens else "gravado",
        "check_timestamp": datetime.utcnow().isoformat()
    }


def calculate_transfer_fees(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Calcular derechos registrales, ISAI catastral y otros impuestos"""
    operation_value = context.get("operation_value", 0)
    
    # Cálculo de derechos e impuestos
    rpp_fees = 2500.00  # Derechos registrales fijos
    isai_catastral = operation_value * 0.02  # 2% del valor de operación
    other_fees = 500.00  # Otros derechos
    
    total_fees = rpp_fees + isai_catastral + other_fees
    
    return {
        "fee_calculation_completed": True,
        "fee_breakdown": {
            "derechos_rpp": rpp_fees,
            "isai_catastral": isai_catastral,
            "otros_derechos": other_fees,
            "total": total_fees
        },
        "operation_value": operation_value,
        "calculation_timestamp": datetime.utcnow().isoformat()
    }


def execute_rpp_transfer(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecutar traslado en RPP"""
    folio_real = context.get("rpp_record", {}).get("folio_real")
    new_owner = context.get("new_owner", {})
    
    return {
        "rpp_transfer_completed": True,
        "rpp_transfer_successful": True,
        "new_folio_inscription": f"INS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "folio_real": folio_real,
        "new_owner_registered": new_owner.get("nombre"),
        "transfer_date": datetime.utcnow().isoformat()
    }


def execute_catastro_transfer(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecutar traslado en Catastro"""
    clave_catastral = context.get("catastro_record", {}).get("clave_catastral")
    new_owner = context.get("new_owner", {})
    
    return {
        "catastro_transfer_completed": True,
        "catastro_transfer_successful": True,
        "new_catastral_account": f"CC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "clave_catastral": clave_catastral,
        "new_owner_registered": new_owner.get("nombre"),
        "transfer_date": datetime.utcnow().isoformat()
    }


def synchronize_records(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Sincronizar registros entre ambos sistemas"""
    folio_real = context.get("folio_real")
    clave_catastral = context.get("clave_catastral")
    
    return {
        "synchronization_completed": True,
        "synchronization_successful": True,
        "linking_record": {
            "folio_real": folio_real,
            "clave_catastral": clave_catastral,
            "new_owner": context.get("new_owner", {}).get("nombre"),
            "sync_timestamp": datetime.utcnow().isoformat()
        },
        "systems_synchronized": ["rpp", "catastro"]
    }


def generate_certificates(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Generar certificados de traslado"""
    return {
        "certificates_generated": True,
        "rpp_certificate": f"CERT-RPP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "catastro_certificate": f"CERT-CAT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "generation_timestamp": datetime.utcnow().isoformat()
    }


# Funciones condicionales
def property_found_complete(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que se encontró la propiedad en ambos sistemas"""
    return (
        context.get("property_found", False) and
        context.get("rpp_record_found", False) and 
        context.get("catastro_record_found", False)
    )


def property_found_partial(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que se encontró parcialmente"""
    return (
        context.get("property_found", False) and
        (not context.get("rpp_record_found", False) or not context.get("catastro_record_found", False))
    )


def ownership_verified(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que la propiedad fue verificada"""
    return context.get("ownership_verified", False)


def no_blocking_liens(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que no hay gravámenes que bloqueen"""
    return not context.get("blocking_liens_found", True)


def payment_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que el pago fue exitoso"""
    return context.get("payment_successful", False)


def rpp_transfer_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que el traslado RPP fue exitoso"""
    return context.get("rpp_transfer_successful", False)


def catastro_transfer_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que el traslado catastral fue exitoso"""
    return context.get("catastro_transfer_successful", False)


def synchronization_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que la sincronización fue exitosa"""
    return context.get("synchronization_successful", False)


def create_traslado_dominio_unificado_dag_workflow() -> Workflow:
    """Crear workflow de traslado de dominio usando sintaxis DAG"""
    
    # Usar sintaxis DAG con context manager
    with Workflow(
        workflow_id="traslado_dominio_unificado_dag_v1",
        name="Traslado de Dominio Unificado (DAG)",
        description="Proceso completo de cambio de propietario usando sintaxis DAG"
    ) as workflow:
        
        # Definir operadores (se auto-registran)
        collect_data = ActionStep(
            step_id="collect_transfer_data",
            name="Recopilar Datos del Traslado",
            action=collect_transfer_data,
            description="Recolección de información para el traslado de dominio",
            required_inputs=[
                "tipo_traslado", "propietario_actual_nombre", "propietario_actual_rfc",
                "nuevo_propietario_nombre", "nuevo_propietario_rfc", "nuevo_propietario_curp",
                "documento_soporte", "fecha_documento", "valor_operacion"
            ],
            requires_citizen_input=True,
            input_form={
                "title": "Traslado de Dominio",
                "description": "Proporcione la información requerida para el cambio de propietario",
                "fields": [
                    {
                        "id": "tipo_traslado",
                        "label": "Tipo de Traslado",
                        "type": "select",
                        "required": True,
                        "options": ["Compraventa", "Donación", "Herencia", "Adjudicación", "Dación en Pago"]
                    },
                    {
                        "id": "folio_real",
                        "label": "Folio Real",
                        "type": "text",
                        "required": False
                    },
                    {
                        "id": "clave_catastral",
                        "label": "Clave Catastral",
                        "type": "text",
                        "required": False
                    },
                    {
                        "id": "propietario_actual_nombre",
                        "label": "Nombre del Propietario Actual",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "nuevo_propietario_nombre",
                        "label": "Nombre del Nuevo Propietario",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "nuevo_propietario_rfc",
                        "label": "RFC del Nuevo Propietario",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "valor_operacion",
                        "label": "Valor de la Operación",
                        "type": "number",
                        "required": True
                    }
                ]
            }
        ).add_validation(validate_transfer_data).add_validation(validate_rfc)
        
        search_property = ActionStep(
            step_id="search_property_records",
            name="Buscar Registros de la Propiedad", 
            action=search_property_records,
            description="Búsqueda unificada del inmueble en RPP y Catastro"
        )
        
        property_check = ConditionalStep(
            step_id="property_found_check",
            name="Verificar Localización de Propiedad",
            description="Verificar que se localizó la propiedad en ambos sistemas"
        )
        
        verify_ownership = ActionStep(
            step_id="verify_current_ownership",
            name="Verificar Propietario Actual",
            action=verify_current_ownership,
            description="Verificar que el propietario actual coincida en ambos sistemas"
        )
        
        ownership_check = ConditionalStep(
            step_id="ownership_verification_check",
            name="Verificación de Propietario",
            description="Evaluar resultado de verificación de propietario"
        )
        
        check_liens = ActionStep(
            step_id="check_property_liens",
            name="Verificar Gravámenes",
            action=check_property_liens,
            description="Consultar gravámenes y limitaciones de dominio"
        )
        
        liens_check = ConditionalStep(
            step_id="liens_check_result",
            name="Evaluación de Gravámenes",
            description="Evaluar si existen gravámenes que impidan el traslado"
        )
        
        calculate_fees = ActionStep(
            step_id="calculate_transfer_fees",
            name="Calcular Derechos y Impuestos",
            action=calculate_transfer_fees,
            description="Calcular derechos registrales, ISAI catastral y otros impuestos"
        )
        
        process_payment = IntegrationStep(
            step_id="process_payment",
            name="Procesar Pago",
            service_name="payment_gateway",
            endpoint="https://api.payments.example/process-transfer",
            description="Procesar pago de derechos registrales e impuestos"
        )
        
        payment_check = ConditionalStep(
            step_id="payment_verification",
            name="Verificación de Pago",
            description="Verificar que el pago fue procesado exitosamente"
        )
        
        rpp_transfer = ActionStep(
            step_id="execute_rpp_transfer",
            name="Ejecutar Traslado en RPP",
            action=execute_rpp_transfer,
            description="Realizar inscripción del traslado de dominio en RPP"
        )
        
        rpp_check = ConditionalStep(
            step_id="rpp_transfer_check",
            name="Verificar Traslado RPP",
            description="Verificar que el traslado en RPP fue exitoso"
        )
        
        catastro_transfer = ActionStep(
            step_id="execute_catastro_transfer",
            name="Ejecutar Traslado en Catastro",
            action=execute_catastro_transfer,
            description="Actualizar propietario en registro catastral"
        )
        
        catastro_check = ConditionalStep(
            step_id="catastro_transfer_check",
            name="Verificar Traslado Catastro",
            description="Verificar que el traslado catastral fue exitoso"
        )
        
        synchronize = ActionStep(
            step_id="synchronize_records",
            name="Sincronizar Registros",
            action=synchronize_records,
            description="Verificar y sincronizar ambos registros finalmente"
        )
        
        sync_check = ConditionalStep(
            step_id="synchronization_check",
            name="Verificar Sincronización",
            description="Verificar que ambos sistemas están sincronizados"
        )
        
        generate_certs = ActionStep(
            step_id="generate_certificates",
            name="Generar Certificados",
            action=generate_certificates,
            description="Generar certificados de inscripción RPP y catastral"
        )
        
        # Pasos terminales
        success = TerminalStep(
            step_id="traslado_completado",
            name="Traslado de Dominio Completado",
            terminal_status="SUCCESS",
            description="Traslado de dominio ejecutado exitosamente en ambos sistemas"
        )
        
        property_not_found = TerminalStep(
            step_id="property_not_found",
            name="Propiedad No Encontrada",
            terminal_status="FAILURE",
            description="No se pudo localizar la propiedad en los sistemas"
        )
        
        partial_records = TerminalStep(
            step_id="partial_records_found",
            name="Registros Parciales",
            terminal_status="PENDING",
            description="La propiedad no está registrada en ambos sistemas - requiere vinculación manual"
        )
        
        ownership_mismatch = TerminalStep(
            step_id="ownership_mismatch",
            name="Inconsistencia de Propietario",
            terminal_status="FAILURE",
            description="El propietario actual no coincide entre sistemas"
        )
        
        liens_prevent = TerminalStep(
            step_id="liens_prevent_transfer",
            name="Gravámenes Impiden Traslado",
            terminal_status="FAILURE",
            description="Existen gravámenes que impiden el traslado"
        )
        
        payment_failed = TerminalStep(
            step_id="payment_failed",
            name="Pago Fallido",
            terminal_status="FAILURE",
            description="No se pudo procesar el pago de derechos"
        )
        
        rpp_failed = TerminalStep(
            step_id="rpp_transfer_failed",
            name="Fallo en Traslado RPP",
            terminal_status="FAILURE",
            description="No se pudo completar el traslado en RPP"
        )
        
        catastro_failed = TerminalStep(
            step_id="catastro_transfer_failed",
            name="Fallo en Traslado Catastro",
            terminal_status="FAILURE",
            description="No se pudo completar el traslado en Catastro"
        )
        
        sync_failed = TerminalStep(
            step_id="synchronization_failed",
            name="Fallo en Sincronización",
            terminal_status="FAILURE",
            description="Los traslados fueron exitosos pero hay inconsistencias"
        )
        
        # Definir flujo usando sintaxis tipo Airflow
        collect_data >> search_property >> property_check
        
        # Rutas condicionales desde verificación de propiedad
        property_check.when(property_found_complete) >> verify_ownership
        property_check.when(property_found_partial) >> partial_records
        property_check.when(lambda i, c: not property_found_complete(i, c) and not property_found_partial(i, c)) >> property_not_found
        
        # Flujo de verificación de propietario
        verify_ownership >> ownership_check
        ownership_check.when(ownership_verified) >> check_liens
        ownership_check.when(lambda i, c: not ownership_verified(i, c)) >> ownership_mismatch
        
        # Flujo de verificación de gravámenes
        check_liens >> liens_check
        liens_check.when(no_blocking_liens) >> calculate_fees
        liens_check.when(lambda i, c: not no_blocking_liens(i, c)) >> liens_prevent
        
        # Flujo de pago
        calculate_fees >> process_payment >> payment_check
        payment_check.when(payment_successful) >> rpp_transfer
        payment_check.when(lambda i, c: not payment_successful(i, c)) >> payment_failed
        
        # Flujo de traslados
        rpp_transfer >> rpp_check
        rpp_check.when(rpp_transfer_successful) >> catastro_transfer
        rpp_check.when(lambda i, c: not rpp_transfer_successful(i, c)) >> rpp_failed
        
        catastro_transfer >> catastro_check
        catastro_check.when(catastro_transfer_successful) >> synchronize
        catastro_check.when(lambda i, c: not catastro_transfer_successful(i, c)) >> catastro_failed
        
        # Flujo final
        synchronize >> sync_check
        sync_check.when(synchronization_successful) >> generate_certs >> success
        sync_check.when(lambda i, c: not synchronization_successful(i, c)) >> sync_failed
    
    # El workflow se auto-construye y valida al salir del context manager
    return workflow


# Ejemplo de uso
if __name__ == "__main__":
    workflow = create_traslado_dominio_unificado_dag_workflow()
    print(f"Workflow creado: {workflow.name}")
    print(f"ID: {workflow.workflow_id}")
    print(f"Total de pasos: {len(workflow.steps)}")
    print(f"Paso inicial: {workflow.start_step.name}")
    
    # Generar diagrama Mermaid
    print(f"\n=== DIAGRAMA MERMAID ===")
    print(workflow.to_mermaid())