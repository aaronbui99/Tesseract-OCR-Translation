python -m venv venv

venv\Scripts\activate.bat

pip install django
pip install pytesseract
pip install dotenv
pip install deepl
pip install pdf2image
pip install python-docx
pip install reportlab
pip install fpdf2

Then go to this link to download tesseract ocr: https://github.com/UB-Mannheim/tesseract/wiki

In file views.py, Change the path to where you install tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

python manage.py makemigrations

python manage.py migrate

python manage.py runserver
