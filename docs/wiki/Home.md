# PUENTE Catastral - Wiki del Proyecto

Bienvenido al wiki del proyecto **PUENTE Catastral**, un sistema de modernización catastral que unifica los procesos del Catastro y el Registro Público de la Propiedad (RPP) con vinculación bidireccional en tiempo real.

## 📋 Navegación Rápida

### 🏗️ Arquitectura y Diseño
- **[[Arquitectura General|Arquitectura-General]]** - Visión general del sistema PUENTE
- **[[Vinculación Tiempo Real|Vinculacion-Tiempo-Real]]** - Plan de sincronización bidireccional
- **[[Integración MuniStream|Integracion-MuniStream]]** - Cómo PUENTE se integra con MuniStream

### 💻 Desarrollo
- **[[URLs de Debug|URLs-Debug]]** - Enlaces y endpoints para desarrollo y testing
- **[[Workflows Implementados|Workflows-Implementados]]** - Workflows catastrales y RPP desarrollados
- **[[Guía de Desarrollo|Guia-Desarrollo]]** - Setup y mejores prácticas

### 📖 Procesos de Negocio
- **[[Procesos Catastrales|Procesos-Catastrales]]** - Trámites del sistema catastral
- **[[Procesos RPP|Procesos-RPP]]** - Trámites del Registro Público de la Propiedad
- **[[Casos de Uso|Casos-Uso]]** - Escenarios de vinculación y sincronización

## 🎯 Objetivos del Proyecto

### Objetivo Principal
Crear un sistema unificado que permita que cualquier operación en el **Catastro** se sincronice automáticamente con el **RPP** y viceversa, eliminando duplicación de datos y garantizando consistencia en tiempo real.

### Beneficios Clave
- ✅ **Vinculación automática** de registros entre sistemas
- ✅ **Sincronización bidireccional** en tiempo real  
- ✅ **Eliminación de procesos manuales** de búsqueda y actualización
- ✅ **Cédula única** que combina información de ambos sistemas
- ✅ **Rollback automático** en caso de fallos de sincronización

## 🏛️ Sistemas Involucrados

### Sistema Catastral
- **Función**: Registro de propiedades con fines tributarios
- **Identificador**: Clave Catastral (formato: XX-XXX-XXX)
- **Datos**: Superficie, valor catastral, uso de suelo, propietario

### Registro Público de la Propiedad (RPP)
- **Función**: Registro legal de propiedades y actos jurídicos
- **Identificador**: Folio Real
- **Datos**: Escrituras, gravámenes, historial legal, propietario registral

### Tabla de Vinculación
- **Función**: Conecta registros de ambos sistemas
- **Clave**: UUID compartido único
- **Estados**: Sincronizado, Pendiente, Error

## 🚀 Estado Actual

### ✅ Completado
- [x] Análisis de workflows existentes en MuniStream
- [x] Diseño de workflows unificados 
- [x] Plan de vinculación bidireccional automática
- [x] Implementación de clases base (CatastralActionStep, RPPActionStep)
- [x] Ejemplos funcionales de workflows
- [x] Pruebas de integración con MuniStream
- [x] Verificación de compatibilidad completa

### 🔄 En Desarrollo
- [ ] Implementación de workflows específicos
- [ ] APIs de integración con sistemas externos
- [ ] Interfaz administrativa para gestión de vinculaciones
- [ ] Sistema de monitoreo y alertas

## 📊 Métricas y KPIs

### Métricas de Vinculación
- **Tasa de vinculación automática**: Meta 95%+ de registros vinculados automáticamente
- **Tiempo de sincronización**: Meta <5 segundos entre sistemas
- **Tasa de error**: Meta <1% de fallos en sincronización

### Métricas de Proceso
- **Reducción de tiempo de trámites**: Meta 70% menos tiempo vs. proceso manual
- **Satisfacción del usuario**: Meta 90%+ de usuarios satisfechos
- **Consistencia de datos**: Meta 99.9% de datos consistentes entre sistemas

## 🔗 Enlaces Útiles

- **Repositorio Principal**: https://github.com/PuenteCatastral/puente-workflows
- **MuniStream Backend**: http://localhost:8000 (desarrollo)
- **Admin Frontend**: http://localhost:3000 (desarrollo)
- **Citizen Portal**: http://localhost:5173 (desarrollo)

---
**Última actualización**: 2025-08-04  
**Versión del sistema**: 1.0.0-dev