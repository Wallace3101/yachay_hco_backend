# ✅ SISTEMA DE REPORTES IMPLEMENTADO

## 📋 Resumen de la Implementación

Se ha implementado exitosamente un sistema completo de reportes que permite a los usuarios reportar análisis incorrectos de la IA o sugerir nuevos elementos culturales para agregar al dataset.

---

## 🎯 Funcionalidades Implementadas

### Para Usuarios (Autenticados)
✅ Crear reportes de corrección cuando la IA analiza incorrectamente
✅ Sugerir nuevos elementos culturales no presentes en el dataset
✅ Ver todos sus reportes enviados
✅ Ver el estado de cada reporte (Pendiente/Aprobado/Rechazado)
✅ Incluir motivo detallado y corrección sugerida
✅ Adjuntar imagen del elemento (base64)

### Para Administradores
✅ Ver todos los reportes del sistema
✅ Filtrar reportes por estado (Pendiente/Aprobado/Rechazado)
✅ Aprobar reportes válidos
✅ Rechazar reportes con justificación
✅ Agregar notas administrativas
✅ Aprobar/rechazar en batch desde el panel admin de Django
✅ Los reportes aprobados se agregan automáticamente a `elementos_huanuco.json`

---

## 📁 Archivos Creados/Modificados

### Modelos
- ✅ `cultural/models.py` - Agregado modelo `CulturalReport`
  - Tipos: CORRECCION, NUEVO_ELEMENTO
  - Estados: PENDIENTE, APROBADO, RECHAZADO
  - Campos completos del elemento cultural
  - Auditoría completa (usuario, admin, fechas)

### Serializers
- ✅ `cultural/serializers.py` - Agregados serializers:
  - `CulturalReportSerializer` - Para crear reportes
  - `CulturalReportListSerializer` - Para listar reportes
  - `ApproveReportSerializer` - Para aprobar/rechazar

### Views
- ✅ `cultural/views.py` - Agregadas vistas:
  - `create_report()` - Crear nuevo reporte
  - `get_user_reports()` - Ver reportes del usuario
  - `get_all_reports()` - Ver todos (admin)
  - `get_report_detail()` - Ver detalle de un reporte
  - `review_report()` - Aprobar/rechazar reporte
  - `add_to_elementos_json()` - Función helper para agregar a JSON

### URLs
- ✅ `cultural/urls.py` - Agregados endpoints:
  ```
  POST   /api/cultural/reports/create
  GET    /api/cultural/reports/my-reports
  GET    /api/cultural/reports/all
  GET    /api/cultural/reports/{id}
  POST   /api/cultural/reports/{id}/review
  ```

### Admin
- ✅ `cultural/admin.py` - Panel de administración con:
  - Listado de reportes con filtros
  - Acciones en batch (aprobar/rechazar múltiples)
  - Fieldsets organizados
  - Campos de solo lectura apropiados

### Migraciones
- ✅ `cultural/migrations/0004_culturalreport.py` - Migración aplicada ✅

### Documentación
- ✅ `SISTEMA_REPORTES.md` - Documentación completa del sistema
- ✅ `CURL_EXAMPLES.md` - Ejemplos de uso con cURL
- ✅ `test_reports.py` - Script de pruebas Python

---

## 🔄 Flujo del Sistema

```
┌─────────────────┐
│  Usuario toma   │
│      foto       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IA analiza     │
│   (OpenAI)      │
└────────┬────────┘
         │
         ▼
    ¿Correcto?
         │
    ┌────┴────┐
    │         │
   SÍ        NO
    │         │
    │         ▼
    │  ┌─────────────────┐
    │  │ Usuario crea    │
    │  │    REPORTE      │
    │  └────────┬────────┘
    │           │
    │           ▼
    │  ┌─────────────────┐
    │  │  Admin revisa   │
    │  └────────┬────────┘
    │           │
    │      ┌────┴────┐
    │      │         │
    │   APRUEBA  RECHAZA
    │      │         │
    │      ▼         ▼
    │  ┌─────┐  ┌─────┐
    │  │ +DB │  │ FIN │
    │  │+JSON│  └─────┘
    │  └──┬──┘
    │     │
    ▼     ▼
┌─────────────────┐
│  Dataset        │
│  actualizado    │
└─────────────────┘
```

---

## 🗄️ Estructura de Base de Datos

### Tabla: `cultural_culturalreport`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | ID único |
| reported_by_id | FK | Usuario que reporta |
| report_type | String | CORRECCION o NUEVO_ELEMENTO |
| motivo | Text | Razón del reporte |
| titulo | String | Título del elemento |
| categoria | String | Categoría (choices) |
| descripcion | Text | Descripción completa |
| contexto_cultural | Text | Contexto cultural |
| periodo_historico | String | Período histórico |
| ubicacion | String | Ubicación geográfica |
| significado | Text | Significado cultural |
| confianza | Float | Nivel de confianza (0-1) |
| imagen | ImageField | Imagen del elemento |
| status | String | PENDIENTE/APROBADO/RECHAZADO |
| created_at | DateTime | Fecha de creación |
| updated_at | DateTime | Fecha de actualización |
| reviewed_by_id | FK | Admin que revisó |
| reviewed_at | DateTime | Fecha de revisión |
| admin_notes | Text | Notas del admin |
| created_cultural_item_id | FK | Elemento creado (si aprobado) |

---

## 🔐 Permisos y Seguridad

| Endpoint | Permiso Requerido | Descripción |
|----------|-------------------|-------------|
| `POST /reports/create` | `IsAuthenticated` | Cualquier usuario autenticado |
| `GET /reports/my-reports` | `IsAuthenticated` | Solo reportes propios |
| `GET /reports/all` | `IsAdminUser` | Solo administradores |
| `GET /reports/{id}` | `IsAuthenticated` | Propio o admin |
| `POST /reports/{id}/review` | `IsAdminUser` | Solo administradores |

---

## 📝 Ejemplo de Uso

### 1. Usuario crea reporte
```bash
POST /api/cultural/reports/create
Authorization: Token abc123...

{
  "report_type": "CORRECCION",
  "motivo": "La IA identificó esto como X cuando es Y",
  "titulo": "Pachamanca Huanuqueña",
  "categoria": "GASTRONOMIA",
  "descripcion": "...",
  "contexto_cultural": "...",
  "periodo_historico": "Prehispánico - Presente",
  "ubicacion": "Huánuco",
  "significado": "...",
  "confianza": 0.85,
  "imagen_base64": "data:image/jpeg;base64,..."
}
```

### 2. Admin aprueba reporte
```bash
POST /api/cultural/reports/1/review
Authorization: Token admin_token...

{
  "action": "approve",
  "admin_notes": "Válido, agregado al dataset"
}
```

### 3. Sistema automáticamente:
- ✅ Crea `CulturalItem` en BD
- ✅ Marca como validado
- ✅ Agrega a `elementos_huanuco.json`
- ✅ Vincula reporte con elemento creado

---

## 🎨 Categorías Soportadas

- ✅ Gastronomía
- ✅ Patrimonio Arqueológico
- ✅ Flora Medicinal
- ✅ Leyendas y Tradiciones
- ✅ Festividades
- ✅ Danza
- ✅ Música
- ✅ Vestimenta
- ✅ Arte Popular
- ✅ Naturaleza/Cultural
- ✅ Otro

---

## 🧪 Cómo Probar

### Opción 1: Django Admin
```bash
python manage.py runserver
# Ir a http://localhost:8000/admin/cultural/culturalreport/
```

### Opción 2: API con cURL
```bash
# Ver CURL_EXAMPLES.md para ejemplos completos
curl -X POST http://localhost:8000/api/cultural/reports/create \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @reporte.json
```

### Opción 3: Script Python
```bash
# Configurar tokens en test_reports.py
python test_reports.py
```

---

## 📊 Estados del Reporte

| Estado | Descripción |
|--------|-------------|
| 🟡 PENDIENTE | Esperando revisión del administrador |
| 🟢 APROBADO | Aprobado y agregado al dataset |
| 🔴 RECHAZADO | Rechazado por el administrador |

---

## 🚀 Próximos Pasos Sugeridos

1. **Frontend**
   - Crear formulario de reporte en la app móvil/web
   - Mostrar estado de reportes al usuario
   - Notificaciones cuando cambia el estado

2. **Notificaciones**
   - Email cuando se crea un reporte (a admins)
   - Email cuando cambia estado (a usuario)
   - Notificaciones push en app móvil

3. **Mejoras**
   - Sistema de puntos/gamificación
   - Votación comunitaria de reportes
   - Detección automática de duplicados
   - Dashboard de estadísticas para admins
   - Exportar reportes a CSV/Excel

4. **Validaciones**
   - IA que pre-valida reportes
   - Sugerencias automáticas de categoría
   - Detección de contenido inapropiado

---

## 📚 Documentación Adicional

- Ver `SISTEMA_REPORTES.md` para documentación completa de API
- Ver `CURL_EXAMPLES.md` para ejemplos de cURL
- Ver `test_reports.py` para scripts de prueba

---

## ✨ Características Destacadas

1. **Integración Automática**: Los reportes aprobados se agregan automáticamente a `elementos_huanuco.json`
2. **Auditoría Completa**: Se registra quién, cuándo y por qué se aprobó/rechazó
3. **Permisos Granulares**: Usuarios ven solo sus reportes, admins ven todo
4. **Panel Admin Potente**: Acciones en batch, filtros avanzados
5. **Base64 Support**: Imágenes pueden enviarse directamente en base64
6. **Validación Duplicados**: Verifica que no existan títulos duplicados en JSON
7. **Estado Inmutable**: No se puede revisar dos veces el mismo reporte

---

## 🎉 Implementación Completada

El sistema de reportes está **100% funcional** y listo para usar. Todas las migraciones han sido aplicadas y todos los endpoints están operativos.

**Fecha de implementación**: 10 de Noviembre de 2025
