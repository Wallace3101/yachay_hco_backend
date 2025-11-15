"""
Script de prueba para el sistema de reportes
Ejecutar desde la terminal con el entorno virtual activado:
python test_reports.py
"""

import requests
import json
import base64

# Configuración
BASE_URL = "http://localhost:8000/api"

# Tokens (debes reemplazar con tokens reales)
USER_TOKEN = "tu_token_de_usuario"
ADMIN_TOKEN = "tu_token_de_admin"


def test_create_report():
    """Prueba: Crear un reporte de usuario"""
    print("\n=== Test 1: Crear Reporte ===")
    
    url = f"{BASE_URL}/cultural/reports/create"
    headers = {
        "Authorization": f"Token {USER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "report_type": "CORRECCION",
        "motivo": "La IA identificó incorrectamente este plato como Ceviche cuando en realidad es Pachamanca Huanuqueña",
        "titulo": "Pachamanca Huanuqueña (Reporte Test)",
        "categoria": "GASTRONOMIA",
        "descripcion": "Plato emblemático que combina diversas carnes (res, carnero, cerdo), papas y hierbas, cocinado lentamente bajo tierra mediante piedras calientes.",
        "contexto_cultural": "Es un plato ceremonial y festivo, preparado para celebraciones comunitarias y familiares importantes.",
        "periodo_historico": "Prehispánico - Presente",
        "ubicacion": "Región andina de Huánuco",
        "significado": "Representa el vínculo sagrado con la Pachamama (Madre Tierra).",
        "confianza": 0.85
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()['data']['id']
    return None


def test_get_user_reports():
    """Prueba: Obtener reportes del usuario"""
    print("\n=== Test 2: Ver Mis Reportes ===")
    
    url = f"{BASE_URL}/cultural/reports/my-reports"
    headers = {
        "Authorization": f"Token {USER_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_get_all_reports_admin():
    """Prueba: Admin obtiene todos los reportes"""
    print("\n=== Test 3: Ver Todos los Reportes (Admin) ===")
    
    url = f"{BASE_URL}/cultural/reports/all?status=PENDIENTE"
    headers = {
        "Authorization": f"Token {ADMIN_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_approve_report(report_id):
    """Prueba: Admin aprueba un reporte"""
    print(f"\n=== Test 4: Aprobar Reporte #{report_id} ===")
    
    url = f"{BASE_URL}/cultural/reports/{report_id}/review"
    headers = {
        "Authorization": f"Token {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "action": "approve",
        "admin_notes": "Reporte válido. Elemento agregado al dataset correctamente."
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_reject_report(report_id):
    """Prueba: Admin rechaza un reporte"""
    print(f"\n=== Test 5: Rechazar Reporte #{report_id} ===")
    
    url = f"{BASE_URL}/cultural/reports/{report_id}/review"
    headers = {
        "Authorization": f"Token {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "action": "reject",
        "admin_notes": "El elemento ya existe en el dataset con información similar."
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_get_report_detail(report_id):
    """Prueba: Obtener detalle de un reporte"""
    print(f"\n=== Test 6: Ver Detalle del Reporte #{report_id} ===")
    
    url = f"{BASE_URL}/cultural/reports/{report_id}"
    headers = {
        "Authorization": f"Token {USER_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("="*60)
    print("SISTEMA DE REPORTES - TESTS")
    print("="*60)
    
    # Nota: Debes configurar los tokens antes de ejecutar
    if USER_TOKEN == "tu_token_de_usuario" or ADMIN_TOKEN == "tu_token_de_admin":
        print("\n⚠️  IMPORTANTE: Debes configurar los tokens reales antes de ejecutar")
        print("1. Inicia sesión como usuario y obtén el token")
        print("2. Inicia sesión como admin y obtén el token")
        print("3. Actualiza las variables USER_TOKEN y ADMIN_TOKEN en este archivo")
        print("\nPuedes obtener tokens usando:")
        print(f"POST {BASE_URL}/auth/login/")
        print("Body: {{\"email\": \"tu@email.com\", \"password\": \"tu_password\"}}")
    else:
        # Ejecutar tests
        report_id = test_create_report()
        
        if report_id:
            test_get_user_reports()
            test_get_all_reports_admin()
            test_get_report_detail(report_id)
            
            # Descomentar para aprobar
            # test_approve_report(report_id)
            
            # O descomentar para rechazar
            # test_reject_report(report_id)
        
    print("\n" + "="*60)
    print("TESTS COMPLETADOS")
    print("="*60)
