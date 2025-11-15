# cultural/views.py
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .services import analyze_cultural_image, OpenAIAnalysisError
from .serializers import (
    CulturalAnalysisSerializer, 
    CulturalItemSerializer, 
    CulturalReportSerializer,
    CulturalReportListSerializer,
    ApproveReportSerializer
)

from .models import CulturalItem, CulturalReport, ReportStatus
from django.utils import timezone
import json
import os
from django.conf import settings

import traceback

@api_view(['POST'])
@permission_classes([AllowAny])
def create_cultural_item(request):
    """Crear un nuevo elemento cultural"""
    serializer = CulturalItemSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        cultural_item = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Elemento cultural guardado exitosamente',
            'data': CulturalItemSerializer(cultural_item).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Error al guardar el elemento cultural',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cultural_items(request):
    """Obtener todos los elementos culturales, con filtro opcional por categoría"""
    category = request.query_params.get('category', None)
    
    queryset = CulturalItem.objects.all().order_by('-created_at')
    
    if category:
        queryset = queryset.filter(categoria=category)
    
    serializer = CulturalItemSerializer(queryset, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data
    })
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cultural_item_detail(request, id):
    """Obtener detalle de un elemento cultural específico"""
    try:
        cultural_item = CulturalItem.objects.get(id=id)
        serializer = CulturalItemSerializer(cultural_item)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    except CulturalItem.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Elemento cultural no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
        
@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_cultural_content(request):
    """
    Analiza una imagen cultural usando OpenAI Vision API
    """
    print("=== INICIO ANALYZE CULTURAL CONTENT ===")
    print(f"Datos recibidos: {list(request.data.keys()) if hasattr(request.data, 'keys') else 'No data keys'}")
    
    try:
        # Validar datos de entrada
        serializer = CulturalAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"ERRORES DE VALIDACIÓN DEL SERIALIZER: {serializer.errors}")
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print("Serializer validado exitosamente")
        
        # Obtener imagen base64
        image_base64 = serializer.validated_data['image']
        ubicacion = serializer.validated_data.get('ubicacion', 'Huánuco, Perú')
        
        print(f"Imagen base64 recibida (longitud: {len(image_base64)})")
        print(f"Ubicación: {ubicacion}")
        
        # Realizar análisis
        print("Llamando a analyze_cultural_image...")
        analysis_result = analyze_cultural_image(image_base64)
        print("Análisis completado exitosamente")
        
        return Response({
            'success': True,
            'message': 'Análisis completado exitosamente',
            'data': analysis_result
        }, status=status.HTTP_200_OK)
        
    except OpenAIAnalysisError as e:
        error_message = str(e)
        print(f"OpenAIAnalysisError: {error_message}")
        
        # Si es error de confianza baja, notificar sin datos
        if "Confianza insuficiente" in error_message:
            # Extraer la descripción del por qué no califica
            descripcion = error_message.split('). ', 1)[-1] if '). ' in error_message else error_message
            
            return Response({
                'success': False,
                'message': 'No se identificó como elemento cultural de Huánuco',
                'reason': descripcion,
                'data': None
            }, status=status.HTTP_200_OK)
        
        # Otros errores (API, timeout, auth) siguen siendo 400
        return Response({
            'success': False,
            'message': error_message,
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"Error inesperado en analyze_cultural_content: {e}")
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============== ENDPOINTS DE REPORTES ===============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report(request):
    """
    Crear un nuevo reporte de usuario.
    Permite reportar análisis incorrectos o sugerir nuevos elementos culturales.
    """
    serializer = CulturalReportSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        report = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Reporte creado exitosamente. Será revisado por un administrador.',
            'data': CulturalReportSerializer(report).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Error al crear el reporte',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_reports(request):
    """
    Obtener todos los reportes del usuario autenticado.
    """
    reports = CulturalReport.objects.filter(reported_by=request.user).order_by('-created_at')
    serializer = CulturalReportListSerializer(reports, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_reports(request):
    """
    Obtener todos los reportes (solo administradores).
    Puede filtrar por estado: ?status=PENDIENTE
    """
    status_filter = request.query_params.get('status', None)
    
    queryset = CulturalReport.objects.all().order_by('-created_at')
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    serializer = CulturalReportSerializer(queryset, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data,
        'count': queryset.count()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report_detail(request, report_id):
    """
    Obtener detalle de un reporte específico.
    Los usuarios solo pueden ver sus propios reportes.
    Los administradores pueden ver todos.
    """
    try:
        report = CulturalReport.objects.get(id=report_id)
        
        # Verificar permisos
        if not request.user.is_staff and report.reported_by != request.user:
            return Response({
                'success': False,
                'message': 'No tienes permiso para ver este reporte'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CulturalReportSerializer(report)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except CulturalReport.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Reporte no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def review_report(request, report_id):
    """
    Aprobar o rechazar un reporte (solo administradores).
    Si se aprueba, crea un nuevo elemento cultural y lo agrega a elementos_huanuco.json
    
    Body:
    {
        "action": "approve" | "reject",
        "admin_notes": "Notas opcionales del admin"
    }
    """
    try:
        report = CulturalReport.objects.get(id=report_id)
        
        # Verificar que el reporte esté pendiente
        if report.status != ReportStatus.PENDIENTE:
            return Response({
                'success': False,
                'message': f'Este reporte ya fue {report.get_status_display().lower()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar datos de entrada
        serializer = ApproveReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        action = serializer.validated_data['action']
        admin_notes = serializer.validated_data.get('admin_notes', '')
        
        # Actualizar el reporte
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.admin_notes = admin_notes
        
        if action == 'approve':
            # Aprobar el reporte
            report.status = ReportStatus.APROBADO
            
            # Crear el elemento cultural
            cultural_item = CulturalItem.objects.create(
                titulo=report.titulo,
                categoria=report.categoria,
                confianza=report.confianza,
                descripcion=report.descripcion,
                contexto_cultural=report.contexto_cultural,
                periodo_historico=report.periodo_historico,
                ubicacion=report.ubicacion,
                significado=report.significado,
                imagen=report.imagen,
                created_by=report.reported_by,
                is_validated=True,
                validated_by=request.user
            )
            
            # Vincular el elemento creado al reporte
            report.created_cultural_item = cultural_item
            report.save()
            
            # Agregar a elementos_huanuco.json
            success_json = add_to_elementos_json(cultural_item)
            
            return Response({
                'success': True,
                'message': 'Reporte aprobado exitosamente',
                'data': {
                    'report': CulturalReportSerializer(report).data,
                    'cultural_item': CulturalItemSerializer(cultural_item).data,
                    'added_to_json': success_json
                }
            }, status=status.HTTP_200_OK)
        
        else:  # action == 'reject'
            # Rechazar el reporte
            report.status = ReportStatus.RECHAZADO
            report.save()
            
            return Response({
                'success': True,
                'message': 'Reporte rechazado',
                'data': CulturalReportSerializer(report).data
            }, status=status.HTTP_200_OK)
        
    except CulturalReport.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Reporte no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error en review_report: {e}")
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error al procesar el reporte: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def add_to_elementos_json(cultural_item):
    """
    Agregar un elemento cultural al archivo elementos_huanuco.json
    """
    try:
        # Ruta al archivo JSON
        json_path = os.path.join(
            settings.BASE_DIR, 
            'cultural', 
            'data', 
            'elementos_huanuco.json'
        )
        
        # Leer el archivo actual
        with open(json_path, 'r', encoding='utf-8') as f:
            elementos = json.load(f)
        
        # Crear el nuevo elemento
        nuevo_elemento = {
            "titulo": cultural_item.titulo,
            "categoria": cultural_item.get_categoria_display(),
            "confianza": cultural_item.confianza,
            "descripcion": cultural_item.descripcion,
            "contexto_cultural": cultural_item.contexto_cultural,
            "periodo_historico": cultural_item.periodo_historico,
            "ubicacion": cultural_item.ubicacion,
            "significado": cultural_item.significado
        }
        
        # Verificar si ya existe (por título)
        existe = any(elem['titulo'] == nuevo_elemento['titulo'] for elem in elementos)
        
        if not existe:
            # Agregar el nuevo elemento
            elementos.append(nuevo_elemento)
            
            # Guardar el archivo actualizado
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(elementos, f, ensure_ascii=False, indent=2)
            
            print(f"Elemento '{cultural_item.titulo}' agregado a elementos_huanuco.json")
            return True
        else:
            print(f"Elemento '{cultural_item.titulo}' ya existe en elementos_huanuco.json")
            return False
            
    except Exception as e:
        print(f"Error al agregar elemento a JSON: {e}")
        traceback.print_exc()
        return False

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_cultural_items(request):
    """
    Obtener todos los elementos culturales creados por el usuario autenticado.
    """
    queryset = CulturalItem.objects.filter(created_by=request.user).order_by('-created_at')
    serializer = CulturalItemSerializer(queryset, many=True)

    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)