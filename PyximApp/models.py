from django.db import models
from django.contrib.auth.models import User
import uuid

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename_start = filename.replace('.'+ext,'')
    filename = "%s__%s.%s" % (uuid.uuid4(),filename_start, ext)
    return os.path.join('pictures', filename)

class Category(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)

class Tag(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)

class Record(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category,related_name='records')
    tags = models.ManyToManyField(Tag,related_name='records')
    author = models.ForeignKey(User,related_name='records')

class Photo(models.Model):
    file = models.ImageField(upload_to=get_file_path,verbose_name=(u'File'))
    record = models.ForeignKey(Record,related_name='photos')
    description = models.CharField(max_length=500)
