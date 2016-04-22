from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=100)
    pred_rating = models.CharField(max_length=20)
    real_rating = models.CharField(max_length=20)
    rating_words = models.CharField(max_length=200)
    cloud_words = models.CharField(max_length=400)
    def __str__(self):
        return self.title

class Movie_File(models.Model):
    address = models.CharField(max_length=200)
    def __str__(self):
        return "Movie File at " + self.address