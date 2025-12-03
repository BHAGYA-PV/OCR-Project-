INTRODUCTION:
#-----------

    This project accepts file uploads (images and PDFs), stores files, extracts text using a hybrid approach (fast text-based extraction for "text PDFs" + OCR for scanned images/PDFs using Tesseract), stores OCR results in the database, and supports searching by filename and by OCR text.
    Upload images and PDFs via REST endpoint

#------------------------------------------------------------------------------------------

FEATURES:
#--------

    Automatic MIME detection

    Fast extraction for text-based PDFs (PyPDF2)

    OCR for scanned PDFs and images (pytesseract + pdf2image)

    Background OCR processing using Python threading

    Search by filename and by OCR text (case-insensitive contains search)

#------------------------------------------------------------------------------------------

USED:
    Python 3.11.2

USED DB:
    Sqlite3

API TESTING:
    By Postman
        Upload several small images and PDFs and confirm the ocr_text column populates after a short delay.

#------------------------------------------------------------------------------------------

QUICK SETUP - PROJECT RUNNING:
#----------------------------

    1) create and activate virtual environment
        Command: python venv env

    2) Activate virtual environment
        Command: env\Scripts\activate

        PYTHON PACKAGES INSTALLED IN ENV FILE:
        #------------------------------------

        Django :
            Command: pip install django

        djangorestframework :
            pip install djangorestframework
            (Have build in Validations, Serialization, Better error handling, Consistent API patterns...)
            
        pytesseract :
            Command: pip install pytesseract
            (Python wrapper around Tesseract for OCR.
            Converts images/PDF pages into text using mechine trained character recognition )

        python-magic :
            Command: pip install python-magic
            (or python-magic-bin on Windows - detect MIME type reliably from file bytes.)

        Pillow :
            Command: pip install Pillow
            (image handling.)

        pdf2image :
            Command: pip install pdf2image
            (convert PDF pages to images so we can OCR scanned PDFs.)
            
        PyPDF2 :
            Command: pip install PyPDF2
            (fast text extraction for PDFs that already contain selectable text (faster than OCR).)

    3) Create a Django Project:
        Command : django-admin startproject 'projectname'

    4) Move into project directory
        Command: cd 'projectname'
    
    5) Create a Django App
        Command: python manage.py startapp ocr_documents

    6) Register the App in settings.py

    7) migrate DB
        python manage.py migrations
        python manage.py migrate

    8) run server
        python manage.py runserver

#------------------------------------------------------------------------------------------

SYSTEM DEPENDENCIES:
#-------------------

    Tesseract OCR: 
        required by pytesseract. Install from https://github.com/tesseract-ocr/tesseract 

    Poppler (for pdf2image): 
        required to convert PDF pages to images. On Windows use the builds from https://github.com/oschwartz10612/poppler-windows/releases


#------------------------------------------------------------------------------------------

In Settings.py :
#--------------

    Add app name In installed apps

    # media
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

    # tesseract & poppler 
    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    POPPLER_PATH = r'C:\poppler-23.03.0\Library\bin'

    # DRF
    REST_FRAMEWORK = {
        'DEFAULT_PARSER_CLASSES': [
            'rest_framework.parsers.MultiPartParser',
            'rest_framework.parsers.FormParser',
        ]
    }

#------------------------------------------------------------------------------------------

IMPLEMENTATION (models, serializers, views):
#------------------------------------------------

    Model:
        Document model contains: filename, path (FileField), uploaded_date, mime_type, ocr_text.
        ocr_text can be nullable/blank; updated by background worker.

    Serializers:
        DocumentSerializer is a ModelSerializer exposing id, filename, path, uploaded_date, mime_type, ocr_text.
        read_only_fields includes id, uploaded_date, ocr_text.

    Views:
        UploadDocument accepts multipart file uploads, detects MIME type using python-magic, creates Document record, saves file, then create a background Thread for run_ocr(doc).

    run_ocr function:
        Uses PyPDF2 to try extracting text quickly (fast path) for text PDFs — this is CPU cheap and returns immediately when successful.

        If no text or extraction fails, falls back to converting PDF pages to images using pdf2image and then running pytesseract on each page.

        For images, opens with Pillow and runs pytesseract.image_to_string.

        Saves extracted text to doc.ocr_text and calls doc.save() when finished.

        The provided implementation uses threading.Thread(..., daemon=True) so the web request does not wait on OCR and the worker thread does not prevent exit if server stops.

#------------------------------------------------------------------------------------------

PERFORMANCE (HOW SPEED WAS ACHIEVED):
#------------------------------------

    Fast PDF extraction first:
        The system tries to read text directly from PDFs before running OCR. Many PDFs already contain text, so this step is very fast and avoids heavy OCR.

    OCR runs in the background:
        When a file is uploaded, OCR happens in another thread. The API responds immediately without waiting for the extraction to finish.

    Only do OCR when needed:
        If the PDF already has text, the system skips OCR entirely. This saves time and processing power.

    Faster PDF-to-image conversion:
        When OCR is needed for scanned PDFs, images are generated at a lower DPI. This speeds up processing.

    Optimized Tesseract settings:
        Tesseract is run with simple config options that make it faster and more accurate for standard documents.
