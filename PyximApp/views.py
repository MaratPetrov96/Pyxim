from django.shortcuts import render,redirect,HttpResponse,Http404
from django.views.generic import DetailView,UpdateView
from .forms import *
from django.core.paginator import Paginator
from transliterate import slugify
from uuid import uuid4
from bs4 import BeautifulSoup as bs
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,logout
from django.core.files.storage import FileSystemStorage
from .models import *
from django.http import JsonResponse

width = 560 #ширина картинок в записях
height = 500 #высота картинок в записях

def fresh(record=None): #показ свежего в шапке сайта
    fresh = list(Record.objects.filter(hot=True).all())
    if len(fresh) < 5:
        return fresh
    fresh = fresh[-5:]
    if record in fresh:
        index = fresh.index(record)
        fresh[index] = fresh[0]
    return fresh[-4:]

def pyxim(request,template,data): #шаблонизация
    data['fresh'] = fresh()
    data['categories'] = Category.objects.all()
    data['user'] = request.user
    return render(request,template,data)

def load_more(request):
    loaded_item = int(request.GET.get('loaded_item'))
    limit = 2
    all_ = Record.objects.all().order_by('-date')
    params = [(i.photos.first().file.url,i.category.title) for i in list(all_)[loaded_item:loaded_item+limit]]
    post_obj = list(all_.values()[loaded_item:loaded_item+limit])
    for n,p in enumerate(post_obj):
        post_obj[n]['photo'] = params[n][0]
        post_obj[n]['category'] = params[n][1]
    #post_obj = list(Record.objects.all().order_by('-date'))[loaded_item:loaded_item+limit]
    data = {'posts': post_obj}
    #data['images'] = [post.photos.first.file.url for post in data['posts']]
    return JsonResponse(data=data)

def main(request): #главная страница
    data = Paginator(Record.objects.all().order_by('-date'),3)
    data = data.page(1)
    return pyxim(request,'Records.html',{'title':'Главная страница','records':data})

def handler404(request,exception):
    return render(request,'404.html')

@login_required
def add(request): #добавление записи
    if request.method == 'POST':
        text = request.POST['text']
        title = request.POST['title']
        tags = request.POST['tags_id']
        imgs = bs(request.POST['text'],'html.parser').findAll(class_='picture') #картинки
        new = Record(title=title,link=slugify(title),content=text,
                     category=Category.objects.get(pk=request.POST['category']),
                     author=request.user)
        new.save()
        for count,i in enumerate(request.FILES.getlist('img')):
            file = Photo(file=i,record=new,description=request.POST.getlist('descr')[count])
            file.save()
            attrs = imgs[count].attrs
            attrs['class'] = attrs['class'][0]
            blob = sorted(attrs.items()) #сортируем атрибуты, так как в html онм могут быть в любом порядке
            blob = '<img '+' '.join([f'{k}="{v}"' for k,v in attrs.items()])+'>'
            text = text.replace('<input name="img" type="file" onchange="upload(this)" style="display: none;">'
                              ,f'<img src>',1).replace(
                                  '<input type="text" name="descr">'
                                  ,'',1#вставляем код для изображений
                                  ).replace(blob,'')
        new.content = text
        new.save()
        if tags.split('-')[1:-1]:
            for i in tags.split('-')[1:-1]:
                new.tags.add(Tag.objects.get(pk=int(i)))
        return redirect('record',link=new.link,pk=new.pk)
    return pyxim(request,'NewRecord.html',{'tags':Tag.objects.all()})

class RecordView(DetailView):
    model = Record
    template_name = 'Record.html'
    context_name_object = 'record'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['categories'] = Category.objects.all()
        context['fresh'] = fresh(self.object)
        text = self.object.content
        for n,i in enumerate(self.object.photos.all()): #заменяем <img src> на изображения
            text = text.replace('<img src>',f'<div><img src={i.file.url} width={width} height={height}><p>{i.description}</p></div>',1)
        context['content'] = text
        return context

    def get_object(self, **kwargs):
        try:
            return self.model.objects.get(link=self.kwargs['link'],pk=self.kwargs['pk'])
        except Record.DoesNotExist:
            raise Http404

class TagView(DetailView):
    model = Tag
    template_name = 'Records.html'
    context_name_object = 'tag'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        if 'pg' not in self.kwargs.keys():
            self.kwargs['pg'] = 1
        context['records'] = Paginator(self.object.records.all().order_by('-date'),5).page(self.kwargs['pg'])
        context['categories'] = Category.objects.all()
        context['title'] = self.object.title
        context['fresh'] = fresh()
        return context

    def get_object(self, **kwargs):
        return self.model.objects.get(link=self.kwargs['tag'])

class CategoryView(DetailView):
    model = Category
    template_name = 'Records.html'
    context_name_object = 'category'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        if 'pg' not in self.kwargs.keys():
            self.kwargs['pg'] = 1
        context['records'] = Paginator(self.object.records.all().order_by('-date'),5).page(self.kwargs['pg'])
        context['categories'] = Category.objects.all()
        context['title'] = self.object.title
        context['fresh'] = fresh()
        return context

    def get_object(self, **kwargs):
        return self.model.objects.get(link=self.kwargs['cat'])

def login(request):
    return render(request,'Login.html')

def comment(request):
    com = Comment(content=request.POST['text'])
    if request.user.is_authenticated:
        com.user = request.user
    else:
        com.username = request.POST['username']
    com.save()
