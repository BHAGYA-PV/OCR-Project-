import pytesseract
import magic
from PIL import Image
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from threading import Thread

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from .models import Document
from .serializers import DocumentSerializer


# ---------------------------------------------
# Helper function to run OCR in a background thread
# ---------------------------------------------
def run_ocr(doc):
    try:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        mime_type = doc.mime_type
        file_path = doc.path.path

        # IMAGE
        if "image" in mime_type:
            try:
                img = Image.open(file_path)
                doc.ocr_text = pytesseract.image_to_string(img, config='--oem 1 --psm 6')
            except:
                doc.ocr_text = ""
        # PDF
        elif "pdf" in mime_type:
            # Try text extraction
            text = ""
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted
                if text.strip():
                    doc.ocr_text = text
                    doc.save()
                    return
            except:
                pass
            # Fallback to OCR on PDF images
            try:
                pages = convert_from_path(file_path, poppler_path=settings.POPPLER_PATH, dpi=150)
                text = ""
                for p in pages:
                    text += pytesseract.image_to_string(p)
                doc.ocr_text = text
            except:
                doc.ocr_text = ""
        doc.save()
    except Exception as e:
        doc.ocr_text = f"OCR failed: {str(e)}"
        doc.save()

# ---------------------------------------------
# Upload Document
# ---------------------------------------------
class UploadDocument(APIView):

    def post(self, request):
        try:
            uploaded = request.FILES.get("file")
            if not uploaded:
                return Response({"error": "No file uploaded"}, status=400)

            # Detect MIME type
            mime_type = magic.from_buffer(uploaded.read(2048), mime=True)
            uploaded.seek(0)

            # Save file
            doc = Document.objects.create(
                filename=uploaded.name,
                mime_type=mime_type
            )
            doc.path.save(uploaded.name, uploaded, save=True)

            # Start OCR in a background thread
            Thread(target=run_ocr, args=(doc,), daemon=True).start()

            return Response(
                {
                    "message": "Document uploaded successfully.",
                    "data": DocumentSerializer(doc).data
                },
                status=201
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)

# ---------------------------------------------
# List Documents
# ---------------------------------------------
class ListDocuments(APIView):

    def get(self, request):
        try:
            documents = Document.objects.all().order_by("-uploaded_date")
            serializer = DocumentSerializer(documents, many=True)
            if not serializer.data:
                return Response(
                    {"message": "No documents found"},
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    "message": "Documents fetched successfully",
                    "count": len(serializer.data),
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)

# ---------------------------------------------
# Search by Name
# ---------------------------------------------
class SearchByName(APIView):

    def get(self, request):
        try:
            query = request.GET.get("filename", "").strip()
            if not query:
                return Response({"error": "Query parameter 'filename' is required"}, status=400)

            results = Document.objects.filter(filename__icontains=query)
            serializer = DocumentSerializer(results, many=True)
            if not serializer.data:
                return Response(
                    {"message": "No documents found"},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"message": "Search results",
                "count": len(serializer.data),
                "data": serializer.data},
                status=200
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)

# ---------------------------------------------
# Search by OCR text
# ---------------------------------------------
class SearchByOCR(APIView):

    def get(self, request):
        try:
            query = request.GET.get("file_content", "").strip()
            if not query:
                return Response({"error": "Query parameter 'file_content' is required"}, status=400)

            results = Document.objects.filter(ocr_text__icontains=query)
            serializer = DocumentSerializer(results, many=True)
            if not serializer.data:
                return Response(
                    {"message": "No documents found"},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"message": "OCR search results",
                "count": len(serializer.data),
                "data": serializer.data},
                status=200
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        