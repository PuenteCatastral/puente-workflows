"""
Workflow unificado para actualización catastral con sincronización automática al RPP.
Ejemplo práctico de vinculación en tiempo real.
"""

from typing import Dict, Any, List
from datetime import datetime
import uuid

# Import base classes
from ..base.catastral_steps import CatastralActionStep, ValidationResult


class AutoLinkingStep(CatastralActionStep):
    """Paso para vinculación automática en tiempo real"""
    
    def __init__(self, step_id: str, name: str, target_system: str = "rpp", **kwargs):
        super().__init__(
            step_id=step_id,
            name=name,
            action=self._perform_auto_linking,
            description=f"Vinculación automática con sistema {target_system.upper()}",
            **kwargs
        )
        self.target_system = target_system
    
    def _perform_auto_linking(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Realizar vinculación automática con el sistema objetivo"""
        
        # 1. Extraer datos de identificación
        datos_busqueda = self._extract_search_data(inputs, context)
        
        # 2. Buscar en sistema contrario
        resultado_busqueda = self._search_in_target_system(datos_busqueda)
        
        # 3. Evaluar coincidencias
        score = self._calculate_match_score(resultado_busqueda, datos_busqueda)
        
        # 4. Tomar decisión de vinculación
        decision_result = self._make_linking_decision(score, resultado_busqueda)
        
        return {
            "auto_linking_performed": True,
            "target_system": self.target_system,
            "search_criteria": datos_busqueda,
            "search_results": resultado_busqueda,
            "match_score": score,
            "linking_decision": decision_result["decision"],
            "linking_action": decision_result["action"],
            "linked_record": decision_result.get("linked_record"),
            "requires_manual_review": decision_result["decision"] == "manual_review",
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_search_data(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Extraer datos para búsqueda en sistema objetivo"""
        return {
            "nombre_propietario": inputs.get("nombre_propietario"),
            "direccion_inmueble": inputs.get("direccion_inmueble"), 
            "superficie_terreno": inputs.get("superficie_terreno"),
            "superficie_construccion": inputs.get("superficie_construccion"),
            "clave_catastral": inputs.get("clave_catastral"),
            "cuenta_catastral": inputs.get("cuenta_catastral")
        }
    
    def _search_in_target_system(self, datos_busqueda: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Buscar registros coincidentes en sistema objetivo"""
        # Simular búsqueda en RPP
        if self.target_system == "rpp":
            # Buscar por nombre y dirección
            return [{
                "folio_real": f"FR-{uuid.uuid4().hex[:8].upper()}",
                "propietario_registral": datos_busqueda["nombre_propietario"],
                "direccion_registral": datos_busqueda["direccion_inmueble"],
                "superficie_registral": datos_busqueda["superficie_terreno"],
                "fecha_registro": "2023-01-15",
                "tipo_operacion": "compraventa"
            }]
        
        return []
    
    def _calculate_match_score(self, resultados: List[Dict], datos_busqueda: Dict) -> float:
        """Calcular score de coincidencia"""
        if not resultados:
            return 0.0
        
        # Tomar el mejor resultado
        mejor_resultado = resultados[0]
        score = 0.0
        
        # Compare nombre (40% del score)
        if self._compare_names(datos_busqueda.get("nombre_propietario", ""), 
                              mejor_resultado.get("propietario_registral", "")):
            score += 0.4
        
        # Compare dirección (35% del score)
        if self._compare_addresses(datos_busqueda.get("direccion_inmueble", ""),
                                  mejor_resultado.get("direccion_registral", "")):
            score += 0.35
        
        # Compare superficie (25% del score)
        if self._compare_surfaces(datos_busqueda.get("superficie_terreno", ""),
                                 mejor_resultado.get("superficie_registral", "")):
            score += 0.25
        
        return score
    
    def _compare_names(self, name1: str, name2: str) -> bool:
        """Comparar nombres con tolerancia"""
        if not name1 or not name2:
            return False
        
        # Normalizar nombres
        n1 = self._normalize_name(name1)
        n2 = self._normalize_name(name2)
        
        # Comparación exacta
        if n1 == n2:
            return True
        
        # Comparación por palabras (al menos 2 palabras coinciden)
        words1 = set(n1.split())
        words2 = set(n2.split())
        common_words = words1.intersection(words2)
        
        return len(common_words) >= 2
    
    def _normalize_name(self, name: str) -> str:
        """Normalizar nombre para comparación"""
        return name.upper().strip().replace("  ", " ")
    
    def _compare_addresses(self, addr1: str, addr2: str) -> bool:
        """Comparar direcciones con tolerancia"""
        if not addr1 or not addr2:
            return False
        
        # Normalizar direcciones
        a1 = addr1.upper().replace(".", "").replace(",", "")
        a2 = addr2.upper().replace(".", "").replace(",", "")
        
        return a1 == a2
    
    def _compare_surfaces(self, surf1: str, surf2: str) -> bool:
        """Comparar superficies con tolerancia del 5%"""
        try:
            s1 = float(surf1) if surf1 else 0
            s2 = float(surf2) if surf2 else 0
            
            if s1 == 0 or s2 == 0:
                return False
            
            # Tolerancia del 5%
            diff_percentage = abs(s1 - s2) / max(s1, s2)
            return diff_percentage <= 0.05
        except:
            return False
    
    def _make_linking_decision(self, score: float, resultados: List[Dict]) -> Dict[str, Any]:
        """Tomar decisión de vinculación basada en score"""
        if score >= 0.95:
            return {
                "decision": "automatic_link",
                "action": "vincular_automaticamente",
                "linked_record": resultados[0] if resultados else None,
                "confidence": "high"
            }
        elif score >= 0.70:
            return {
                "decision": "manual_review", 
                "action": "enviar_a_revision_manual",
                "linked_record": resultados[0] if resultados else None,
                "confidence": "medium"
            }
        else:
            return {
                "decision": "create_new",
                "action": "crear_registro_nuevo",
                "linked_record": None,
                "confidence": "low"
            }


class SyncStep(CatastralActionStep):
    """Paso para sincronizar cambios con sistema objetivo"""
    
    def __init__(self, step_id: str, name: str, target_system: str = "rpp", **kwargs):
        super().__init__(
            step_id=step_id,
            name=name,
            action=self._perform_sync,
            description=f"Sincronizar cambios con sistema {target_system.upper()}",
            **kwargs
        )
        self.target_system = target_system
    
    def _perform_sync(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Sincronizar cambios con sistema objetivo"""
        
        # 1. Obtener registro vinculado
        linked_record = context.get("linked_record")
        if not linked_record:
            return {
                "sync_performed": False,
                "error": "No linked record found",
                "requires_manual_linking": True
            }
        
        # 2. Mapear campos entre sistemas
        mapped_data = self._map_fields(inputs, context)
        
        # 3. Aplicar cambios en sistema objetivo
        sync_result = self._apply_changes_to_target(linked_record, mapped_data)
        
        # 4. Verificar sincronización
        if sync_result["success"]:
            # Actualizar tabla de vinculación
            self._update_linking_table(inputs, linked_record, context)
            
            return {
                "sync_performed": True,
                "target_system": self.target_system,
                "target_record_id": linked_record.get("folio_real"),
                "changes_applied": mapped_data,
                "sync_timestamp": datetime.now().isoformat(),
                "rollback_possible": True
            }
        else:
            return {
                "sync_performed": False,
                "error": sync_result["error"],
                "requires_rollback": True,
                "manual_intervention_needed": True
            }
    
    def _map_fields(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Mapear campos del catastro al RPP"""
        return {
            "propietario_registral": inputs.get("nombre_propietario"),
            "direccion_registral": inputs.get("direccion_inmueble"),
            "superficie_registral": inputs.get("superficie_terreno"),
            "valor_registral": inputs.get("valor_catastral"),
            "uso_suelo_registral": inputs.get("uso_suelo"),
            "fecha_actualizacion": datetime.now().isoformat(),
            "origen_actualizacion": "catastro",
            "motivo_actualizacion": inputs.get("motivo_actualizacion", "actualizacion_catastral")
        }
    
    def _apply_changes_to_target(self, linked_record: Dict, mapped_data: Dict) -> Dict[str, Any]:
        """Aplicar cambios en el sistema objetivo"""
        # Simular actualización en RPP
        try:
            # En implementación real, aquí se haría la llamada a la API del RPP
            updated_record = {
                **linked_record,
                **mapped_data,
                "ultima_modificacion": datetime.now().isoformat(),
                "modificado_por": "sistema_catastral"
            }
            
            return {
                "success": True,
                "updated_record": updated_record,
                "operation_id": f"UPD-{uuid.uuid4().hex[:8].upper()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "rollback_needed": True
            }
    
    def _update_linking_table(self, inputs: Dict, linked_record: Dict, context: Dict):
        """Actualizar tabla de vinculación activa"""
        # En implementación real, esto actualizaría la base de datos
        linking_data = {
            "clave_catastral": inputs.get("clave_catastral"),
            "folio_real": linked_record.get("folio_real"),
            "estado_sincronizacion": "sincronizado",
            "ultima_actualizacion": datetime.now().isoformat(),
            "origen_ultimo_cambio": "catastro"
        }
        
        print(f"Actualizando tabla de vinculación: {linking_data}")


class RollbackStep(CatastralActionStep):
    """Paso para revertir cambios en caso de fallo de sincronización"""
    
    def __init__(self, step_id: str, name: str, **kwargs):
        super().__init__(
            step_id=step_id,
            name=name,
            action=self._perform_rollback,
            description="Revertir cambios por fallo de sincronización",
            **kwargs
        )
    
    def _perform_rollback(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Revertir cambios realizados"""
        original_data = context.get("original_catastral_data")
        
        if not original_data:
            return {
                "rollback_performed": False,
                "error": "No original data found for rollback"
            }
        
        # Revertir cambios en catastro
        rollback_result = self._revert_catastral_changes(original_data)
        
        return {
            "rollback_performed": rollback_result["success"],
            "reverted_data": original_data,
            "rollback_timestamp": datetime.now().isoformat(),
            "error": rollback_result.get("error")
        }
    
    def _revert_catastral_changes(self, original_data: Dict) -> Dict[str, Any]:
        """Revertir cambios en sistema catastral"""
        try:
            # En implementación real, aquí se revertiría en la base de datos
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Funciones condicionales
def linking_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar si la vinculación fue exitosa"""
    decision = context.get("linking_decision", "")
    return decision == "automatic_link"

def requires_manual_review(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar si requiere revisión manual"""
    return context.get("requires_manual_review", False)

def sync_successful(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar si la sincronización fue exitosa"""
    return context.get("sync_performed", False)

def sync_failed(inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Verificar si la sincronización falló"""
    return context.get("requires_rollback", False)


# Crear workflow de actualización catastral unificado
def create_actualizacion_catastral_unificada_workflow():
    """Crear workflow de actualización catastral con sincronización automática RPP"""
    
    # Simulación de clases base
    class Workflow:
        def __init__(self, workflow_id, name, description):
            self.workflow_id = workflow_id
            self.name = name
            self.description = description
            self.steps = {}
    
    class ConditionalStep:
        def __init__(self, step_id, name, description=""):
            self.step_id = step_id
            self.name = name
            self.description = description
    
    class TerminalStep:
        def __init__(self, step_id, name, terminal_status, description=""):
            self.step_id = step_id
            self.name = name
            self.terminal_status = terminal_status
            self.description = description
    
    # Crear workflow
    workflow = Workflow(
        workflow_id="actualizacion_catastral_unificada_v1",
        name="Actualización Catastral Unificada",
        description="Actualizar registro catastral con sincronización automática al RPP"
    )
    
    # Pasos del workflow
    
    # 1. Validar datos catastrales (existente)
    step_validate_catastral = CatastralActionStep(
        step_id="validate_catastral_data",
        name="Validar Datos Catastrales",
        action=lambda inputs, context: {
            "validation_passed": True,
            "original_catastral_data": inputs.copy(),  # Guardar datos originales para rollback
            "validated_at": datetime.now().isoformat()
        },
        required_cadastral_fields=["clave_catastral", "nombre_propietario", "direccion_inmueble"]
    )
    
    # 2. Actualizar registro catastral (existente)
    step_update_catastral = CatastralActionStep(
        step_id="update_catastral_record",
        name="Actualizar Registro Catastral",
        action=lambda inputs, context: {
            "catastral_updated": True,
            "updated_fields": list(inputs.keys()),
            "update_timestamp": datetime.now().isoformat(),
            "backup_created": True
        }
    )
    
    # 3. NUEVO: Vinculación automática con RPP
    step_auto_linking = AutoLinkingStep(
        step_id="auto_link_rpp",
        name="Vinculación Automática RPP",
        target_system="rpp"
    )
    
    # 4. Decisión de vinculación
    step_linking_decision = ConditionalStep(
        step_id="linking_decision",
        name="Decisión de Vinculación",
        description="Determinar acción basada en resultado de vinculación"
    )
    
    # 5. NUEVO: Sincronización con RPP
    step_sync_rpp = SyncStep(
        step_id="sync_with_rpp",
        name="Sincronizar con RPP",
        target_system="rpp"
    )
    
    # 6. Verificación de sincronización
    step_sync_check = ConditionalStep(
        step_id="sync_verification",
        name="Verificar Sincronización",
        description="Verificar que la sincronización fue exitosa"
    )
    
    # 7. NUEVO: Rollback en caso de fallo
    step_rollback = RollbackStep(
        step_id="rollback_changes",
        name="Revertir Cambios"
    )
    
    # 8. Notificación final
    step_notify = CatastralActionStep(
        step_id="send_notification",
        name="Enviar Notificación",
        action=lambda inputs, context: {
            "notification_sent": True,  
            "systems_updated": ["catastro", "rpp"] if context.get("sync_performed") else ["catastro"],
            "notification_channels": ["email", "sms"],
            "sent_at": datetime.now().isoformat()
        }
    )
    
    # Pasos terminales
    terminal_success = TerminalStep(
        step_id="update_completed",
        name="Actualización Completada",
        terminal_status="SUCCESS",
        description="Actualización catastral y sincronización RPP completadas"
    )
    
    terminal_manual_review = TerminalStep(
        step_id="pending_manual_review",
        name="Pendiente Revisión Manual",
        terminal_status="PENDING",
        description="Vinculación requiere revisión manual"
    )
    
    terminal_rollback_success = TerminalStep(
        step_id="rollback_completed",
        name="Cambios Revertidos",
        terminal_status="FAILURE",
        description="Cambios revertidos por fallo de sincronización"
    )
    
    # Definir flujo del workflow
    
    # Flujo principal
    # step_validate_catastral >> step_update_catastral >> step_auto_linking >> step_linking_decision
    
    # Rutas de decisión de vinculación
    # step_linking_decision.when(linking_successful) >> step_sync_rpp
    # step_linking_decision.when(requires_manual_review) >> terminal_manual_review
    
    # Verificación de sincronización
    # step_sync_rpp >> step_sync_check
    # step_sync_check.when(sync_successful) >> step_notify >> terminal_success
    # step_sync_check.when(sync_failed) >> step_rollback >> terminal_rollback_success
    
    print(f"Workflow creado: {workflow.workflow_id}")
    print("Pasos incluidos:")
    print("1. Validar datos catastrales")
    print("2. Actualizar registro catastral") 
    print("3. [NUEVO] Vinculación automática con RPP")
    print("4. [NUEVO] Sincronización bidireccional")
    print("5. [NUEVO] Rollback automático si falla")
    print("6. Notificación unificada")
    
    return workflow


# Ejemplo de uso
if __name__ == "__main__":
    workflow = create_actualizacion_catastral_unificada_workflow()
    
    # Datos de ejemplo
    sample_data = {
        "clave_catastral": "09-123-456",
        "cuenta_catastral": "1234567890123",
        "nombre_propietario": "Juan Pérez García",
        "direccion_inmueble": "Av. Reforma 123, Col. Centro, CDMX", 
        "superficie_terreno": "150.00",
        "superficie_construccion": "120.00",
        "valor_catastral": "1250000.00",
        "uso_suelo": "Habitacional",
        "motivo_actualizacion": "Cambio de propietario"
    }
    
    print(f"\nEjemplo de datos para actualización:")
    for key, value in sample_data.items():
        print(f"  {key}: {value}")
    
    print(f"\nEste workflow:")
    print("✅ Actualiza el registro catastral")
    print("✅ Busca automáticamente el registro en RPP")
    print("✅ Sincroniza cambios en tiempo real")
    print("✅ Revierte cambios si falla la sincronización")
    print("✅ Mantiene ambos sistemas consistentes")