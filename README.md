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

python manage.py makemigrations
python manage.py migrate
python manage.py runserver