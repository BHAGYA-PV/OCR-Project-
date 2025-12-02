from django.db import models

class Document(models.Model):
    filename = models.CharField(max_length=255)
    path = models.FileField(upload_to="documents/")
    uploaded_date = models.DateTimeField(auto_now_add=True)
    mime_type = models.CharField(max_length=100)
    ocr_text = models.TextField(blank=True, null=True, db_index=True)

    def __str__(self):
        return self.filename
