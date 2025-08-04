# Integración PUENTE con MuniStream

Esta página documenta cómo el sistema PUENTE Catastral se integra con la plataforma MuniStream para aprovechar su infraestructura de workflows ya existente.

## 🎯 Estrategia de Integración

### ¿Por qué MuniStream?

**MuniStream** es una plataforma robusta de gestión de workflows gubernamentales que ya incluye:
- ✅ Motor de workflows DAG (Directed Acyclic Graph)
- ✅ Interface ciudadana completa
- ✅ Sistema de seguimiento en tiempo real
- ✅ Gestión de documentos y archivos
- ✅ Sistema de aprobaciones manuales/automáticas
- ✅ APIs REST completas
- ✅ Base de datos MongoDB + Redis

### Beneficios de la Integración
- **Desarrollo acelerado**: Aprovechar infraestructura existente
- **Costo reducido**: No reconstruir desde cero
- **Funcionalidades avanzadas**: Sistema maduro y probado
- **Escalabilidad**: Arquitectura probada en producción

## 🏗️ Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────┐
│                    PUENTE Catastral                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Workflows     │  │  Vinculación    │  │   Steps      │ │
│  │   Catastrales   │  │  Bidireccional  │  │ Personalizados│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     MuniStream Base                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Workflow       │  │   Document      │  │   Citizen    │ │
│  │   Engine        │  │  Management     │  │   Portal     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │     Admin       │  │    Database     │  │     APIs     │ │
│  │   Interface     │  │  (MongoDB)      │  │   (REST)     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Modelo de Workflows en MuniStream

### Estructura de Workflow
```json
{
  "workflow_id": "actualizacion_catastral_unificada_v1",
  "name": "Actualización Catastral Unificada",
  "description": "Actualizar catastro con sync automático al RPP",
  "version": "1.0.0",
  "status": "active",
  "steps": [
    {
      "step_id": "validate_catastral_data",
      "name": "Validar Datos Catastrales",
      "step_type": "action",
      "required_inputs": ["clave_catastral", "nombre_propietario"],
      "next_steps": ["auto_link_rpp"]
    },
    {
      "step_id": "auto_link_rpp", 
      "name": "Vinculación Automática RPP",
      "step_type": "integration",
      "integration_config": {
        "service": "puente_linking_service",
        "endpoint": "/api/catastro-rpp/auto-link"
      },
      "next_steps": ["sync_with_rpp", "manual_review"]
    }
  ],
  "start_step_id": "validate_catastral_data"
}
```

### Tipos de Steps Utilizados

#### 1. **action** - Acciones con formularios dinámicos
```json
{
  "step_type": "action",
  "requires_citizen_input": true,
  "input_form": {
    "title": "Datos Catastrales",
    "fields": [
      {
        "id": "clave_catastral",
        "label": "Clave Catastral", 
        "type": "text",
        "pattern": "^[0-9]{2}-[0-9]{3}-[0-9]{3}$",
        "required": true
      }
    ]
  }
}
```

#### 2. **integration** - Conexión con servicios PUENTE
```json
{
  "step_type": "integration",
  "integration_config": {
    "service": "puente_catastral_service",
    "endpoint": "/api/catastro/validate-property",
    "method": "POST",
    "timeout": 30
  }
}
```

#### 3. **conditional** - Lógica de decisión
```json
{
  "step_type": "conditional",
  "conditions": [
    {
      "condition": "linking_score >= 0.95",
      "next_step": "sync_automatically"
    },
    {
      "condition": "linking_score >= 0.70", 
      "next_step": "manual_review"
    },
    {
      "default": true,
      "next_step": "create_new_record"
    }
  ]
}
```

#### 4. **approval** - Aprobaciones manuales
```json
{
  "step_type": "approval",
  "approval_config": {
    "required_role": "catastral_supervisor",
    "timeout_hours": 48,
    "escalation_role": "catastral_manager"
  }
}
```

## 🔌 Servicios de Integración PUENTE

### 1. PUENTE Linking Service
**Propósito**: Vinculación automática Catastro-RPP

**Endpoints**:
```bash
POST /api/catastro-rpp/auto-link
POST /api/catastro-rpp/sync
POST /api/catastro-rpp/rollback
GET  /api/catastro-rpp/status/{link_id}
```

**Ejemplo de Request**:
```json
{
  "clave_catastral": "09-123-456",
  "nombre_propietario": "Juan Pérez García",
  "direccion_inmueble": "Av. Reforma 123, CDMX",
  "superficie_terreno": "150.00"
}
```

**Ejemplo de Response**:
```json
{
  "linking_performed": true,
  "match_score": 0.96,
  "linking_decision": "automatic_link",
  "linked_record": {
    "folio_real": "FR-2024-ABC123",
    "confidence": "high"
  },
  "uuid_compartido": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. PUENTE Catastral Service  
**Propósito**: Operaciones del sistema catastral

**Endpoints**:
```bash
POST /api/catastro/validate-property
POST /api/catastro/update-record
GET  /api/catastro/search
POST /api/catastro/calculate-value
```

### 3. PUENTE RPP Service
**Propósito**: Operaciones del RPP

**Endpoints**:
```bash
POST /api/rpp/inscribe-escritura
POST /api/rpp/generate-certificate  
GET  /api/rpp/search-folio
POST /api/rpp/register-lien
```

## 📋 Mapeo de Clases Python a MuniStream

### Conversión de CatastralActionStep
**Clase Python Original**:
```python
class CatastralActionStep(BaseStep):
    def __init__(self, step_id, name, action, 
                 required_cadastral_fields=None):
        # Implementación...
```

**Configuración MuniStream**:
```json
{
  "step_id": "validate_catastral_data",
  "step_type": "action", 
  "integration_config": {
    "service": "puente_catastral_service",
    "validation_fields": ["clave_catastral", "cuenta_catastral"]
  },
  "input_form": {
    "title": "Validación Catastral",
    "fields": [...]
  }
}
```

### Conversión de AutoLinkingStep
**Clase Python Original**:
```python
class AutoLinkingStep(CatastralActionStep):
    def _perform_auto_linking(self, inputs, context):
        # Algoritmo de vinculación...
        return resultado
```

**Configuración MuniStream**:
```json
{
  "step_id": "auto_link_rpp",
  "step_type": "integration",
  "integration_config": {
    "service": "puente_linking_service", 
    "endpoint": "/api/catastro-rpp/auto-link",
    "matching_algorithm": "name_address_surface",
    "confidence_threshold": 0.95
  }
}
```

## 🚀 Proceso de Despliegue

### Fase 1: Preparación de Servicios
1. **Desarrollar servicios de integración** PUENTE
2. **Configurar endpoints** en infraestructura
3. **Probar conectividad** con MuniStream

### Fase 2: Registro de Workflows
1. **Convertir workflows Python** a JSON MuniStream
2. **Registrar workflows** vía API
3. **Configurar formularios** dinámicos

### Fase 3: Testing y Validación
1. **Pruebas unitarias** de cada step
2. **Pruebas de integración** end-to-end
3. **Validación con datos reales**

### Fase 4: Producción
1. **Despliegue gradual** por tipo de trámite
2. **Monitoreo continuo** de performance
3. **Ajustes basados en feedback**

## 📊 Monitoreo y Métricas

### KPIs de Integración
- **Tiempo de respuesta** de servicios PUENTE < 2 segundos
- **Disponibilidad** de servicios > 99.5%
- **Tasa de éxito** de vinculaciones automáticas > 95%
- **Tiempo total de workflows** < 5 minutos para casos simples

### Logs y Auditoría
- **Logs estructurados** de todas las operaciones
- **Trazabilidad completa** de vinculaciones
- **Métricas en tiempo real** vía MuniStream dashboard
- **Alertas automáticas** por fallos críticos

## 🔧 Configuración de Desarrollo

### Variables de Entorno
```bash
# MuniStream
MUNISTREAM_BASE_URL=http://localhost:8000
MUNISTREAM_API_KEY=dev_key_123

# Servicios PUENTE  
PUENTE_LINKING_SERVICE=http://localhost:9001
PUENTE_CATASTRAL_SERVICE=http://localhost:9002
PUENTE_RPP_SERVICE=http://localhost:9003

# Base de datos
MONGODB_URL=mongodb://localhost:27017/civicstream
REDIS_URL=redis://localhost:6379
```

### Testing Local
```bash
# Iniciar MuniStream
docker-compose up -d

# Verificar servicios
curl http://localhost:8000/health

# Registrar workflow PUENTE
curl -X POST http://localhost:8000/api/v1/workflows/ -d @workflow_catastral.json

# Iniciar instancia de prueba
curl -X POST http://localhost:8000/api/v1/public/workflows/actualizacion_catastral_v1/start
```

---
**Estado de Integración**: ✅ Arquitectura validada y compatible  
**Próximos pasos**: Implementación de servicios PUENTE