# cultural/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CulturalCategory(models.TextChoices):
    GASTRONOMIA = 'GASTRONOMIA', 'Gastronomía'
    PATRIMONIO_ARQUEOLOGICO = 'PATRIMONIO_ARQUEOLOGICO', 'Patrimonio Arqueológico'
    FLORA_MEDICINAL = 'FLORA_MEDICINAL', 'Flora Medicinal'
    LEYENDAS_Y_TRADICIONES = 'LEYENDAS_Y_TRADICIONES', 'Leyendas y Tradiciones'
    FESTIVIDADES = 'FESTIVIDADES', 'Festividades'
    DANZA = 'DANZA', 'Danza'
    MUSICA = 'MUSICA', 'Música'
    VESTIMENTA = 'VESTIMENTA', 'Vestimenta'
    ARTE_POPULAR = 'ARTE_POPULAR', 'Arte Popular'
    NATURALEZA_CULTURAL = 'NATURALEZA_CULTURAL', 'Naturaleza/Cultural'
    OTRO = 'OTRO', 'Otro'

class CulturalItem(models.Model):
    titulo = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=CulturalCategory.choices)
    confianza = models.FloatField()  # 0.0 a 1.0
    descripcion = models.TextField()
    contexto_cultural = models.TextField()
    periodo_historico = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=200)
    significado = models.TextField()
    imagen = models.ImageField(upload_to='cultural_items/', null=True, blank=True)
    
    # Campos de auditoría
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Validación
    is_validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='validated_items'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Elemento Cultural'
        verbose_name_plural = 'Elementos Culturales'
    
    def __str__(self):
        return f"{self.titulo} ({self.get_categoria_display()})"

class CulturalAnalysisLog(models.Model):
    """Log de análisis realizados con OpenAI"""
    cultural_item = models.OneToOneField(CulturalItem, on_delete=models.CASCADE)
    openai_response = models.TextField()
    processing_time = models.FloatField()  # en segundos
    api_cost = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Análisis Cultural'
        verbose_name_plural = 'Logs de Análisis Cultural'

class ReportStatus(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    APROBADO = 'APROBADO', 'Aprobado'
    RECHAZADO = 'RECHAZADO', 'Rechazado'


class ReportType(models.TextChoices):
    CORRECCION = 'CORRECCION', 'Corrección de análisis incorrecto'
    NUEVO_ELEMENTO = 'NUEVO_ELEMENTO', 'Nuevo elemento cultural'


class CulturalReport(models.Model):
    """Reporte de usuario sobre análisis incorrecto o nuevo elemento cultural"""
    # Usuario que reporta
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    
    # Tipo de reporte
    report_type = models.CharField(
        max_length=20, 
        choices=ReportType.choices,
        default=ReportType.CORRECCION
    )
    
    # Información del reporte
    motivo = models.TextField(help_text="Razón del reporte")
    
    # Datos de la corrección/nuevo elemento
    titulo = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=CulturalCategory.choices)
    descripcion = models.TextField()
    contexto_cultural = models.TextField()
    periodo_historico = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=200)
    significado = models.TextField()
    confianza = models.FloatField(default=0.85, help_text="Nivel de confianza sugerido")
    
    # Imagen del elemento
    imagen = models.ImageField(upload_to='reports/', null=True, blank=True)
    
    # Estado del reporte
    status = models.CharField(
        max_length=20, 
        choices=ReportStatus.choices,
        default=ReportStatus.PENDIENTE
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Administrador que revisa
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_reports'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Notas del administrador")
    
    # Referencia al elemento cultural creado (si fue aprobado)
    created_cultural_item = models.ForeignKey(
        CulturalItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_report'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reporte Cultural'
        verbose_name_plural = 'Reportes Culturales'
    
    def __str__(self):
        return f"Reporte #{self.id} - {self.titulo} ({self.get_status_display()})"