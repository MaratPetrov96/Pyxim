from django.db import models
import os
from django.conf import settings

class Category(models.Model):
    title = models.CharField(max_length=50)
    link = models.CharField(max_length=50)
    class Meta:
        verbose_name='Категория'
        verbose_name_plural='Категории'

class Tag(models.Model):
    title = models.CharField(max_length=50)
    link = models.CharField(max_length=50)
    class Meta:
        verbose_name='Тег'
        verbose_name_plural='Теги'

class Record(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category,related_name='records',on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag,related_name='records')
    date = models.DateField(auto_now_add=True)
    class Meta:
        verbose_name='Публикация'
        verbose_name_plural='Публикации'

class Photo(models.Model):
    file = models.ImageField(upload_to=settings.MEDIA_ROOT)
    record = models.ForeignKey(Record,related_name='photos',on_delete=models.CASCADE)
    description = models.CharField(max_length=400,blank=True)
    class Meta:
        verbose_name='Фото'
        verbose_name_plural='Фото'

class Comment(models.Model):
    username = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
