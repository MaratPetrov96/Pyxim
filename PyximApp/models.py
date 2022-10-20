from django.db import models
import os
from django.conf import settings
from django.contrib.auth.models import User

class Category(models.Model):
    title = models.CharField(max_length=50)
    link = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name='Категория'
        verbose_name_plural='Категории'

class Tag(models.Model):
    title = models.CharField(max_length=50)
    link = models.CharField(max_length=50)

    def __str__(self):
        return self.title
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
    hot = models.BooleanField(default=False)
    author = models.ForeignKey(User,related_name='records',on_delete=models.CASCADE)
    class Meta:
        verbose_name='Публикация'
        verbose_name_plural='Публикации'
    def __str__(self):
        return self.title

class Photo(models.Model):
    file = models.ImageField(upload_to=settings.MEDIA_ROOT)
    record = models.ForeignKey(Record,related_name='photos',on_delete=models.CASCADE)
    description = models.CharField(max_length=400,blank=True)
    class Meta:
        verbose_name='Фото'
        verbose_name_plural='Фото'
    def __str__(self):
        return f'К записи {self.record.pk}'

class Comment(models.Model):
    username = models.CharField(max_length=100,default='Гость')
    content = models.TextField()
    user = models.ForeignKey(User,related_name='comms',null=True,
                             blank=True,on_delete=models.CASCADE)
    record = models.ForeignKey(Record,related_name='comms',on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE
                                ,null=True,blank=True,related_name='replies')
    main_parent = models.ForeignKey('self',on_delete=models.CASCADE
                                ,null=True,blank=True,related_name='all_replies')
    def __str__(self):
        return f'{self.content} (К записи {self.record.pk})'

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    saved = models.ManyToManyField(Record,related_name='saved',blank=True)
