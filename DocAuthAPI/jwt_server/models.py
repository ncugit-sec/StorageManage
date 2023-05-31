from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    department = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'user'