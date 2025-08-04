# PUENTE Catastral - Workflows

Workflows específicos para la unificación de procesos del **Catastro** y **Registro Público de la Propiedad (RPP)** en una sola plataforma.

## Objetivo

Unificar los procesos catastrales y registrales mediante workflows automatizados basados en MuniStream.

## Arquitectura

- **Plataforma Base**: MuniStream (FastAPI + MongoDB)
- **Workflow Engine**: Sistema DAG con pasos especializados
- **Frontend**: Portales existentes extendidos con módulos catastrales
- **Integración**: APIs REST para interoperabilidad

## Componentes del Proyecto

### 1. Workflows Catastrales
- Actualización de información catastral
- Valuación de propiedades
- Emisión de certificados catastrales
- Notificación de cambios de valor

### 2. Workflows RPP (Registro Público de la Propiedad)
- Inscripción de escrituras
- Búsqueda de antecedentes registrales
- Expedición de certificados de libertad de gravamen
- Registro de hipotecas y gravámenes

### 3. Workflows Unificados
- Vinculación Catastro-RPP
- Cédula Única Registral-Catastral
- Búsqueda sistematizada automática
- Reportes estadísticos integrados

## Estructura del Proyecto

```
puente-workflows/
├── workflows/
│   ├── catastro/           # Workflows específicos del catastro
│   ├── rpp/                # Workflows del Registro Público
│   ├── unificados/         # Workflows que integran ambos sistemas
│   └── base/               # Clases base y utilidades
├── models/                 # Modelos de datos específicos
├── services/               # Servicios de integración
├── templates/              # Plantillas de documentos
└── examples/               # Ejemplos de uso
```

## Workflows Principales

### Procesos Catastrales
1. **Actualización Catastral**: Modificación de datos de propiedades
2. **Valuación de Inmuebles**: Proceso de avalúo oficial
3. **Certificación Catastral**: Emisión de certificados oficiales
4. **Notificación de Valores**: Comunicación de cambios de valor

### Procesos RPP
1. **Inscripción de Escrituras**: Registro de actos jurídicos
2. **Certificados de Libertad**: Emisión de certificados de gravámenes
3. **Registro de Hipotecas**: Inscripción de garantías reales
4. **Búsqueda de Antecedentes**: Consulta de historial registral

### Procesos Unificados
1. **Vinculación Automática**: Enlace folio real ↔ clave catastral
2. **Cédula Única**: Documento integrador de información
3. **Búsqueda Sistematizada**: Coincidencias automatizadas
4. **Reportes Estadísticos**: Análisis de vinculación

## Tecnologías

- **Backend**: Extensión de MuniStream (FastAPI + MongoDB)
- **Workflows**: Sistema DAG con steps especializados
- **Seguridad**: JWT + RBAC existente de MuniStream
- **APIs**: REST para interoperabilidad
- **Datos Geo**: PostgreSQL/PostGIS para información geoespacial

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/PuenteCatastral/puente-workflows.git
cd puente-workflows

# Instalar dependencias (requiere MuniStream base)
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
```

## Uso

```python
from workflows.unificados.vinculacion_catastro_rpp import create_vinculacion_workflow
from workflows.catastro.actualizacion_catastral import create_actualizacion_workflow

# Crear workflow de vinculación
workflow = create_vinculacion_workflow()

# Ejecutar con datos de prueba
instance = await workflow.execute_instance(instance_data)
```

## Contribuir

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nuevo-workflow`)
3. Commit de cambios (`git commit -m 'Agregar workflow X'`)
4. Push a la rama (`git push origin feature/nuevo-workflow`)
5. Crear Pull Request

## Documentación

- [Workflows Catastrales](docs/workflows-catastro.md)
- [Workflows RPP](docs/workflows-rpp.md)
- [API Reference](docs/api.md)
- [Guía de Integración](docs/integracion.md)

## Licencia

Proyecto gubernamental - Consultar términos específicos