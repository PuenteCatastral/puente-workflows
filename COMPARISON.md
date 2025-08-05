# Comparación de Sintaxis: Antes vs Después (Estilo DAG)

## ✅ **NUEVA SINTAXIS - Estilo DAG (Recomendada)**

Similar a Airflow DAGs, usando context manager pattern:

```python
def create_mi_workflow() -> Workflow:
    # Usar sintaxis DAG con context manager
    with Workflow(
        workflow_id="mi_workflow_v1",
        name="Mi Workflow",
        description="Ejemplo usando sintaxis DAG"
    ) as workflow:
        
        # Los operadores se auto-registran al crearse
        collect = ActionStep(
            step_id="collect_data",
            name="Recopilar Datos",
            action=collect_data_function,
            requires_citizen_input=True,
            input_form={...}
        )
        
        process = ActionStep(
            step_id="process_data", 
            name="Procesar Datos",
            action=process_data_function
        )
        
        validation = ConditionalStep(
            step_id="validation_check",
            name="Verificar Validez"
        )
        
        success = TerminalStep(
            step_id="success",
            name="Proceso Exitoso",
            terminal_status="SUCCESS"
        )
        
        failure = TerminalStep(
            step_id="failure", 
            name="Proceso Fallido",
            terminal_status="FAILURE"
        )
        
        # Definir flujo usando >> operator (como Airflow)
        collect >> process >> validation
        
        # Flujos condicionales
        validation.when(data_valid) >> success
        validation.when(lambda i, c: not data_valid(i, c)) >> failure
    
    # Auto-construye y valida al salir del context manager
    return workflow
```

### **Ventajas de la Nueva Sintaxis:**
- ✅ **Familiar para desarrolladores de Airflow**
- ✅ **Auto-registro automático** - No necesitas `add_step()` manual
- ✅ **Auto-construcción** - Se construye y valida automáticamente
- ✅ **Más legible** - El contexto es claro
- ✅ **Menos código** - Elimina pasos manuales repetitivos

---

## 📝 **SINTAXIS ANTERIOR - Manual**

La forma anterior requería construcción manual:

```python
def create_mi_workflow() -> Workflow:
    # Crear workflow manualmente
    workflow = Workflow(
        workflow_id="mi_workflow_v1",
        name="Mi Workflow", 
        description="Ejemplo usando sintaxis manual"
    )
    
    # Crear pasos
    collect = ActionStep(...)
    process = ActionStep(...)
    validation = ConditionalStep(...)
    success = TerminalStep(...)
    failure = TerminalStep(...)
    
    # Definir flujo
    collect >> process >> validation
    validation.when(data_valid) >> success
    validation.when(lambda i, c: not data_valid(i, c)) >> failure
    
    # Registro manual requerido
    workflow.add_step(collect)
    workflow.add_step(process) 
    workflow.add_step(validation)
    workflow.add_step(success)
    workflow.add_step(failure)
    
    # Configuración manual requerida
    workflow.set_start(collect)
    
    # Construcción y validación manual
    workflow.build_graph()
    workflow.validate()
    
    return workflow
```

### **Desventajas de la Sintaxis Anterior:**
- ❌ **Código repetitivo** - Muchos `add_step()` manuales
- ❌ **Propenso a errores** - Fácil olvidar pasos
- ❌ **Menos familiar** - Sintaxis única de MuniStream
- ❌ **Más verboso** - Más líneas de código

---

## 🎯 **RESUMEN**

La nueva sintaxis DAG hace que MuniStream sea:

1. **Más familiar** para desarrolladores con experiencia en Airflow
2. **Menos propenso a errores** con auto-registro y auto-construcción
3. **Más legible** con el context manager pattern claro
4. **Más mantenible** con menos código boilerplate

### **Migración Gradual:**

- ✅ **Compatibilidad completa** - Ambas sintaxis funcionan
- ✅ **Sin breaking changes** - Workflows existentes siguen funcionando
- ✅ **Migración opcional** - Puedes migrar gradualmente
- ✅ **Mismo resultado** - Ambas producen workflows idénticos

**Recomendación:** Usar la nueva sintaxis DAG para nuevos workflows y migrar gradualmente los existentes.