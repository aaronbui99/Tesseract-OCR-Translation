import os
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import Document, OCRResult, Translation, OutputFile
from .forms import DocumentUploadForm, OCRLanguageForm, TranslationForm, OutputFormatForm
from .utils import perform_ocr, translate_text, generate_output_file

def home_view(request):
    """Home page view."""
    recent_documents = Document.objects.order_by('-uploaded_at')[:5]
    context = {
        'recent_documents': recent_documents,
        'view_name': 'home'
    }
    return render(request, 'translator/app.html', context)

def upload_view(request):
    """View for uploading documents."""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('translator:ocr', document_id=document.id)
    else:
        form = DocumentUploadForm()
    
    context = {
        'form': form,
        'view_name': 'upload'
    }
    return render(request, 'translator/app.html', context)

def ocr_view(request, document_id):
    """View for OCR processing."""
    document = get_object_or_404(Document, id=document_id)
    
    # Check if OCR has already been performed
    if hasattr(document, 'ocr_result'):
        messages.info(request, 'OCR has already been performed on this document.')
        return redirect('translator:translate', ocr_id=document.ocr_result.id)
    
    if request.method == 'POST':
        form = OCRLanguageForm(request.POST)
        if form.is_valid():
            try:
                # Update document status
                document.status = 'processing'
                document.save()
                
                # Perform OCR
                ocr_text = perform_ocr(document.file.path, form.cleaned_data['language'])
                
                # Create OCR result
                ocr_result = OCRResult.objects.create(
                    document=document,
                    text=ocr_text,
                    language=form.cleaned_data['language']
                )
                
                # Update document status
                document.status = 'completed'
                document.save()
                
                messages.success(request, 'OCR processing completed successfully!')
                return redirect('translator:translate', ocr_id=ocr_result.id)
            
            except Exception as e:
                document.status = 'failed'
                document.save()
                messages.error(request, f'OCR processing failed: {str(e)}')
    else:
        form = OCRLanguageForm()
    
    context = {
        'document': document,
        'form': form,
        'view_name': 'ocr'
    }
    return render(request, 'translator/app.html', context)

def translate_view(request, ocr_id):
    """View for translating OCR results."""
    ocr_result = get_object_or_404(OCRResult, id=ocr_id)
    
    if request.method == 'POST':
        form = TranslationForm(request.POST)
        if form.is_valid():
            try:
                # Get source language from OCR result
                source_lang = ocr_result.language
                target_lang = form.cleaned_data['target_language']
                
                # Map Tesseract language codes to DeepL language codes
                tesseract_to_deepl = {
                    'eng': 'EN',
                    'fra': 'FR',
                    'deu': 'DE',
                    'spa': 'ES',
                    'ita': 'IT',
                    'por': 'PT',
                    'rus': 'RU',
                    'jpn': 'JA',
                    'chi_sim': 'ZH',
                    'nld': 'NL',
                    'pol': 'PL',
                }
                
                # Get DeepL source language code
                deepl_source_lang = tesseract_to_deepl.get(source_lang)
                
                # Translate text
                translated_text = translate_text(
                    ocr_result.text,
                    source_lang=deepl_source_lang,
                    target_lang=target_lang
                )
                
                # Create translation
                translation = Translation.objects.create(
                    ocr_result=ocr_result,
                    text=translated_text,
                    source_language=source_lang,
                    target_language=target_lang
                )
                
                messages.success(request, 'Text translated successfully!')
                return redirect('translator:output_format', translation_id=translation.id)
            
            except Exception as e:
                messages.error(request, f'Translation failed: {str(e)}')
    else:
        form = TranslationForm()
    
    context = {
        'ocr_result': ocr_result,
        'form': form,
        'view_name': 'translate'
    }
    return render(request, 'translator/app.html', context)

def output_format_view(request, translation_id):
    """View for selecting output format and editing translated text."""
    translation = get_object_or_404(Translation, id=translation_id)
    
    if request.method == 'POST':
        form = OutputFormatForm(request.POST)
        if form.is_valid():
            try:
                output_format = form.cleaned_data['output_format']
                edited_text = form.cleaned_data['translated_text']
                
                # Create output directory if it doesn't exist
                output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
                os.makedirs(output_dir, exist_ok=True)
                
                # Generate output filename
                filename = f"{uuid.uuid4()}.{output_format}"
                output_path = os.path.join(output_dir, filename)
                
                # Generate output file with the edited text
                generate_output_file(edited_text, output_format, output_path)
                
                # Create output file record
                relative_path = os.path.join('outputs', filename)
                output_file = OutputFile.objects.create(
                    translation=translation,
                    file=relative_path,
                    file_type=output_format
                )
                
                # Update the translation with the edited text if it's different
                if edited_text != translation.text:
                    translation.text = edited_text
                    translation.save()
                    messages.info(request, 'Translation text has been updated with your edits.')
                
                messages.success(request, f'{output_format.upper()} file generated successfully!')
                return redirect('translator:result', output_id=output_file.id)
            
            except Exception as e:
                messages.error(request, f'Output file generation failed: {str(e)}')
    else:
        # Pre-populate the form with the translation text
        form = OutputFormatForm(initial={'translated_text': translation.text})
    
    context = {
        'translation': translation,
        'form': form,
        'view_name': 'output_format'
    }
    return render(request, 'translator/app.html', context)

def result_view(request, output_id):
    """View for displaying results."""
    output_file = get_object_or_404(OutputFile, id=output_id)
    context = {
        'output_file': output_file,
        'view_name': 'result'
    }
    return render(request, 'translator/app.html', context)

def document_detail_view(request, document_id):
    """View for document details."""
    document = get_object_or_404(Document, id=document_id)
    context = {
        'document': document,
        'view_name': 'document_detail'
    }
    return render(request, 'translator/app.html', context)

def delete_document_view(request, document_id):
    """View for deleting documents."""
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('translator:home')
    
    return redirect('translator:document_detail', document_id=document.id)
