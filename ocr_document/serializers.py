from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "filename", "path", "uploaded_date", "mime_type", "ocr_text"]
        read_only_fields = ["id", "uploaded_date", "ocr_text", "path"]