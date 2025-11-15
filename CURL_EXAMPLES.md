# Ejemplos cURL para el Sistema de Reportes

## Variables de Configuración
```bash
# Configura estos valores
export BASE_URL="http://localhost:8000/api"
export USER_TOKEN="tu_token_de_usuario_aqui"
export ADMIN_TOKEN="tu_token_de_admin_aqui"
```

## 1. Crear Reporte (Usuario)

```bash
curl -X POST "${BASE_URL}/cultural/reports/create" \
  -H "Authorization: Token ${USER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "CORRECCION",
    "motivo": "La IA identificó incorrectamente este plato como Ceviche cuando en realidad es Pachamanca Huanuqueña",
    "titulo": "Pachamanca Huanuqueña",
    "categoria": "GASTRONOMIA",
    "descripcion": "Plato emblemático que combina diversas carnes (res, carnero, cerdo), papas y hierbas, cocinado lentamente bajo tierra mediante piedras calientes.",
    "contexto_cultural": "Es un plato ceremonial y festivo, preparado para celebraciones comunitarias y familiares importantes. Requiere un esfuerzo colectivo.",
    "periodo_historico": "Prehispánico - Presente",
    "ubicacion": "Región andina de Huánuco",
    "significado": "Representa el vínculo sagrado con la Pachamama (Madre Tierra), que actúa como un horno natural y fuente de los alimentos.",
    "confianza": 0.85
  }'
```

## 2. Crear Reporte de Nuevo Elemento

```bash
curl -X POST "${BASE_URL}/cultural/reports/create" \
  -H "Authorization: Token ${USER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "NUEVO_ELEMENTO",
    "motivo": "Este elemento cultural no está en el dataset actual",
    "titulo": "Danza de los Shacshas",
    "categoria": "DANZA",
    "descripcion": "Danza tradicional de la región de Huánuco que representa...",
    "contexto_cultural": "Se baila durante las festividades patronales...",
    "periodo_historico": "Colonial - Presente",
    "ubicacion": "Provincia de Huamalíes",
    "significado": "Representa la alegría y la unión comunitaria...",
    "confianza": 0.90
  }'
```

## 3. Ver Mis Reportes

```bash
curl -X GET "${BASE_URL}/cultural/reports/my-reports" \
  -H "Authorization: Token ${USER_TOKEN}"
```

## 4. Ver Todos los Reportes (Admin)

```bash
# Todos los reportes
curl -X GET "${BASE_URL}/cultural/reports/all" \
  -H "Authorization: Token ${ADMIN_TOKEN}"

# Solo reportes pendientes
curl -X GET "${BASE_URL}/cultural/reports/all?status=PENDIENTE" \
  -H "Authorization: Token ${ADMIN_TOKEN}"

# Solo reportes aprobados
curl -X GET "${BASE_URL}/cultural/reports/all?status=APROBADO" \
  -H "Authorization: Token ${ADMIN_TOKEN}"

# Solo reportes rechazados
curl -X GET "${BASE_URL}/cultural/reports/all?status=RECHAZADO" \
  -H "Authorization: Token ${ADMIN_TOKEN}"
```

## 5. Ver Detalle de un Reporte

```bash
# Reemplaza {REPORT_ID} con el ID del reporte
curl -X GET "${BASE_URL}/cultural/reports/1" \
  -H "Authorization: Token ${USER_TOKEN}"
```

## 6. Aprobar Reporte (Admin)

```bash
# Reemplaza {REPORT_ID} con el ID del reporte
curl -X POST "${BASE_URL}/cultural/reports/1/review" \
  -H "Authorization: Token ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "admin_notes": "Reporte válido. Elemento agregado al dataset correctamente."
  }'
```

## 7. Rechazar Reporte (Admin)

```bash
# Reemplaza {REPORT_ID} con el ID del reporte
curl -X POST "${BASE_URL}/cultural/reports/1/review" \
  -H "Authorization: Token ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reject",
    "admin_notes": "El elemento ya existe en el dataset. Favor de revisar antes de reportar."
  }'
```

## Flujo Completo de Ejemplo

```bash
# 1. Usuario crea un reporte
REPORT_RESPONSE=$(curl -s -X POST "${BASE_URL}/cultural/reports/create" \
  -H "Authorization: Token ${USER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "CORRECCION",
    "motivo": "Corrección necesaria",
    "titulo": "Elemento de Prueba",
    "categoria": "GASTRONOMIA",
    "descripcion": "Descripción de prueba",
    "contexto_cultural": "Contexto de prueba",
    "periodo_historico": "Presente",
    "ubicacion": "Huánuco",
    "significado": "Significado de prueba",
    "confianza": 0.85
  }')

# Extraer el ID del reporte
REPORT_ID=$(echo $REPORT_RESPONSE | jq -r '.data.id')
echo "Reporte creado con ID: $REPORT_ID"

# 2. Usuario verifica sus reportes
curl -X GET "${BASE_URL}/cultural/reports/my-reports" \
  -H "Authorization: Token ${USER_TOKEN}"

# 3. Admin ve reportes pendientes
curl -X GET "${BASE_URL}/cultural/reports/all?status=PENDIENTE" \
  -H "Authorization: Token ${ADMIN_TOKEN}"

# 4. Admin aprueba el reporte
curl -X POST "${BASE_URL}/cultural/reports/${REPORT_ID}/review" \
  -H "Authorization: Token ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "admin_notes": "Aprobado para pruebas"
  }'

# 5. Verificar que se creó el elemento cultural
curl -X GET "${BASE_URL}/cultural/items" \
  -H "Authorization: Token ${USER_TOKEN}"
```

## Obtener Tokens

Si aún no tienes tokens, primero debes autenticarte:

```bash
# Login como usuario
curl -X POST "${BASE_URL}/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "tu_password"
  }'

# Login como admin
curl -X POST "${BASE_URL}/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin_password"
  }'
```

La respuesta incluirá el token:
```json
{
  "success": true,
  "data": {
    "token": "abc123def456...",
    "user": {...}
  }
}
```

## Notas

- Todos los endpoints de reportes requieren autenticación
- Los endpoints de admin solo funcionan con tokens de usuarios con `is_staff=True`
- Los usuarios solo pueden ver sus propios reportes (excepto admins)
- Al aprobar un reporte, automáticamente se crea el elemento cultural y se agrega a `elementos_huanuco.json`
- Las imágenes pueden enviarse en formato base64 usando el campo `imagen_base64`
