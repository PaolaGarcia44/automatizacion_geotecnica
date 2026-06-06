# DIAGNOSTICO Y SOLUCION - Datos no coinciden en P-1.xls (Column I)

## PROBLEMA IDENTIFICADO

El usuario reportó que los datos ingresados en el frontend **NO coinciden** con los datos que aparecen en la Columna I del archivo P-1.xls generado:

**Frontend (datos enviados):**
- Capa 1: "suelo de prueba" | Café oscuro
- Capa 2: "Suelo expansivo de color rojo" | Rojizo  
- Capa 3: "Arcilla arenosa color amarillo café" | Amarillo oscuro

**Archivo P-1.xls generado (Columna I):**
- "Capa vegetal y materia orgánica"
- "ceniza volcánica"
- "Limo arenoso..."

Esto indica que **los datos del template original NO se están siendo sobrescritos** con los datos del frontend.

## CAUSAS PROBABLES

1. **Column I no es la columna correcta en P-1.xls**
   - El código asumía que Column I contenía "Descripción Macroscópica"
   - Pero en el template P-1.xls, esta columna podría estar en otra ubicación

2. **Celdas merged (combinadas) en el template**
   - Las celdas de Columna I podrían estar merged verticalmente
   - `Range("I8")` no funciona correctamente con celdas merged
   - Necesita usar `Cells(row, col)` para acceso correcto

3. **Acceso incorrecto a las celdas**
   - El método usaba `worksheet.Range(f"I{row}")`
   - Este método puede no funcionar bien con celdas merged

## SOLUCIONES IMPLEMENTADAS

### 1. Búsqueda automática de la columna correcta
```python
# Ahora el código busca el encabezado "Descripción Macroscópica"
for col_idx in range(1, 20):  # Check columns A to S
    cell = worksheet.Cells(7, col_idx)
    cell_value = str(cell.Value) if cell.Value else ''
    if 'descripción macroscópica' in cell_value.lower():
        target_column = col_idx
        break
```

### 2. Uso de `Cells(row, col)` en lugar de `Range()`
```python
# Antes (problemático con celdas merged):
cell = worksheet.Range(f"I{row}")

# Después (funciona mejor con celdas merged):
cell = worksheet.Cells(row, target_column)
```

### 3. Logging detallado para diagnosticar problemas
```python
logger.info(f"[COLUMN_I] Layer {idx+1}: Writing to {col_letter}{row}")
logger.info(f"[COLUMN_I]   Soil Type: {soil_type[:50]}")
logger.info(f"[COLUMN_I]   Color: {color_name}")
```

## CAMBIOS DE CODIGO

### File: `backend/app/services/excel_service.py`

**Método actualizado:** `_fill_column_i_with_colors()`

**Cambios:**
1. Agregó búsqueda de columna por encabezado
2. Cambió de `Range()` a `Cells()` para mejor compatibilidad
3. Agregó logging extenso para debugging
4. Maneja excepciones de forma más robusta

## COMO VERIFICAR QUE FUNCIONA

1. **Generar nuevamente desde el frontend:**
   - Ingresa los mismos datos: 3 capas, colores diferentes
   - Genera el documento

2. **Verificar los logs del backend:**
   - Busca líneas que comiencen con `[COLUMN_I]`
   - Deberían mostrar exactamente qué se está escribiendo y dónde

3. **Abrir P-1.xls generado en Excel:**
   - Busca la columna "Descripción Macroscópica"
   - Verifica que tenga tus datos (no los del template)
   - Verifica que los colores sean correctos

## EJEMPLO DE LOGS ESPERADOS

```
[COLUMN_I] Starting to fill Column I. Pisos=3, Max rows=6, Total perforaciones=3
[COLUMN_I] Found 'Descripción' header at Column I, Row 7
[COLUMN_I] Layer 1: Writing to I8
[COLUMN_I]   Soil Type: suelo de prueba
[COLUMN_I]   Color: Café oscuro
[COLUMN_I]   Successfully wrote soil type to I8
[COLUMN_I]   Applying color Café oscuro (hex=5C3D2E, RGB=92,61,46)
[COLUMN_I]   Color and font applied successfully
[COLUMN_I] Layer 2: Writing to I10
[COLUMN_I]   Soil Type: Suelo expansivo de color rojo
[COLUMN_I]   Color: Rojizo
...
```

## ARCHIVOS MODIFICADOS

1. `backend/app/services/excel_service.py`
   - Método: `_fill_column_i_with_colors()`
   - Líneas: ~192-280

## PROXIMOS PASOS

1. Reiniciar el backend
2. Ejecutar nuevo test desde el frontend
3. Verificar logs
4. Abrir archivo generado en Excel
5. Si aún hay problemas, revisar logs para identificar causa específica

## NOTA IMPORTANTE

Si después de estos cambios los datos aún NO aparecen en P-1.xls, significa que:
- Posiblemente las celdas estén protegidas con contraseña
- O el template tiene una estructura radicalmente diferente
- En ese caso, será necesario abrir P-1.xls en Excel y examinar su estructura manualmente

---

**Última actualización:** 5 de junio de 2026
**Estado:** Cambios implementados, pendiente reinicio de backend y verificación
