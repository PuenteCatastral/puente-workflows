# Plan de Vinculación Catastro-RPP en Tiempo Real

## Concepto Principal

**Vinculación Bidireccional Automática**: Cada operación en un sistema (Catastro o RPP) desencadena automáticamente la actualización correspondiente en el otro sistema, manteniendo ambos sincronizados en tiempo real.

## Arquitectura de Vinculación

### 1. **Capa de Sincronización Automática**
```
Workflow Catastral  →  [Vinculador Bidireccional]  →  Sistema RPP
Sistema RPP  →  [Vinculador Bidireccional]  →  Workflow Catastral
```

### 2. **Componentes Clave**

#### A. **Identificador Único Compartido (UUID)**
- Cada propiedad tendrá un UUID único que conecta ambos sistemas
- Se crea en el primer registro (Catastro o RPP)
- Se propaga automáticamente al otro sistema

#### B. **Motor de Vinculación Bidireccional**
- **Detecta** cambios en cualquier sistema
- **Busca** el registro correspondiente en el otro sistema
- **Sincroniza** automáticamente los datos
- **Registra** la operación de vinculación

#### C. **Tabla de Correspondencias en Tiempo Real**
```sql
tabla_vinculacion_activa {
    uuid_propiedad: STRING (clave primaria)
    clave_catastral: STRING
    cuenta_catastral: STRING
    folio_real: STRING
    estado_sincronizacion: ENUM(sincronizado, pendiente, error)
    ultima_actualizacion: DATETIME
    origen_ultimo_cambio: ENUM(catastro, rpp)
}
```

## Workflows Unificados Propuestos

### 1. **Modificación de Registro Catastral Unificado**

#### Flujo Original (Solo Catastro):
```
Solicitud → Validar → Actualizar Catastro → Notificar → Fin
```

#### Flujo Unificado (Catastro + RPP):
```
Solicitud → Validar → Actualizar Catastro → [Buscar en RPP] → Actualizar RPP → Notificar Ambos → Fin
```

#### Pasos Adicionales:
1. **Paso de Búsqueda RPP**: Buscar folio real correspondiente
2. **Paso de Actualización RPP**: Actualizar datos registrales
3. **Paso de Confirmación**: Verificar sincronización exitosa
4. **Paso de Rollback**: Deshacer cambios si falla la sincronización

### 2. **Inscripción de Escritura Unificada**

#### Flujo Original (Solo RPP):
```
Escritura → Validar → Inscribir RPP → Generar Folio → Notificar → Fin
```

#### Flujo Unificado (RPP + Catastro):
```
Escritura → Validar → Inscribir RPP → [Buscar en Catastro] → Actualizar Catastro → Sincronizar → Notificar Ambos → Fin
```

### 3. **Registro de Propiedad Nueva (Unificado)**

#### Flujo Completo:
```
Solicitud → Crear UUID → Registrar en Catastro → Registrar en RPP → Vincular → Generar Cédula Única → Fin
```

## Estrategias de Vinculación por Casos

### Caso 1: **Propiedad Nueva**
- Se crea en cualquier sistema primero
- Se genera UUID único
- Se replica automáticamente en el otro sistema
- **Resultado**: Ambos sistemas sincronizados desde el inicio

### Caso 2: **Propiedad Existente Solo en Catastro**
- Al hacer cualquier modificación catastral
- **Trigger automático**: Buscar en RPP por criterios múltiples
- Si se encuentra → Vincular con UUID
- Si no se encuentra → Crear registro básico en RPP
- **Resultado**: Propiedad ahora existe en ambos sistemas

### Caso 3: **Propiedad Existente Solo en RPP**
- Al hacer cualquier modificación registral
- **Trigger automático**: Buscar en Catastro por criterios múltiples  
- Si se encuentra → Vincular con UUID
- Si no se encuentra → Crear registro básico en Catastro
- **Resultado**: Propiedad ahora existe en ambos sistemas

### Caso 4: **Propiedad Existente en Ambos (Sin Vincular)**
- Al modificar cualquier sistema
- **Búsqueda automática** del correspondiente
- **Vinculación automática** si coincidencia > 95%
- **Revisión manual** si coincidencia 70-95%
- **Creación duplicada** si coincidencia < 70%

## Algoritmo de Búsqueda y Vinculación

### Criterios de Búsqueda (En orden de prioridad):
1. **Dirección exacta** + **Propietario exacto** (Score: 100%)
2. **Dirección exacta** + **Propietario similar** (Score: 90%)
3. **Dirección similar** + **Propietario exacto** (Score: 85%)
4. **Superficie exacta** + **Propietario exacto** (Score: 95%)
5. **Referencia catastral en documentos RPP** (Score: 100%)

### Lógica de Decisión:
```python
if score >= 95%:
    vincular_automaticamente()
elif score >= 70%:
    enviar_a_revision_manual()
else:
    crear_registro_nuevo()
```

## Pasos Técnicos Específicos

### 1. **Paso de Vinculación Automática** (Nuevo tipo de paso)
```python
class AutoLinkingStep(ActionStep):
    def execute(self, context):
        # 1. Extraer datos de identificación
        datos_busqueda = extraer_datos_identificacion(context)
        
        # 2. Buscar en sistema contrario
        resultado_busqueda = buscar_en_sistema_contrario(datos_busqueda)
        
        # 3. Evaluar coincidencias
        score = calcular_score_coincidencia(resultado_busqueda)
        
        # 4. Decidir acción
        if score >= 95:
            vincular_automaticamente(resultado_busqueda)
        elif score >= 70:
            marcar_para_revision_manual()
        else:
            crear_registro_nuevo()
        
        return resultado
```

### 2. **Paso de Sincronización** (Nuevo tipo de paso)
```python
class SyncStep(ActionStep):
    def execute(self, context):
        # 1. Obtener datos actualizados
        datos_origen = context.get_datos_actualizados()
        
        # 2. Mapear campos entre sistemas
        datos_destino = mapear_campos(datos_origen, sistema_destino)
        
        # 3. Actualizar sistema contrario
        resultado_sync = actualizar_sistema_contrario(datos_destino)
        
        # 4. Verificar sincronización
        if not resultado_sync.success:
            rollback_cambios()
            raise SyncError()
        
        return resultado_sync
```

## Beneficios del Enfoque en Tiempo Real

### 1. **Consistencia de Datos**
- Los dos sistemas siempre están sincronizados
- No hay ventanas de inconsistencia
- Reduces errores por datos desactualizados

### 2. **Experiencia del Usuario**
- Un solo trámite modifica ambos sistemas
- Información siempre actualizada
- Procesos más rápidos

### 3. **Eficiencia Operativa**
- No necesidad de procesos batch de sincronización
- Menos recursos computacionales
- Menos intervención manual

### 4. **Trazabilidad Completa**
- Cada cambio queda registrado en ambos sistemas
- Auditoría completa de modificaciones
- Historia unificada de la propiedad

## Implementación por Fases

### Fase 1: **Infraestructura Base**
- Crear tabla de vinculación activa
- Implementar motor de búsqueda bidireccional
- Desarrollar algoritmos de coincidencia

### Fase 2: **Workflows Piloto**
- Modificación de datos catastrales
- Inscripción de escrituras
- Casos de prueba controlados

### Fase 3: **Expansión Completa**
- Todos los workflows catastrales
- Todos los workflows RPP
- Casos edge y excepciones

### Fase 4: **Optimización**
- Mejora de algoritmos de búsqueda
- Optimización de performance
- Inteligencia artificial para mejores coincidencias

## Manejo de Casos Especiales

### 1. **Fallo de Sincronización**
- **Rollback automático** de cambios
- **Notificación** al usuario del error
- **Queue de reintentos** automáticos
- **Escalación** a administrador si persiste

### 2. **Conflictos de Datos**
- **Identificación** de campos en conflicto
- **Priorización** por fecha de modificación
- **Notificación** a analista para resolución
- **Workflows** específicos de resolución de conflictos

### 3. **Propiedades Complejas**
- **Subdivisiones** y **fusiones** de lotes
- **Condominios** y propiedades horizontales
- **Bienes de dominio público**
- **Casos de herencias** y sucesiones

¿Te parece bien este enfoque? ¿Algún aspecto específico que quieras que desarrolle más?