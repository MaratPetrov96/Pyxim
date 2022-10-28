from django.shortcuts import render,redirect,HttpResponse,Http404
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.views.generic import DetailView,UpdateView
from django.core import serializers
from django.core.paginator import Paginator
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from tempfile import NamedTemporaryFile
from rest_framework import serializers

from .models import *
from .forms import *

from transliterate import slugify
from uuid import uuid4
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

import os
import json


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

def template(request,template,data): #шаблонизация
    data['fresh'] = fresh() #свежие записи в шапке сайта
    data['categories'] = Category.objects.all()
    data['user'] = request.user
    data['sign_form'] = UserCreationForm
    data['login_form'] = AuthenticationForm
    return render(request,template,data)

def load_more(request): #загрузка превью записей на главной странице
    loaded_item = int(request.GET.get('loaded_item'))
    limit = 3
    all_ = Record.objects.all().order_by('-pk')
    params = [(i.photos.first().file.url,i.category.title) for i in list(all_)[loaded_item:loaded_item+limit]]
    post_obj = list(all_.values()[loaded_item:loaded_item+limit])
    index = True
    try:
        all_[loaded_item+limit]
    except IndexError:
        index = False
    for n,p in enumerate(post_obj):
        post_obj[n]['photo'] = params[n][0]
        post_obj[n]['category'] = params[n][1]
    data = {'posts': post_obj,'index':index}
    return JsonResponse(data=data)

def load_tag(request,tag): #загрузка превью записей при просмотре тега
    loaded_item = int(request.GET.get('loaded_item'))
    limit = 3
    all_ = Tag.objects.get(title=tag).records.all().order_by('-pk')
    params = [(i.photos.first().file.url,i.category.title) for i in list(all_)[loaded_item:loaded_item+limit]]
    post_obj = list(all_.values()[loaded_item:loaded_item+limit])
    try:
        all_[loaded_item+limit]
    except IndexError:
        index = False
    else:
        index = True #для создания или удаления кнопки "Загузить ещё"
    for n,p in enumerate(post_obj):
        post_obj[n]['photo'] = params[n][0]
        post_obj[n]['category'] = params[n][1]
    data = {'posts': post_obj,'index':index}
    return JsonResponse(data=data)

def load_category(request,cat): #загрузка превью записей при просмотре категории
    loaded_item = int(request.GET.get('loaded_item'))
    limit = 3
    all_ = Category.objects.get(pk=cat).records.all().order_by('-pk')
    params = [(i.photos.first().file.url,i.category.title) for i in list(all_)[loaded_item:loaded_item+limit]]
    post_obj = list(all_.values()[loaded_item:loaded_item+limit])
    try:
        all_[loaded_item+limit]
    except IndexError:
        index = False
    else:
        index = True
    for n,p in enumerate(post_obj):
        post_obj[n]['photo'] = params[n][0]
        post_obj[n]['category'] = params[n][1]
    data = {'posts': post_obj,'index':index}
    return JsonResponse(data=data)

@login_required
def load_saved(request):
    loaded_item = int(request.GET.get('loaded_item'))
    limit = 3
    all_ = request.user.profile.saved.all().order_by('-pk')
    params = [(i.photos.first().file.url,i.category.title) for i in list(all_)[loaded_item:loaded_item+limit]]
    post_obj = list(all_.values()[loaded_item:loaded_item+limit])
    index = True
    try:
        all_[loaded_item+limit]
    except IndexError:
        index = False
    for n,p in enumerate(post_obj):
        post_obj[n]['photo'] = params[n][0]
        post_obj[n]['category'] = params[n][1]
    data = {'posts': post_obj,'index':index}
    return JsonResponse(data=data)

def main(request): #главная страница
    data = Paginator(Record.objects.all().order_by('-pk'),3)
    more = False
    if data.num_pages != 1:
        more = True
    data = data.page(1)
    return template(request,'Records.html',{'title':'Главная страница','records':data,
                                         'url_':reverse('load'),'more':more})

def handler404(request,exception):
    return render(request,'404.html')

@login_required
def add(request): #добавление записи
    if request.user.is_superuser:
        if request.method == 'POST':
            content = request.POST['text']
            title = request.POST['title']
            tags = request.POST['tags_id']
            imgs = bs(request.POST['text'],'html.parser').findAll(class_='picture') #картинки
            text = []
            images = request.FILES.getlist('img')
            html = bs(content,'html.parser')
            count = 0
            for i in html.findAll('div'):
                if 'class' in i.attrs:
                    if i.attrs['class'] == ['editor']: #текст
                        text.append('\r\n'.join(list(i.stripped_strings)[:-1]))
                        for img in i.findAll('img'): #вставленные изображения, не могут быть прокомментированы
                            text.append('<img src>')
                    elif i.attrs['class'] == ['editor','img']: #загруженные изображения, могут быть прокомментированы
                        text.append('<img src>')
            new = Record(title=title,link=slugify(title),content='\r\n\r\n'.join(text),
                         category=Category.objects.get(pk=request.POST['category']),
                         author=request.user)
            new.save()
            for img in html.findAll('img'):
                if img.findParent().get('class') == ['editor']:
                    name = uuid4() #генерация имени
                    filename = f'Pyxim/temp/{name}.jpg'
                    with open(filename,'wb') as wb: #создание временного файла при сохранении изображения
                        wb.write(urlopen(img.get('src')).read())
                    file = Photo(record=new)
                    with open(filename,'rb') as read: #сохранение вставленного изображения
                        file.file.save(f'{name}.jpg',File(read))
                        file.save()
                    os.remove(filename) #удаление врЕменного файла
                else:
                    #сохранение изображения, загруженного с устройства
                    file = Photo(file=images[count],record=new,description=request.POST.getlist('descr')[count])
                    file.save()
                    count += 1
            if tags.split('-')[1:-1]:
                for i in tags.split('-')[1:-1]:
                    new.tags.add(Tag.objects.get(pk=int(i)))
            return redirect('record',link=new.link,pk=new.pk)
        return template(request,'NewRecord.html',{'tags':Tag.objects.all(),'title':'Новая запись'})
    raise Http404

class RecordView(DetailView):
    model = Record
    template_name = 'Record.html'
    context_name_object = 'record'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['categories'] = Category.objects.all()
        context['fresh'] = fresh(self.object)
        context['comms'] = self.object.comms.filter(models.Q(main_parent=None))
        text = self.object.content
        for n,i in enumerate(self.object.photos.all()): #заменяем <img src> на изображения
            text = text.replace('<img src>',f'<div><img src={i.file.url} width={width} height={height} name="{i.pk}"><p>{i.description}</p></div>',1)
        context['content'] = text
        context['sign_form'] = UserCreationForm
        context['login_form'] = AuthenticationForm
        return context

    def get_object(self, **kwargs):
        try:
            return self.model.objects.get(link=self.kwargs['link'],pk=self.kwargs['pk'])
        except Record.DoesNotExist:
            raise Http404

class RecordsPage(DetailView): #для генерации списков записей
    template_name = 'Records.html'
    def context_data(self,context,url):
        data = Paginator(self.object.records.all().order_by('-pk'),4)
        more = False #есть ли записи для дополнительной загрузки
        if data.num_pages != 1:
            more = True
        context['more'] = more
        context['records'] = data.page(1)
        context['categories'] = Category.objects.all()
        context['title'] = self.object.title
        context['fresh'] = fresh()
        context['user'] = self.request.user
        context['url_'] = reverse(url, args=(self.object.pk,))
        context['sign_form'] = UserCreationForm
        context['login_form'] = AuthenticationForm
        return context

class TagView(RecordsPage):
    model = Tag
    context_name_object = 'tag'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return self.context_data(context,'load_tag')

    def get_object(self, **kwargs):
        return self.model.objects.get(link=self.kwargs['tag'])

class CategoryView(RecordsPage):
    model = Category
    context_name_object = 'category'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return self.context_data(context,'load_cat')

    def get_object(self, **kwargs):
        return self.model.objects.get(link=self.kwargs['cat'])

def sign(request): #авторизация/authorization
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        User.objects.create_user(username=username, password=password, email=email)
        user = authenticate(username=username, password=password)
        profile = Profile(user=user)
        profile.save()
        login(request,user)
    return redirect('main')

def Login(request): #аутентификация/authentication
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(username=username, password=password)
        if user:
            login(request,user)
            return redirect('main')
    return redirect('main')

def Logout(request): #выход из аккаунта
    logout(request)
    return redirect('main')

def comment(request,pk): #комментарий
    if request.POST['text']:
        #для теста
        #com = Comment.objects.get(pk=10)
        com = Comment(content=request.POST['text'],record=Record.objects.get(pk=pk))
        if request.user.is_authenticated:
            com.user = request.user
            com.username = request.user.username
        else:
            com.username = 'Гость'
            if request.POST['username']:
                com.username = request.POST['username']
        com.save()
        user_json = serializers.serialize("json", [com])
        return HttpResponse(user_json, content_type='application/json')

def reply(request,pk): #ответ
    if request.POST['text']:
        #для теста
        #com = Comment.objects.get(pk=13)
        parent = Comment.objects.get(pk=pk)
        if parent.main_parent: #проверка, является ли комментарий ответом
            com = Comment(content=request.POST['text'],record=parent.record,parent=parent,main_parent=parent.main_parent)
        else:
            com = Comment(content=request.POST['text'],record=parent.record,main_parent=parent)
        if request.user.is_authenticated:
            com.user = request.user
            com.username = request.user.username
        else:
            com.username = 'Гость'
            if request.POST['username']:
                com.username = request.POST['username']
        com.save()
        data = [com]
        if parent.parent:
            data.append(parent)
        user_json = serializers.serialize("json", data)
        return HttpResponse(user_json, content_type='application/json')

@login_required
def save(request,record): #сохранение записи в профиль
    request.user.profile.saved.add(
        Record.objects.get(pk=record))
    response = [{"pk":record}]
    data = json.dumps(response)
    return HttpResponse(data, content_type='application/json')

@login_required
def delete(request,record): #удаление записи из профиля
    request.user.profile.saved.remove(
        Record.objects.get(pk=record))
    response = [{"pk":record}]
    data = json.dumps(response)
    return HttpResponse(data, content_type='application/json')

@login_required
def view_saved(request): #просмотр сохранённого
    data = Paginator(request.user.profile.saved.all().order_by('-pk'),4)
    more = False #есть ли записи для дополнительной загрузки
    if data.num_pages != 1:
        more = True
    context = dict()
    context['more'] = more
    context['records'] = data.page(1)
    context['title'] = 'Сохранённое'
    context['url_'] = reverse('load_saved')
    return template(request,'Records.html',context)

def search(request):
    return redirect('search_res',query=request.POST['query'])

def search_res(request,query):
    data = Paginator(Record.objects.filter(title__contains=query).order_by('-pk'),4)
    more = False #есть ли записи для дополнительной загрузки
    if data.num_pages != 1:
        more = True
    context = dict()
    context['more'] = more
    context['records'] = data.page(1)
    context['title'] = f'Поиск по запросу "{query}"'
    context['url_'] = reverse('load_search',kwargs={'query':query})
    return template(request,'Records.html',context)

def load_search(request,query):
    loaded_item = int(request.GET.get('loaded_item'))
    limit = 3
    all_ = Record.objects.filter(title_text__search=query).order_by('-pk')
    params = [(i.photos.first().file.url,i.category.title) for i in list(all_)[loaded_item:loaded_item+limit]]
    post_obj = list(all_.values()[loaded_item:loaded_item+limit])
    try:
        all_[loaded_item+limit]
    except IndexError:
        index = False
    else:
        index = True
    for n,p in enumerate(post_obj):
        post_obj[n]['photo'] = params[n][0]
        post_obj[n]['category'] = params[n][1]
    data = {'posts': post_obj,'index':index}
    return JsonResponse(data=data)
