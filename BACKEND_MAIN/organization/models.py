from django.db import models

# Create your models here.

class Organization(models.Model):

    name=models.CharField(max_length=200,unique=True)
    description=models.TextField(blank=True)
    logo=models.ImageField(upload_to="organization_logos/",null=True, blank=True)
    is_active =models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name