from django.contrib import admin
from .models import Document, OCRResult, Translation, OutputFile

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'uploaded_at', 'status')
    list_filter = ('status', 'file_type', 'uploaded_at')
    search_fields = ('title', 'file')
    readonly_fields = ('uploaded_at',)

@admin.register(OCRResult)
class OCRResultAdmin(admin.ModelAdmin):
    list_display = ('document', 'language', 'created_at')
    list_filter = ('language', 'created_at')
    search_fields = ('document__title', 'text')
    readonly_fields = ('created_at',)

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('ocr_result', 'source_language', 'target_language', 'created_at')
    list_filter = ('source_language', 'target_language', 'created_at')
    search_fields = ('ocr_result__document__title', 'text')
    readonly_fields = ('created_at',)

@admin.register(OutputFile)
class OutputFileAdmin(admin.ModelAdmin):
    list_display = ('translation', 'file_type', 'created_at')
    list_filter = ('file_type', 'created_at')
    readonly_fields = ('created_at',)
