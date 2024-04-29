from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=150, null=True)
    encrypted_password = models.CharField(max_length=256, default="1234")
    token = models.CharField(max_length=30, null=True, unique=True)
    name = models.CharField(max_length=75, default="Beautiful Person")
