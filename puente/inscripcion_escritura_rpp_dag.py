"""
Workflow de Inscripción de Escritura en RPP usando sintaxis DAG.
Proceso para inscribir escrituras públicas en el Registro Público de la Propiedad con sincronización catastral.

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
def validate_deed_document(inputs: Dict[str, Any]) -> ValidationResult:
    """Validar documento de escritura"""
    errors = []
    
    # Validar campos requeridos
    required_fields = [
        "numero_escritura", "fecha_escritura", "notaria_numero", 
        "notario_nombre", "tipo_acto", "valor_operacion"
    ]
    
    for field in required_fields:
        if not inputs.get(field):
            errors.append(f"Campo requerido faltante: {field}")
    
    # Validar formato de fecha
    fecha_escritura = inputs.get("fecha_escritura", "")
    if fecha_escritura:
        try:
            datetime.strptime(fecha_escritura, "%Y-%m-%d")
        except ValueError:
            errors.append("Fecha de escritura debe tener formato YYYY-MM-DD")
    
    # Validar valor de operación
    try:
        valor = float(inputs.get("valor_operacion", 0))
        if valor <= 0:
            errors.append("El valor de la operación debe ser mayor a 0")
    except ValueError:
        errors.append("El valor de la operación debe ser numérico")
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_parties(inputs: Dict[str, Any]) -> ValidationResult:
    """Validar información de las partes"""
    errors = []
    
    # Validar otorgante (vendedor/cedente)
    otorgante_nombre = inputs.get("otorgante_nombre", "")
    otorgante_rfc = inputs.get("otorgante_rfc", "")
    
    if not otorgante_nombre:
        errors.append("Nombre del otorgante es requerido")
    
    if otorgante_rfc and len(otorgante_rfc) not in [12, 13]:
        errors.append("RFC del otorgante debe tener 12 o 13 caracteres")
    
    # Validar adquirente (comprador/beneficiario)
    adquirente_nombre = inputs.get("adquirente_nombre", "")
    adquirente_rfc = inputs.get("adquirente_rfc", "")
    adquirente_curp = inputs.get("adquirente_curp", "")
    
    if not adquirente_nombre:
        errors.append("Nombre del adquirente es requerido")
    
    if adquirente_rfc and len(adquirente_rfc) not in [12, 13]:
        errors.append("RFC del adquirente debe tener 12 o 13 caracteres")
    
    if adquirente_curp and len(adquirente_curp) != 18:
        errors.append("CURP del adquirente debe tener 18 caracteres")
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


# Funciones de acción
def collect_deed_data(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Recopilar datos de la escritura"""
    return {
        "deed_data_collected": True,
        "deed_info": {
            "numero_escritura": inputs.get("numero_escritura"),
            "fecha_escritura": inputs.get("fecha_escritura"),
            "notaria_numero": inputs.get("notaria_numero"),
            "notario_nombre": inputs.get("notario_nombre"),
            "tipo_acto": inputs.get("tipo_acto"),
            "valor_operacion": float(inputs.get("valor_operacion", 0))
        },
        "parties_info": {
            "otorgante": {
                "nombre": inputs.get("otorgante_nombre"),
                "rfc": inputs.get("otorgante_rfc"),
                "domicilio": inputs.get("otorgante_domicilio")
            },
            "adquirente": {
                "nombre": inputs.get("adquirente_nombre"),
                "rfc": inputs.get("adquirente_rfc"),
                "curp": inputs.get("adquirente_curp"),
                "domicilio": inputs.get("adquirente_domicilio")
            }
        },
        "property_info": {
            "folio_real": inputs.get("folio_real"),
            "clave_catastral": inputs.get("clave_catastral"),
            "direccion": inputs.get("direccion_inmueble"),
            "superficie": inputs.get("superficie_inmueble")
        },
        "timestamp": datetime.utcnow().isoformat()
    }


def verify_notarial_authenticity(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Verificar autenticidad notarial"""
    deed_info = context.get("deed_info", {})
    notaria_numero = deed_info.get("notaria_numero")
    numero_escritura = deed_info.get("numero_escritura")
    
    # Simular verificación con colegio de notarios
    authentic = True  # En realidad consultaría sistema de notarios
    
    return {
        "notarial_verification_completed": True,
        "deed_authentic": authentic,
        "notary_validated": authentic,
        "verification_details": {
            "notaria_numero": notaria_numero,
            "notario_autorizado": deed_info.get("notario_nombre"),
            "escritura_verificada": numero_escritura,
            "fecha_verificacion": datetime.utcnow().isoformat()
        }
    }


def verify_property_ownership(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Verificar titularidad actual de la propiedad"""
    property_info = context.get("property_info", {})
    parties_info = context.get("parties_info", {})
    otorgante = parties_info.get("otorgante", {}).get("nombre", "")
    
    # Simular consulta de titularidad actual
    current_owner = "Juan Pérez López"  # En realidad consultaría RPP
    ownership_matches = otorgante.upper().strip() == current_owner.upper().strip()
    
    return {
        "ownership_verification_completed": True,
        "ownership_verified": ownership_matches,
        "current_registered_owner": current_owner,
        "deed_grantor": otorgante,
        "ownership_matches": ownership_matches,
        "verification_timestamp": datetime.utcnow().isoformat()
    }


def check_existing_liens(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Verificar gravámenes existentes"""
    property_info = context.get("property_info", {})
    folio_real = property_info.get("folio_real")
    
    # Simular consulta de gravámenes
    existing_liens = [
        {
            "tipo": "Hipoteca",
            "acreedor": "Banco Nacional",
            "monto": 850000.00,
            "status": "vigente"
        }
    ]
    
    return {
        "liens_check_completed": True,
        "liens_found": len(existing_liens) > 0,
        "existing_liens": existing_liens,
        "liens_total": len(existing_liens),
        "check_timestamp": datetime.utcnow().isoformat()
    }


def calculate_registration_fees(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Calcular derechos registrales"""
    deed_info = context.get("deed_info", {})
    valor_operacion = deed_info.get("valor_operacion", 0)
    
    # Cálculo de derechos registrales
    derecho_fijo = 2500.00  # Derecho fijo
    derecho_variable = valor_operacion * 0.003  # 0.3% del valor
    otros_derechos = 150.00  # Búsquedas y certificaciones
    
    total_derechos = derecho_fijo + derecho_variable + otros_derechos
    
    return {
        "fee_calculation_completed": True,
        "fee_breakdown": {
            "derecho_fijo": derecho_fijo,
            "derecho_variable": derecho_variable,
            "otros_derechos": otros_derechos,
            "total": total_derechos
        },
        "valor_operacion": valor_operacion,
        "calculation_timestamp": datetime.utcnow().isoformat()
    }


def execute_rpp_inscription(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecutar inscripción en RPP"""
    deed_info = context.get("deed_info", {})
    parties_info = context.get("parties_info", {})
    property_info = context.get("property_info", {})
    
    # Simular inscripción registral
    inscription_number = f"INS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "rpp_inscription_completed": True,
        "inscription_successful": True,
        "inscription_details": {
            "numero_inscripcion": inscription_number,
            "folio_real": property_info.get("folio_real"),
            "nuevo_propietario": parties_info.get("adquirente", {}).get("nombre"),
            "acto_inscrito": deed_info.get("tipo_acto"),
            "fecha_inscripcion": datetime.utcnow().isoformat()
        }
    }


def synchronize_catastral_record(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Sincronizar con registro catastral"""
    inscription_details = context.get("inscription_details", {})
    property_info = context.get("property_info", {})
    parties_info = context.get("parties_info", {})
    
    return {
        "catastral_sync_completed": True,
        "sync_successful": True,
        "catastral_update": {
            "clave_catastral": property_info.get("clave_catastral"),
            "nuevo_propietario_catastral": parties_info.get("adquirente", {}).get("nombre"),
            "folio_real_vinculado": property_info.get("folio_real"),
            "fecha_actualizacion": datetime.utcnow().isoformat()
        },
        "sync_timestamp": datetime.utcnow().isoformat()
    }


def generate_inscription_certificate(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Generar certificado de inscripción"""
    inscription_details = context.get("inscription_details", {})
    
    certificate_number = f"CERT-INS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "certificate_generated": True,
        "certificate_data": {
            "numero_certificado": certificate_number,
            "numero_inscripcion": inscription_details.get("numero_inscripcion"),
            "folio_real": inscription_details.get("folio_real"),
            "propietario": inscription_details.get("nuevo_propietario"),
            "acto": inscription_details.get("acto_inscrito"),
            "fecha_emision": datetime.utcnow().isoformat(),
            "vigencia": "Indefinida"
        }
    }


# Funciones condicionales
def deed_authentic(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que la escritura es auténtica"""
    return context.get("deed_authentic", False)


def ownership_verified(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que la titularidad coincide"""
    return context.get("ownership_verified", False)


def payment_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que el pago fue exitoso"""
    return context.get("payment_successful", False)


def inscription_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que la inscripción fue exitosa"""
    return context.get("inscription_successful", False)


def sync_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar que la sincronización fue exitosa"""
    return context.get("sync_successful", False)


def create_inscripcion_escritura_rpp_dag_workflow() -> Workflow:
    """Crear workflow de inscripción de escritura usando sintaxis DAG"""
    
    # Usar sintaxis DAG con context manager
    with Workflow(
        workflow_id="inscripcion_escritura_rpp_dag_v1",
        name="Inscripción de Escritura en RPP (DAG)",
        description="Proceso de inscripción de escrituras públicas usando sintaxis DAG"
    ) as workflow:
        
        # Definir operadores (se auto-registran)
        collect_deed = ActionStep(
            step_id="collect_deed_data",
            name="Recopilar Datos de Escritura",
            action=collect_deed_data,
            description="Captura de información de la escritura y las partes",
            required_inputs=[
                "numero_escritura", "fecha_escritura", "notaria_numero", "notario_nombre",
                "tipo_acto", "valor_operacion", "otorgante_nombre", "adquirente_nombre"
            ],
            requires_citizen_input=True,
            input_form={
                "title": "Inscripción de Escritura Pública",
                "description": "Proporcione los datos de la escritura para su inscripción",
                "fields": [
                    {
                        "id": "numero_escritura",
                        "label": "Número de Escritura",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "fecha_escritura",
                        "label": "Fecha de Escritura",
                        "type": "date",
                        "required": True
                    },
                    {
                        "id": "notaria_numero",
                        "label": "Número de Notaría",
                        "type": "number",
                        "required": True
                    },
                    {
                        "id": "notario_nombre",
                        "label": "Nombre del Notario",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "tipo_acto",
                        "label": "Tipo de Acto",
                        "type": "select",
                        "required": True,
                        "options": ["Compraventa", "Donación", "Herencia", "Permuta", "Adjudicación"]
                    },
                    {
                        "id": "valor_operacion",
                        "label": "Valor de la Operación",
                        "type": "number",
                        "required": True
                    },
                    {
                        "id": "otorgante_nombre",
                        "label": "Nombre del Otorgante",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "adquirente_nombre",
                        "label": "Nombre del Adquirente",
                        "type": "text",
                        "required": True
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
                    }
                ]
            }
        ).add_validation(validate_deed_document).add_validation(validate_parties)
        
        verify_notarial = ActionStep(
            step_id="verify_notarial_authenticity",
            name="Verificar Autenticidad Notarial",
            action=verify_notarial_authenticity,
            description="Verificación de la escritura con el Colegio de Notarios"
        )
        
        notarial_check = ConditionalStep(
            step_id="notarial_authenticity_check",
            name="Verificar Validez Notarial",
            description="Evaluar si la escritura es auténtica"
        )
        
        verify_ownership = ActionStep(
            step_id="verify_property_ownership",
            name="Verificar Titularidad",
            action=verify_property_ownership,
            description="Verificar que el otorgante es el propietario actual"
        )
        
        ownership_check = ConditionalStep(
            step_id="ownership_verification_check",
            name="Verificar Titularidad",
            description="Evaluar si la titularidad es correcta"
        )
        
        check_liens = ActionStep(
            step_id="check_existing_liens",
            name="Verificar Gravámenes Existentes",
            action=check_existing_liens,
            description="Consultar gravámenes que puedan afectar la inscripción"
        )
        
        calculate_fees = ActionStep(
            step_id="calculate_registration_fees",
            name="Calcular Derechos Registrales",
            action=calculate_registration_fees,
            description="Calcular derechos e impuestos por la inscripción"
        )
        
        process_payment = IntegrationStep(
            step_id="process_payment",
            name="Procesar Pago",
            service_name="payment_gateway",
            endpoint="https://api.payments.example/process-registration",
            description="Procesar pago de derechos registrales"
        )
        
        payment_check = ConditionalStep(
            step_id="payment_verification",
            name="Verificar Pago",
            description="Verificar que el pago fue procesado exitosamente"
        )
        
        execute_inscription = ActionStep(
            step_id="execute_rpp_inscription",
            name="Ejecutar Inscripción RPP",
            action=execute_rpp_inscription,
            description="Realizar inscripción en el Registro Público de la Propiedad"
        )
        
        inscription_check = ConditionalStep(
            step_id="inscription_result_check",
            name="Verificar Inscripción",
            description="Verificar que la inscripción fue exitosa"
        )
        
        sync_catastral = ActionStep(
            step_id="synchronize_catastral_record",
            name="Sincronizar Registro Catastral",
            action=synchronize_catastral_record,
            description="Actualizar información en el sistema catastral"
        )
        
        sync_check = ConditionalStep(
            step_id="sync_verification",
            name="Verificar Sincronización",
            description="Verificar sincronización catastral"
        )
        
        generate_certificate = ActionStep(
            step_id="generate_inscription_certificate",
            name="Generar Certificado",
            action=generate_inscription_certificate,
            description="Generar certificado de inscripción"
        )
        
        # Pasos terminales
        success = TerminalStep(
            step_id="inscription_completed",
            name="Inscripción Completada",
            terminal_status="SUCCESS",
            description="Escritura inscrita exitosamente con sincronización catastral"
        )
        
        notarial_invalid = TerminalStep(
            step_id="notarial_authentication_failed",
            name="Escritura No Auténtica",
            terminal_status="FAILURE",
            description="La escritura no pudo ser verificada como auténtica"
        )
        
        ownership_invalid = TerminalStep(
            step_id="ownership_verification_failed",
            name="Titularidad No Verificada",
            terminal_status="FAILURE",
            description="El otorgante no es el propietario registral actual"
        )
        
        payment_failed = TerminalStep(
            step_id="payment_failed",
            name="Pago Fallido",
            terminal_status="FAILURE",
            description="No se pudo procesar el pago de derechos"
        )
        
        inscription_failed = TerminalStep(
            step_id="inscription_failed",
            name="Inscripción Fallida",
            terminal_status="FAILURE",
            description="No se pudo completar la inscripción en RPP"
        )
        
        sync_failed = TerminalStep(
            step_id="sync_failed",
            name="Sincronización Fallida",
            terminal_status="FAILURE",
            description="Inscripción exitosa pero falló la sincronización catastral"
        )
        
        # Definir flujo usando sintaxis tipo Airflow
        collect_deed >> verify_notarial >> notarial_check
        
        # Verificación notarial
        notarial_check.when(deed_authentic) >> verify_ownership
        notarial_check.when(lambda i, c: not deed_authentic(i, c)) >> notarial_invalid
        
        # Verificación de titularidad
        verify_ownership >> ownership_check
        ownership_check.when(ownership_verified) >> check_liens
        ownership_check.when(lambda i, c: not ownership_verified(i, c)) >> ownership_invalid
        
        # Flujo de inscripción
        check_liens >> calculate_fees >> process_payment >> payment_check
        payment_check.when(payment_successful) >> execute_inscription
        payment_check.when(lambda i, c: not payment_successful(i, c)) >> payment_failed
        
        # Verificación de inscripción
        execute_inscription >> inscription_check
        inscription_check.when(inscription_successful) >> sync_catastral
        inscription_check.when(lambda i, c: not inscription_successful(i, c)) >> inscription_failed
        
        # Sincronización y finalización
        sync_catastral >> sync_check
        sync_check.when(sync_successful) >> generate_certificate >> success
        sync_check.when(lambda i, c: not sync_successful(i, c)) >> sync_failed
    
    # El workflow se auto-construye y valida al salir del context manager
    return workflow


# Ejemplo de uso
if __name__ == "__main__":
    workflow = create_inscripcion_escritura_rpp_dag_workflow()
    print(f"Workflow creado: {workflow.name}")
    print(f"ID: {workflow.workflow_id}")
    print(f"Total de pasos: {len(workflow.steps)}")
    print(f"Paso inicial: {workflow.start_step.name}")