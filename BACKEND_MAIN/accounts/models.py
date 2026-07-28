from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from organization.models import Organization




# Create your models here.
class User(AbstractUser):

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    email = models.EmailField(unique=True)

    organization=models.ForeignKey(Organization,null=True,blank=True,on_delete=models.PROTECT)

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super_Admin"
        ORG_ADMIN = "ORG_ADMIN", "Organization_Admin"
        EMPLOYEE = "EMPLOYEE", "Employee"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )
    
    def save(self,*args,**kwargs):

        if self.is_superuser:
            self.role=self.Role.SUPER_ADMIN
        super().save(*args,**kwargs)


    def __str__(self):
        return self.email