from django.db import models

# Create your models here.
class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    editora = models.CharField(max_length=150)
    genero =  models.CharField(max_length=100)
    quantidade = models.IntegerField()

    def __str__(self):
        return self.titulo