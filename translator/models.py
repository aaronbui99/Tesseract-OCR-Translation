from django.db import models
import os
import uuid

def get_file_path(instance, filename):
    """Generate a unique file path for uploaded files."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

def get_output_path(instance, filename):
    """Generate a unique file path for output files."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('outputs', filename)

class Document(models.Model):
    """Model to store uploaded documents."""
    PROCESSING_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=get_file_path)
    file_type = models.CharField(max_length=10)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='pending')
    
    def __str__(self):
        return self.title or os.path.basename(self.file.name)
    
    def delete(self, *args, **kwargs):
        # Delete the file when the model instance is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

class OCRResult(models.Model):
    """Model to store OCR results."""
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='ocr_result')
    text = models.TextField()
    language = models.CharField(max_length=10, default='eng')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"OCR Result for {self.document}"

class Translation(models.Model):
    """Model to store translations."""
    ocr_result = models.ForeignKey(OCRResult, on_delete=models.CASCADE, related_name='translations')
    text = models.TextField()
    source_language = models.CharField(max_length=10)
    target_language = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Translation from {self.source_language} to {self.target_language}"

class OutputFile(models.Model):
    """Model to store output files."""
    OUTPUT_TYPES = (
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('txt', 'TXT'),
        ('jpeg', 'JPEG'),
        ('png', 'PNG'),
    )
    
    translation = models.ForeignKey(Translation, on_delete=models.CASCADE, related_name='output_files')
    file = models.FileField(upload_to=get_output_path)
    file_type = models.CharField(max_length=10, choices=OUTPUT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file_type} output for {self.translation}"
    
    def delete(self, *args, **kwargs):
        # Delete the file when the model instance is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)
