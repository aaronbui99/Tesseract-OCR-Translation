from django.urls import path
from . import views

app_name = 'translator'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('upload/', views.upload_view, name='upload'),
    path('ocr/<int:document_id>/', views.ocr_view, name='ocr'),
    path('translate/<int:ocr_id>/', views.translate_view, name='translate'),
    path('output-format/<int:translation_id>/', views.output_format_view, name='output_format'),
    path('result/<int:output_id>/', views.result_view, name='result'),
    path('document/<int:document_id>/', views.document_detail_view, name='document_detail'),
    path('document/<int:document_id>/delete/', views.delete_document_view, name='delete_document'),
]