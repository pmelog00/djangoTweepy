from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Busqueda(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    query = models.CharField(max_length=100)
    maximo = models.IntegerField()
    fecha = models.CharField(max_length=100)