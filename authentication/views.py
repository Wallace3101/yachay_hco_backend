# authentication/views.py
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, GoogleAuthSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Login exitoso',
            'token': token.key,
            'user': UserSerializer(user).data
        })
    return Response({
        'success': False,
        'message': 'Credenciales inválidas',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Registro exitoso',
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'message': 'Error en el registro',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    """
    Endpoint para autenticación con Google
    Verifica el ID Token de Google y crea/obtiene el usuario
    """
    serializer = GoogleAuthSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': 'Datos inválidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    id_token_str = serializer.validated_data['idToken']
    
    try:
        # 🔥 VERIFICAR EL TOKEN CON GOOGLE
        idinfo = id_token.verify_oauth2_token(
            id_token_str, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        # Verificar que el token es válido y para nuestra app
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logger.error(f"Invalid issuer: {idinfo['iss']}")
            raise ValueError('Token inválido')
        
        # Extraer información del usuario
        google_id = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name', '')
        given_name = idinfo.get('given_name', '')
        family_name = idinfo.get('family_name', '')
        picture = idinfo.get('picture', '')
        
        logger.info(f"Google auth attempt for email: {email}")
        
        if not email:
            return Response({
                'success': False,
                'message': 'No se pudo obtener el email de Google'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 🔥 BUSCAR O CREAR USUARIO
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,  # Usar email como username por defecto
                'first_name': given_name,
                'last_name': family_name,
                'is_active': True,
            }
        )
        
        if created:
            logger.info(f"New user created via Google: {email}")
            # Establecer un password unusable para usuarios de Google
            user.set_unusable_password()
            user.save()
        else:
            logger.info(f"Existing user logged in via Google: {email}")
            # Actualizar información si es necesario
            if not user.first_name and given_name:
                user.first_name = given_name
            if not user.last_name and family_name:
                user.last_name = family_name
            user.save()
        
        # Crear o obtener token de autenticación
        token, token_created = Token.objects.get_or_create(user=user)
        
        response_data = {
            'success': True,
            'message': 'Autenticación con Google exitosa',
            'token': token.key,
            'user': UserSerializer(user).data,
            'is_new_user': created
        }
        
        logger.info(f"Google auth successful for user: {user.id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except ValueError as e:
        logger.error(f"Google token verification failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Token de Google inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Unexpected error in Google auth: {str(e)}")
        return Response({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)