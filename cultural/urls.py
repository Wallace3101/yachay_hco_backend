# cultural/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Endpoints de elementos culturales
    path('items/create', views.create_cultural_item, name='create_cultural_item'),
    path('items', views.get_cultural_items, name='get_cultural_items'),
    path('items/<int:id>', views.get_cultural_item_detail, name='get_cultural_item_detail'),
    path('analyze/', views.analyze_cultural_content, name='analyze_cultural_content'),
    path('items/me', views.get_my_cultural_items, name='get_my_cultural_items'),
    
    # Endpoints de reportes
    path('reports/create', views.create_report, name='create_report'),
    path('reports/my-reports', views.get_user_reports, name='get_user_reports'),
    path('reports/all', views.get_all_reports, name='get_all_reports'),  # Admin only
    path('reports/<int:report_id>', views.get_report_detail, name='get_report_detail'),
    path('reports/<int:report_id>/review', views.review_report, name='review_report'),  # Admin only
]