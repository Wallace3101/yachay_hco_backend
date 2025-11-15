# cultural/admin.py
from django.contrib import admin
from .models import CulturalItem, CulturalAnalysisLog, CulturalReport

@admin.register(CulturalItem)
class CulturalItemAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'confianza', 'is_validated', 'created_at']
    list_filter = ['categoria', 'is_validated', 'created_at']
    search_fields = ['titulo', 'descripcion', 'ubicacion']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['validate_items']
    
    def validate_items(self, request, queryset):
        updated = queryset.update(
            is_validated=True,
            validated_by=request.user
        )
        self.message_user(request, f'{updated} elementos validados correctamente.')
    
    validate_items.short_description = "Validar elementos seleccionados"

@admin.register(CulturalAnalysisLog)
class CulturalAnalysisLogAdmin(admin.ModelAdmin):
    list_display = ['cultural_item', 'processing_time', 'api_cost', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(CulturalReport)
class CulturalReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'report_type', 'status', 'reported_by', 'created_at']
    list_filter = ['status', 'report_type', 'categoria', 'created_at']
    search_fields = ['titulo', 'motivo', 'descripcion']
    readonly_fields = ['created_at', 'updated_at', 'reported_by']
    
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('report_type', 'motivo', 'reported_by', 'status')
        }),
        ('Datos del Elemento Cultural', {
            'fields': (
                'titulo', 'categoria', 'descripcion', 'contexto_cultural',
                'periodo_historico', 'ubicacion', 'significado', 'confianza', 'imagen'
            )
        }),
        ('Revisión del Administrador', {
            'fields': ('reviewed_by', 'reviewed_at', 'admin_notes', 'created_cultural_item')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_reports', 'reject_reports']
    
    def approve_reports(self, request, queryset):
        """Acción personalizada para aprobar reportes desde el admin"""
        from django.utils import timezone
        from .views import add_to_elementos_json
        
        approved = 0
        for report in queryset.filter(status='PENDIENTE'):
            # Crear elemento cultural
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
            
            # Actualizar reporte
            report.status = 'APROBADO'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.created_cultural_item = cultural_item
            report.save()
            
            # Agregar a JSON
            add_to_elementos_json(cultural_item)
            approved += 1
        
        self.message_user(request, f'{approved} reportes aprobados y agregados al dataset.')
    
    approve_reports.short_description = "Aprobar reportes seleccionados"
    
    def reject_reports(self, request, queryset):
        """Acción personalizada para rechazar reportes desde el admin"""
        from django.utils import timezone
        
        rejected = queryset.filter(status='PENDIENTE').update(
            status='RECHAZADO',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        
        self.message_user(request, f'{rejected} reportes rechazados.')
    
    reject_reports.short_description = "Rechazar reportes seleccionados"