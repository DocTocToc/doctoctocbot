from django.db import models

# Create your models here.
class Mesh(models.Model):
    uid = models.CharField(
        max_length=10,
        unique=True
    )
    fr = models.CharField(
        max_length=255,
    )
    en = models.CharField(
        max_length=255,
    )
    
    def __str__(self):
        return f"{self.uid}, {self.en}"
    
    class Meta:
        indexes = [
            models.Index(fields=['uid']),
        ]