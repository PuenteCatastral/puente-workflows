"""
Specialized workflow steps for Registro Público de la Propiedad (RPP) processes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
from .catastral_steps import BaseStep, ValidationResult


class RPPActionStep(BaseStep):
    """Action step specialized for RPP operations"""
    
    def __init__(self, 
                 step_id: str,
                 name: str,
                 action,
                 description: str = "",
                 required_rpp_fields: Optional[List[str]] = None,
                 requires_legal_validation: bool = True,
                 **kwargs):
        super().__init__(step_id, name, description)
        self.action = action
        self.required_rpp_fields = required_rpp_fields or []
        self.requires_legal_validation = requires_legal_validation
    
    def validate_rpp_inputs(self, inputs: Dict[str, Any]) -> ValidationResult:
        """Validate RPP-specific inputs"""
        errors = []
        
        # Check required RPP fields
        for field in self.required_rpp_fields:
            if field not in inputs or not inputs[field]:
                errors.append(f"Missing required RPP field: {field}")
        
        # Validate folio real format if present
        if "folio_real" in inputs:
            folio = inputs["folio_real"]
            if not self._validate_folio_real(folio):
                errors.append("Invalid folio real format")
        
        # Validate escritura number if present
        if "numero_escritura" in inputs:
            escritura = inputs["numero_escritura"]
            if not self._validate_escritura(escritura):
                errors.append("Invalid escritura number format")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def _validate_folio_real(self, folio: str) -> bool:
        """Validate folio real format"""
        # Simplified validation - adjust based on actual format
        return isinstance(folio, str) and len(folio) >= 8
    
    def _validate_escritura(self, escritura: str) -> bool:
        """Validate escritura number format"""
        return isinstance(escritura, str) and escritura.isdigit()


class FolioRegistrationStep(RPPActionStep):
    """Step for registering new folio real"""
    
    def __init__(self, step_id: str, name: str, **kwargs):
        super().__init__(
            step_id=step_id,
            name=name,
            action=self._register_folio,
            description="Register new folio real in RPP system",
            required_rpp_fields=["tipo_acto", "intervinientes"],
            **kwargs
        )
    
    def _register_folio(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Register new folio real"""
        tipo_acto = inputs.get("tipo_acto")
        intervinientes = inputs.get("intervinientes", [])
        
        # Generate new folio real
        nuevo_folio = f"FR-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
        
        registration_data = {
            "folio_registrado": True,
            "folio_real": nuevo_folio,
            "fecha_registro": datetime.now().isoformat(),
            "tipo_acto": tipo_acto,
            "numero_intervinientes": len(intervinientes),
            "intervinientes": intervinientes,
            "estatus": "registrado",
            "registrador": context.get("user_id", "SYSTEM"),
            "oficina_registro": inputs.get("oficina_registro", "CDMX-01"),
            "vigencia": "indefinida"
        }
        
        return registration_data


class EscrituraInscriptionStep(RPPActionStep):
    """Step for inscribing escrituras públicas"""
    
    def __init__(self, step_id: str, name: str, **kwargs):
        super().__init__(
            step_id=step_id,
            name=name,
            action=self._inscribe_escritura,
            description="Inscribe escritura pública in RPP",
            required_rpp_fields=["numero_escritura", "notario", "fecha_escritura"],
            **kwargs
        )
    
    def _inscribe_escritura(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Inscribe escritura pública"""
        numero_escritura = inputs.get("numero_escritura")
        notario = inputs.get("notario")
        fecha_escritura = inputs.get("fecha_escritura")
        
        # Generate inscription data
        inscription_data = {
            "escritura_inscrita": True,
            "numero_escritura": numero_escritura,
            "notario_autorizante": notario,
            "fecha_escritura": fecha_escritura,
            "fecha_inscripcion": datetime.now().isoformat(),
            "numero_inscripcion": f"INS-{uuid.uuid4().hex[:10].upper()}",
            "tipo_operacion": inputs.get("tipo_operacion", "compraventa"),
            "valor_operacion": inputs.get("valor_operacion"),
            "impuestos_causados": self._calculate_taxes(inputs.get("valor_operacion", 0)),
            "gravamenes_existentes": context.get("gravamenes", []),
            "observaciones": inputs.get("observaciones", "")
        }
        
        return inscription_data
    
    def _calculate_taxes(self, valor_operacion: float) -> Dict[str, float]:
        """Calculate taxes for the operation"""
        if valor_operacion <= 0:
            return {"isai": 0.0, "impuesto_registro": 0.0}
        
        # Simplified tax calculation
        isai = valor_operacion * 0.003  # 0.3%
        impuesto_registro = valor_operacion * 0.001  # 0.1%
        
        return {
            "isai": round(isai, 2),
            "impuesto_registro": round(impuesto_registro, 2),
            "total_impuestos": round(isai + impuesto_registro, 2)
        }


class CertificateIssuanceStep(RPPActionStep):
    """Step for issuing RPP certificates"""
    
    def __init__(self, step_id: str, name: str, certificate_type: str = "libertad_gravamen", **kwargs):
        super().__init__(
            step_id=step_id,
            name=name,
            action=self._issue_certificate,
            description=f"Issue {certificate_type} certificate",
            required_rpp_fields=["folio_real"] if certificate_type == "libertad_gravamen" else ["search_criteria"],
            **kwargs
        )
        self.certificate_type = certificate_type
    
    def _issue_certificate(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Issue RPP certificate"""
        certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        
        base_certificate_data = {
            "certificado_emitido": True,
            "numero_certificado": certificate_id,
            "tipo_certificado": self.certificate_type,
            "fecha_emision": datetime.now().isoformat(),
            "fecha_vencimiento": (datetime.now() + timedelta(days=30)).isoformat(),
            "emitido_por": context.get("user_id", "SYSTEM"),
            "oficina_emisora": inputs.get("oficina_registro", "CDMX-01"),
            "costo_certificado": self._get_certificate_cost(self.certificate_type),
            "validez_legal": "30 días naturales"
        }
        
        # Add specific data based on certificate type
        if self.certificate_type == "libertad_gravamen":
            base_certificate_data.update(self._get_libertad_gravamen_data(inputs))
        elif self.certificate_type == "antecedentes_registrales":
            base_certificate_data.update(self._get_antecedentes_data(inputs))
        
        return base_certificate_data
    
    def _get_certificate_cost(self, cert_type: str) -> float:
        """Get certificate cost based on type"""
        costs = {
            "libertad_gravamen": 185.00,
            "antecedentes_registrales": 125.00,
            "copia_certificada": 95.00,
            "busqueda_especifica": 155.00
        }
        return costs.get(cert_type, 100.00)
    
    def _get_libertad_gravamen_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific data for libertad de gravamen certificate"""
        folio_real = inputs.get("folio_real")
        
        return {
            "folio_real_consultado": folio_real,
            "gravamenes_encontrados": [],  # Simulate no liens found
            "estado_libertad": "LIBRE DE GRAVAMENES",
            "propietario_actual": inputs.get("nombre_propietario", ""),
            "descripcion_inmueble": inputs.get("descripcion_inmueble", ""),
            "superficie_registral": inputs.get("superficie_registral", ""),
            "colindancias": inputs.get("colindancias", [])
        }
    
    def _get_antecedentes_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific data for antecedentes registrales certificate"""
        return {
            "criterios_busqueda": inputs.get("search_criteria", {}),
            "antecedentes_encontrados": [
                {
                    "fecha": "2023-01-15",
                    "tipo_acto": "Compraventa",
                    "folio_real": f"FR-{uuid.uuid4().hex[:8].upper()}",
                    "partes": ["Juan Pérez", "María González"]
                }
            ],
            "periodo_consultado": inputs.get("periodo_busqueda", "10 años"),
            "total_antecedentes": 1
        }


class LienRegistrationStep(RPPActionStep):
    """Step for registering liens and encumbrances"""
    
    def __init__(self, step_id: str, name: str, **kwargs):
        super().__init__(
            step_id=step_id,
            name=name,
            action=self._register_lien,
            description="Register lien or encumbrance on property",
            required_rpp_fields=["folio_real", "tipo_gravamen", "monto_gravamen"],
            **kwargs
        )
    
    def _register_lien(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Register lien on property"""
        folio_real = inputs.get("folio_real")
        tipo_gravamen = inputs.get("tipo_gravamen")
        monto_gravamen = float(inputs.get("monto_gravamen", 0))
        
        lien_data = {
            "gravamen_registrado": True,
            "folio_real": folio_real,
            "numero_gravamen": f"GRAV-{uuid.uuid4().hex[:10].upper()}",
            "tipo_gravamen": tipo_gravamen,
            "monto_gravamen": monto_gravamen,
            "acreedor": inputs.get("acreedor", ""),
            "deudor": inputs.get("deudor", ""),
            "fecha_registro": datetime.now().isoformat(),
            "plazo_gravamen": inputs.get("plazo_anos", 0),
            "tasa_interes": inputs.get("tasa_interes", 0.0),
            "garantia_adicional": inputs.get("garantia_adicional", ""),
            "observaciones": inputs.get("observaciones_gravamen", ""),
            "estatus": "vigente"
        }
        
        return lien_data


# Condition functions for RPP workflows
def folio_exists(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Check if folio real exists"""
    return context.get("folio_found", False)

def escritura_valid(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Check if escritura is valid for inscription"""
    return context.get("escritura_valida", False)

def has_liens(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Check if property has liens"""
    gravamenes = context.get("gravamenes_encontrados", [])
    return len(gravamenes) > 0

def certificate_approved(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Check if certificate issuance is approved"""
    return context.get("certificado_aprobado", False)

def taxes_paid(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Check if required taxes are paid"""
    return context.get("impuestos_pagados", False)