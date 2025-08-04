---
layout: default
title: PUENTE Catastral - Documentación
---

# PUENTE Catastral - Documentación del Proyecto

Documentación técnica del proyecto **PUENTE Catastral**, sistema de modernización catastral que implementa la unificación de procesos del Catastro y el Registro Público de la Propiedad (RPP) mediante vinculación bidireccional en tiempo real.

## Navegación

### Arquitectura y Diseño
- **[Vinculación Tiempo Real](Vinculacion-Tiempo-Real.md)** - Especificación del sistema de sincronización bidireccional
- **[Integración MuniStream](Integracion-MuniStream.md)** - Arquitectura de integración con la plataforma MuniStream

### Desarrollo y Operaciones
- **[URLs de Debug](URLs-Debug.md)** - Endpoints y herramientas para desarrollo y testing

## Objetivos del Proyecto

### Objetivo Principal
Crear un sistema unificado que permita que cualquier operación en el **Catastro** se sincronice automáticamente con el **RPP** y viceversa, eliminando duplicación de datos y garantizando consistencia en tiempo real.

### Beneficios Técnicos
- **Vinculación automática** de registros entre sistemas mediante algoritmos de matching
- **Sincronización bidireccional** en tiempo real con garantías transaccionales
- **Eliminación de procesos manuales** de búsqueda y actualización entre sistemas
- **Documento único unificado** que consolida información de ambos sistemas
- **Rollback automático** con recuperación de estado ante fallos de sincronización

## Sistemas Involucrados

### Sistema Catastral
- **Función**: Registro de propiedades con fines tributarios y administrativos
- **Identificador**: Clave Catastral (formato: XX-XXX-XXX)
- **Datos**: Superficie, valor catastral, uso de suelo, propietario

### Registro Público de la Propiedad (RPP)
- **Función**: Registro legal de propiedades y actos jurídicos
- **Identificador**: Folio Real
- **Datos**: Escrituras, gravámenes, historial legal, propietario registral

### Tabla de Vinculación
- **Función**: Mapeo de correspondencia entre registros de ambos sistemas
- **Clave primaria**: UUID compartido único
- **Estados**: Sincronizado, Pendiente, Error

## Estado del Proyecto

### Fase Completada
- Análisis de workflows existentes en MuniStream
- Diseño de workflows unificados 
- Plan de vinculación bidireccional automática
- Implementación de clases base (CatastralActionStep, RPPActionStep)
- Ejemplos funcionales de workflows
- Pruebas de integración con MuniStream
- Verificación de compatibilidad completa

### Fase de Desarrollo
- Implementación de workflows específicos
- APIs de integración con sistemas externos
- Interfaz administrativa para gestión de vinculaciones
- Sistema de monitoreo y alertas

## Métricas y KPIs

### Métricas de Vinculación
- **Tasa de vinculación automática**: Meta 95%+ de registros vinculados automáticamente
- **Tiempo de sincronización**: Meta <5 segundos entre sistemas
- **Tasa de error**: Meta <1% de fallos en sincronización

### Métricas de Proceso
- **Reducción de tiempo de trámites**: Meta 70% menos tiempo vs. proceso manual
- **Satisfacción del usuario**: Meta 90%+ de usuarios satisfechos
- **Consistencia de datos**: Meta 99.9% de datos consistentes entre sistemas

## Enlaces de Referencia

- **Repositorio Principal**: [https://github.com/PuenteCatastral/puente-workflows](https://github.com/PuenteCatastral/puente-workflows)
- **MuniStream Backend**: http://localhost:8000 (entorno de desarrollo)
- **Admin Frontend**: http://localhost:3000 (entorno de desarrollo)
- **Citizen Portal**: http://localhost:5173 (entorno de desarrollo)

---
**Última actualización**: 2025-08-04  
**Versión del sistema**: 1.0.0-dev