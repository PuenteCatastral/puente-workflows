# URLs de Debug y Desarrollo

Esta página contiene todas las URLs y endpoints necesarios para el desarrollo y testing del sistema PUENTE Catastral.

## 🖥️ Aplicaciones Frontend

### Admin Frontend (Gestión Administrativa)
- **URL**: http://localhost:3000
- **Puerto**: 3000
- **Propósito**: Gestión de workflows, usuarios, aprobaciones, documentos
- **Tecnología**: Vite + React + TypeScript
- **Estado**: ✅ Operativo

### Citizen Portal (Portal Ciudadano)
- **URL**: http://localhost:5173
- **Puerto**: 5173
- **Propósito**: Inicio y seguimiento de trámites por ciudadanos
- **Tecnología**: Vite + React + TypeScript
- **Estado**: ✅ Operativo

## 🔌 Backend API

### API Principal
- **URL Base**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

### Endpoints Críticos para PUENTE

#### Workflows
```bash
# Listar todos los workflows
GET http://localhost:8000/api/v1/workflows/

# Crear nuevo workflow
POST http://localhost:8000/api/v1/workflows/

# Obtener workflow específico
GET http://localhost:8000/api/v1/workflows/{workflow_id}

# Workflows disponibles públicamente
GET http://localhost:8000/api/v1/public/workflows

# Actualizar workflow
PUT http://localhost:8000/api/v1/workflows/{workflow_id}
```

#### Instancias de Workflow
```bash
# Crear instancia privada
POST http://localhost:8000/api/v1/instances/

# Iniciar workflow público
POST http://localhost:8000/api/v1/public/workflows/{workflow_id}/start

# Seguimiento público de instancia
GET http://localhost:8000/api/v1/public/track/{instance_id}

# Estado detallado de instancia
GET http://localhost:8000/api/v1/instances/{instance_id}

# Historial de instancia
GET http://localhost:8000/api/v1/instances/{instance_id}/history
```

#### Documentos
```bash
# Subir documento
POST http://localhost:8000/api/v1/documents/upload

# Listar documentos
GET http://localhost:8000/api/v1/documents/

# Descargar documento
GET http://localhost:8000/api/v1/documents/{document_id}/download

# Analizar documento
POST http://localhost:8000/api/v1/documents/{document_id}/analyze
```

#### Administración
```bash
# Estadísticas del sistema
GET http://localhost:8000/api/v1/admin/stats

# Documentos pendientes de verificación
GET http://localhost:8000/api/v1/admin/pending-documents

# Aprobaciones pendientes
GET http://localhost:8000/api/v1/admin/pending-approvals

# Revisiones manuales
GET http://localhost:8000/api/v1/admin/manual-reviews
```

## 🗄️ Bases de Datos

### MongoDB (Base de Datos Principal)
- **Host**: localhost
- **Puerto**: 27017
- **URL de Conexión**: `mongodb://localhost:27017`
- **Base de Datos**: `civicstream`

### Redis (Cache y Sesiones)
- **Host**: localhost
- **Puerto**: 6379
- **URL de Conexión**: `redis://localhost:6379`

## 🧪 Comandos de Testing

### Health Checks
```bash
# Verificar salud del backend
curl -s http://localhost:8000/health

# Verificar frontend admin
curl -s -I http://localhost:3000

# Verificar citizen portal
curl -s -I http://localhost:5173
```

### Testing de Workflows
```bash
# Listar workflows con formato
curl -s http://localhost:8000/api/v1/workflows/ | python3 -m json.tool

# Crear workflow de prueba PUENTE
curl -X POST http://localhost:8000/api/v1/workflows/ \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "test_puente_catastral",
    "name": "Test PUENTE Catastral",
    "description": "Workflow de prueba para vinculación catastro-RPP",
    "version": "1.0.0",
    "steps": [...],
    "start_step_id": "validate_property"
  }'

# Iniciar instancia de workflow
curl -X POST http://localhost:8000/api/v1/public/workflows/fishing_permit_v1/start \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 🐳 Gestión de Contenedores Docker

### Comandos Básicos
```bash
# Ver estado de todos los contenedores
docker ps

# Ver logs del backend
docker logs civicstream-backend

# Ver logs del admin frontend
docker logs civicstream-admin-frontend-frontend-dev-1

# Ver logs del citizen portal
docker logs civicstream-citizen-portal-citizen-portal-1
```

### Iniciar/Parar Servicios
```bash
# Iniciar frontends si están parados
docker start civicstream-admin-frontend-frontend-dev-1
docker start civicstream-citizen-portal-citizen-portal-1

# Reiniciar todos los servicios principales
docker restart civicstream-backend civicstream-mongodb civicstream-redis

# Parar todos los contenedores MuniStream
docker stop civicstream-backend civicstream-mongodb civicstream-redis \
             civicstream-admin-frontend-frontend-dev-1 \
             civicstream-citizen-portal-citizen-portal-1
```

## 🔧 Troubleshooting

### Problemas Comunes

#### Frontend no carga
```bash
# Verificar que los contenedores estén corriendo
docker ps | grep frontend

# Si están parados, iniciarlos
docker start civicstream-admin-frontend-frontend-dev-1 civicstream-citizen-portal-citizen-portal-1

# Ver logs para diagnóstico
docker logs civicstream-admin-frontend-frontend-dev-1
```

#### API no responde
```bash
# Test básico de conectividad
curl -s http://localhost:8000/health

# Si falla, verificar contenedor backend
docker ps | grep backend
docker logs civicstream-backend

# Reiniciar si es necesario
docker restart civicstream-backend
```

#### Base de datos no conecta
```bash
# Verificar MongoDB
docker ps | grep mongo
docker logs civicstream-mongodb

# Test de conexión
mongosh --host localhost --port 27017
```

## 📝 Workflows de Prueba Creados

### Workflow PUENTE Catastral Simple
- **ID**: `actualizacion_catastral_simple_v1`
- **Estado**: `active`
- **URL**: http://localhost:8000/api/v1/workflows/actualizacion_catastral_simple_v1

### Instancias de Prueba Exitosas
- **Workflow**: `fishing_permit_v1` (ejemplo funcional)
- **Instance ID**: `ce8d40d4-013a-4815-880a-060e37c69323`
- **URL Seguimiento**: http://localhost:8000/api/v1/public/track/ce8d40d4-013a-4815-880a-060e37c69323
- **Estado**: `awaiting_input` (funcionando correctamente)

---
**Sistema Status**: ✅ Todos los servicios operativos  
**Última verificación**: 2025-08-04