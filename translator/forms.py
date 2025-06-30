from django import forms
from .models import Document, OCRResult, Translation

class DocumentUploadForm(forms.ModelForm):
    """Form for uploading documents."""
    class Meta:
        model = Document
        fields = ['file', 'title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            file_type = file.name.split('.')[-1].lower()
            if file_type not in ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif']:
                raise forms.ValidationError("Unsupported file type. Please upload PDF, PNG, JPEG, TIFF, BMP, or GIF files.")
            
            # Store the file type for later use
            self.instance.file_type = file_type
        return file

class OCRLanguageForm(forms.ModelForm):
    """Form for selecting OCR language."""
    class Meta:
        model = OCRResult
        fields = ['language']
        widgets = {
            'language': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # List of common languages supported by Tesseract
        language_choices = [
            ('eng', 'English'),
            ('fra', 'French'),
            ('deu', 'German'),
            ('spa', 'Spanish'),
            ('ita', 'Italian'),
            ('por', 'Portuguese'),
            ('rus', 'Russian'),
            ('jpn', 'Japanese'),
            ('chi_sim', 'Chinese Simplified'),
            ('chi_tra', 'Chinese Traditional'),
            ('kor', 'Korean'),
            ('ara', 'Arabic'),
            ('hin', 'Hindi'),
            ('vie', 'Vietnamese'),
            ('nld', 'Dutch'),
            ('swe', 'Swedish'),
            ('fin', 'Finnish'),
            ('pol', 'Polish'),
            ('tur', 'Turkish'),
            ('ell', 'Greek'),
            ('heb', 'Hebrew'),
        ]
        self.fields['language'].choices = language_choices

class TranslationForm(forms.ModelForm):
    """Form for selecting translation languages."""
    class Meta:
        model = Translation
        fields = ['target_language']
        widgets = {
            'target_language': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # List of languages supported by DeepL
        language_choices = [
            ('EN-US', 'English (American)'),
            ('EN-GB', 'English (British)'),
            ('FR', 'French'),
            ('DE', 'German'),
            ('ES', 'Spanish'),
            ('IT', 'Italian'),
            ('PT-PT', 'Portuguese'),
            ('PT-BR', 'Portuguese (Brazilian)'),
            ('RU', 'Russian'),
            ('JA', 'Japanese'),
            ('ZH', 'Chinese (simplified)'),
            ('NL', 'Dutch'),
            ('PL', 'Polish'),
            ('BG', 'Bulgarian'),
            ('CS', 'Czech'),
            ('DA', 'Danish'),
            ('ET', 'Estonian'),
            ('FI', 'Finnish'),
            ('EL', 'Greek'),
            ('HU', 'Hungarian'),
            ('LV', 'Latvian'),
            ('LT', 'Lithuanian'),
            ('RO', 'Romanian'),
            ('SK', 'Slovak'),
            ('SL', 'Slovenian'),
            ('SV', 'Swedish'),
        ]
        self.fields['target_language'].choices = language_choices

class OutputFormatForm(forms.Form):
    """Form for selecting output format and editing translated text."""
    OUTPUT_FORMATS = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document (DOCX)'),
        ('txt', 'Text File (TXT)'),
        ('jpeg', 'JPEG Image'),
        ('png', 'PNG Image'),
    ]
    
    translated_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'style': 'font-family: monospace;'
        }),
        required=True
    )
    
    output_format = forms.ChoiceField(
        choices=OUTPUT_FORMATS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )