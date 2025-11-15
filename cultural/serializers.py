# cultural/serializers.py
from rest_framework import serializers
from .models import CulturalItem, CulturalCategory, CulturalReport, ReportStatus, ReportType
import base64
from django.core.files.base import ContentFile

class CulturalItemSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    
    # Campos extra que NO existen en el modelo
    imagen_base64 = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = CulturalItem
        fields = [
            'id', 'titulo', 'categoria', 'categoria_display', 'confianza',
            'descripcion', 'contexto_cultural', 'periodo_historico',
            'ubicacion', 'significado', 'imagen', 'imagen_base64',
            'is_validated', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'imagen': {'read_only': True},
            'created_by': {'read_only': True},
        }
    
    def validate_imagen_base64(self, value):
        """Validar que el campo imagen_base64 sea base64 válido si se proporciona"""
        if value and value.strip():
            try:
                # Remover el prefijo data:image/...;base64, si existe
                if ';base64,' in value:
                    format_part, imgstr = value.split(';base64,')
                    base64.b64decode(imgstr)
                else:
                    base64.b64decode(value)
            except Exception as e:
                raise serializers.ValidationError(f"Formato de imagen base64 inválido: {str(e)}")
        return value
    
    def create(self, validated_data):
        # Extraer imagen_base64 antes de crear el objeto
        imagen_base64 = validated_data.pop('imagen_base64', None)
        
        # Establecer el usuario
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        # Crear el objeto sin imagen_base64
        cultural_item = super().create(validated_data)
        
        # Si hay imagen base64, convertirla y guardarla
        if imagen_base64 and imagen_base64.strip():
            try:
                # Remover el prefijo data:image/...;base64, si existe
                if ';base64,' in imagen_base64:
                    format_part, imgstr = imagen_base64.split(';base64,')
                    ext = format_part.split('/')[-1] if '/' in format_part else 'jpg'
                else:
                    imgstr = imagen_base64
                    ext = 'jpg'
                
                # Decodificar y crear archivo
                data = ContentFile(
                    base64.b64decode(imgstr), 
                    name=f'cultural_{cultural_item.id}.{ext}'
                )
                cultural_item.imagen = data
                cultural_item.save()
            except Exception as e:
                # Si falla, continuar sin imagen
                print(f"Error procesando imagen base64: {e}")
        
        return cultural_item
    
    def update(self, instance, validated_data):
        # Extraer imagen_base64 antes de actualizar el objeto
        imagen_base64 = validated_data.pop('imagen_base64', None)
        
        # Actualizar el objeto sin imagen_base64
        cultural_item = super().update(instance, validated_data)
        
        # Si hay nueva imagen base64, convertirla y guardarla
        if imagen_base64 and imagen_base64.strip():
            try:
                # Remover el prefijo data:image/...;base64, si existe
                if ';base64,' in imagen_base64:
                    format_part, imgstr = imagen_base64.split(';base64,')
                    ext = format_part.split('/')[-1] if '/' in format_part else 'jpg'
                else:
                    imgstr = imagen_base64
                    ext = 'jpg'
                
                # Decodificar y crear archivo
                data = ContentFile(
                    base64.b64decode(imgstr), 
                    name=f'cultural_{cultural_item.id}.{ext}'
                )
                cultural_item.imagen = data
                cultural_item.save()
            except Exception as e:
                print(f"Error procesando imagen base64 en actualización: {e}")
        
        return cultural_item


class CulturalAnalysisSerializer(serializers.Serializer):
    image = serializers.CharField(required=True)
    ubicacion = serializers.CharField(default="Huánuco, Perú", required=False)
    
    def validate_image(self, value):
        """Validar que el campo image no esté vacío y sea base64 válido"""
        if not value or value.strip() == "":
            raise serializers.ValidationError("El campo image no puede estar vacío")
        
        try:
            # Validar formato base64
            if ';base64,' in value:
                format_part, imgstr = value.split(';base64,')
                base64.b64decode(imgstr)
            else:
                base64.b64decode(value)
        except Exception as e:
            raise serializers.ValidationError(f"Formato de imagen base64 inválido: {str(e)}")
        
        return value
    
    def validate(self, data):
        """Validaciones adicionales a nivel del objeto completo"""
        # Puedes agregar validaciones que involucren múltiples campos aquí
        return data

class CulturalReportSerializer(serializers.ModelSerializer):
    """Serializer para crear reportes de usuario"""
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    reported_by_email = serializers.EmailField(source='reported_by.email', read_only=True)
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True, allow_null=True)
    
    # Campo para recibir imagen en base64
    imagen_base64 = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = CulturalReport
        fields = [
            'id', 'report_type', 'report_type_display', 'motivo',
            'titulo', 'categoria', 'categoria_display', 'descripcion',
            'contexto_cultural', 'periodo_historico', 'ubicacion',
            'significado', 'confianza', 'imagen', 'imagen_base64',
            'status', 'status_display', 'created_at', 'updated_at',
            'reported_by_email', 'reviewed_by_email', 'reviewed_at',
            'admin_notes', 'created_cultural_item'
        ]
        read_only_fields = [
            'id', 'status', 'created_at', 'updated_at', 'imagen',
            'reviewed_by_email', 'reviewed_at', 'admin_notes',
            'created_cultural_item'
        ]
    
    def validate_imagen_base64(self, value):
        """Validar que el campo imagen_base64 sea base64 válido si se proporciona"""
        if value and value.strip():
            try:
                if ';base64,' in value:
                    format_part, imgstr = value.split(';base64,')
                    base64.b64decode(imgstr)
                else:
                    base64.b64decode(value)
            except Exception as e:
                raise serializers.ValidationError(f"Formato de imagen base64 inválido: {str(e)}")
        return value
    
    def create(self, validated_data):
        # Extraer imagen_base64 antes de crear el objeto
        imagen_base64 = validated_data.pop('imagen_base64', None)
        
        # Establecer el usuario que reporta
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['reported_by'] = request.user
        
        # Crear el reporte
        report = super().create(validated_data)
        
        # Si hay imagen base64, convertirla y guardarla
        if imagen_base64 and imagen_base64.strip():
            try:
                if ';base64,' in imagen_base64:
                    format_part, imgstr = imagen_base64.split(';base64,')
                    ext = format_part.split('/')[-1] if '/' in format_part else 'jpg'
                else:
                    imgstr = imagen_base64
                    ext = 'jpg'
                
                data = ContentFile(
                    base64.b64decode(imgstr), 
                    name=f'report_{report.id}.{ext}'
                )
                report.imagen = data
                report.save()
            except Exception as e:
                print(f"Error procesando imagen base64 del reporte: {e}")
        
        return report


class CulturalReportListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar reportes"""
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    reported_by_email = serializers.EmailField(source='reported_by.email', read_only=True)
    
    class Meta:
        model = CulturalReport
        fields = [
            'id', 'report_type', 'report_type_display', 'titulo',
            'categoria', 'categoria_display', 'status', 'status_display',
            'created_at', 'reported_by_email', 'motivo',
            'descripcion', 'contexto_cultural', 'periodo_historico',
            'ubicacion', 'significado', 'confianza',
        ]


class ApproveReportSerializer(serializers.Serializer):
    """Serializer para aprobar o rechazar un reporte"""
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    admin_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data['action'] == 'reject' and not data.get('admin_notes'):
            raise serializers.ValidationError({
                'admin_notes': 'Las notas del administrador son requeridas al rechazar un reporte.'
            })
        return data