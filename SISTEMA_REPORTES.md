# Sistema de Reportes de Elementos Culturales

## Descripción General

El sistema de reportes permite a los usuarios reportar análisis incorrectos de la IA o sugerir nuevos elementos culturales para agregar al dataset. Los administradores pueden revisar, aprobar o rechazar estos reportes.

## Flujo del Sistema

```
Usuario toma foto → IA analiza → 
  ├─ Análisis correcto → Usuario satisfecho
  └─ Análisis incorrecto → Usuario crea reporte →
       Admin revisa → 
         ├─ Aprueba → Se crea elemento + Se agrega a elementos_huanuco.json
         └─ Rechaza → Reporte archivado
```

## Endpoints Disponibles

### 1. Crear Reporte (Usuario Autenticado)
**POST** `/api/cultural/reports/create`

**Headers:**
```
Authorization: Token {user_token}
Content-Type: application/json
```

**Body:**
```json
{
  "report_type": "CORRECCION",  // o "NUEVO_ELEMENTO"
  "motivo": "La IA identificó incorrectamente este plato como X cuando en realidad es Y",
  "titulo": "Pachamanca Huanuqueña",
  "categoria": "GASTRONOMIA",
  "descripcion": "Plato emblemático que combina diversas carnes...",
  "contexto_cultural": "Es un plato ceremonial y festivo...",
  "periodo_historico": "Prehispánico - Presente",
  "ubicacion": "Región andina de Huánuco",
  "significado": "Representa el vínculo sagrado con la Pachamama...",
  "confianza": 0.85,
  "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Categorías Disponibles:**
- `GASTRONOMIA`
- `PATRIMONIO_ARQUEOLOGICO`
- `FLORA_MEDICINAL`
- `LEYENDAS_Y_TRADICIONES`
- `FESTIVIDADES`
- `DANZA`
- `MUSICA`
- `VESTIMENTA`
- `ARTE_POPULAR`
- `NATURALEZA_CULTURAL`
- `OTRO`

**Tipos de Reporte:**
- `CORRECCION`: Corrección de un análisis incorrecto
- `NUEVO_ELEMENTO`: Nuevo elemento cultural no presente en el dataset

**Response:**
```json
{
  "success": true,
  "message": "Reporte creado exitosamente. Será revisado por un administrador.",
  "data": {
    "id": 1,
    "report_type": "CORRECCION",
    "report_type_display": "Corrección de análisis incorrecto",
    "motivo": "La IA identificó incorrectamente...",
    "titulo": "Pachamanca Huanuqueña",
    "status": "PENDIENTE",
    "status_display": "Pendiente",
    "created_at": "2025-11-10T12:30:00.000Z",
    ...
  }
}
```

### 2. Ver Mis Reportes (Usuario Autenticado)
**GET** `/api/cultural/reports/my-reports`

**Headers:**
```
Authorization: Token {user_token}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "report_type": "CORRECCION",
      "report_type_display": "Corrección de análisis incorrecto",
      "titulo": "Pachamanca Huanuqueña",
      "categoria": "GASTRONOMIA",
      "categoria_display": "Gastronomía",
      "status": "PENDIENTE",
      "status_display": "Pendiente",
      "created_at": "2025-11-10T12:30:00.000Z",
      "reported_by_email": "usuario@example.com",
      "motivo": "La IA identificó incorrectamente..."
    }
  ]
}
```

### 3. Ver Detalle de Reporte
**GET** `/api/cultural/reports/{report_id}`

**Headers:**
```
Authorization: Token {user_token}
```

Los usuarios solo pueden ver sus propios reportes. Los admins pueden ver todos.

### 4. Ver Todos los Reportes (Solo Admin)
**GET** `/api/cultural/reports/all?status=PENDIENTE`

**Headers:**
```
Authorization: Token {admin_token}
```

**Query Params:**
- `status` (opcional): Filtrar por estado (`PENDIENTE`, `APROBADO`, `RECHAZADO`)

**Response:**
```json
{
  "success": true,
  "data": [...],
  "count": 5
}
```

### 5. Revisar Reporte (Solo Admin)
**POST** `/api/cultural/reports/{report_id}/review`

**Headers:**
```
Authorization: Token {admin_token}
Content-Type: application/json
```

**Body para Aprobar:**
```json
{
  "action": "approve",
  "admin_notes": "Reporte válido, elemento agregado al dataset"
}
```

**Body para Rechazar:**
```json
{
  "action": "reject",
  "admin_notes": "El elemento ya existe en el dataset / No cumple con los criterios"
}
```

**Response (Aprobado):**
```json
{
  "success": true,
  "message": "Reporte aprobado exitosamente",
  "data": {
    "report": {...},
    "cultural_item": {
      "id": 123,
      "titulo": "Pachamanca Huanuqueña",
      ...
    },
    "added_to_json": true
  }
}
```

## Estados de Reporte

- **PENDIENTE**: El reporte está esperando revisión del administrador
- **APROBADO**: El reporte fue aprobado, se creó el elemento cultural y se agregó al JSON
- **RECHAZADO**: El reporte fue rechazado por el administrador

## Panel de Administración Django

Los administradores también pueden gestionar reportes desde el panel de Django Admin:

1. Acceder a `/admin/cultural/culturalreport/`
2. Filtrar reportes por estado, tipo, categoría, etc.
3. Usar acciones masivas:
   - **Aprobar reportes seleccionados**: Aprueba múltiples reportes a la vez
   - **Rechazar reportes seleccionados**: Rechaza múltiples reportes a la vez

## Proceso de Aprobación

Cuando un administrador aprueba un reporte:

1. ✅ Se crea un nuevo `CulturalItem` en la base de datos
2. ✅ El elemento se marca como validado automáticamente
3. ✅ Se vincula al usuario que reportó (como creador)
4. ✅ Se agrega al archivo `cultural/data/elementos_huanuco.json`
5. ✅ El reporte se marca como APROBADO
6. ✅ Se registra la fecha y el admin que lo aprobó

## Ejemplo de Uso Completo

### Paso 1: Usuario toma foto y recibe análisis incorrecto
```javascript
// La IA responde incorrectamente
{
  "success": true,
  "data": {
    "titulo": "Ceviche",  // ❌ Incorrecto
    "categoria": "Gastronomía",
    ...
  }
}
```

### Paso 2: Usuario crea reporte
```javascript
fetch('/api/cultural/reports/create', {
  method: 'POST',
  headers: {
    'Authorization': 'Token abc123...',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    report_type: 'CORRECCION',
    motivo: 'La IA identificó esto como Ceviche, pero es Pachamanca Huanuqueña',
    titulo: 'Pachamanca Huanuqueña',
    categoria: 'GASTRONOMIA',
    descripcion: 'Plato emblemático...',
    contexto_cultural: 'Plato ceremonial...',
    periodo_historico: 'Prehispánico - Presente',
    ubicacion: 'Región andina de Huánuco',
    significado: 'Vínculo con la Pachamama...',
    confianza: 0.85,
    imagen_base64: '...'
  })
})
```

### Paso 3: Admin revisa y aprueba
```javascript
fetch('/api/cultural/reports/1/review', {
  method: 'POST',
  headers: {
    'Authorization': 'Token admin_token...',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    action: 'approve',
    admin_notes: 'Corrección válida, agregado al dataset'
  })
})
```

### Paso 4: Resultado
- ✅ Nuevo elemento creado en la BD
- ✅ Agregado a `elementos_huanuco.json`
- ✅ Disponible para futuras búsquedas de la IA
- ✅ Usuario notificado del estado

## Mejoras Futuras Sugeridas

1. **Notificaciones**: Enviar email al usuario cuando su reporte cambia de estado
2. **Sistema de puntos**: Recompensar a usuarios con reportes aprobados
3. **Votación comunitaria**: Permitir que otros usuarios voten por reportes
4. **Historial de cambios**: Registrar todas las modificaciones al dataset
5. **Categorías sugeridas**: IA que sugiere la categoría correcta
6. **Duplicados**: Detectar automáticamente reportes duplicados
7. **Estadísticas**: Dashboard para admins con métricas de reportes

## Notas Importantes

- Los reportes requieren autenticación (usuario registrado)
- Solo admins pueden aprobar/rechazar reportes
- La imagen es opcional pero recomendada
- Los elementos aprobados se marcan automáticamente como validados
- El archivo `elementos_huanuco.json` se actualiza automáticamente
- Se verifica que no existan duplicados por título antes de agregar al JSON
