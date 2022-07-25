from django.shortcuts import render,redirect,HttpResponse
from django.views.generic import DetailView,UpdateView
from .forms import *
from django.core.paginator import Paginator
from transliterate import slugify
from uuid import uuid4
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,logout
from .models import *

width = 480
height = 520

def pyxim(request,template,data):
    fresh = Paginator(Record.objects.all(),3)
    fresh = fresh.page(fresh.num_pages)
    data['fresh'] = fresh
    data['categories'] = Category.objects.all()
    return render(request,template,data)

def main(request):
    return pyxim(request,'Main.html',{'title':'Главная страница'})

def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)

@login_required
def publish(request):
    if request.method == 'POST':
        text = request.POST['text']
        title = request.POST['title']
        for count,i in enumerate(request.FILES.getlist('img')):
            file = Photo(file=i,record=new,description=request.FILES.getlist('descr')[count])
            fs = FileSystemStorage() #defaults to   MEDIA_ROOT
            filename = fs.save(f'{uuid4()}.jpg', i)
            file_url = fs.url(filename)
            attrs = imgs[count].attrs
            attrs['class'] = attrs['class'][0]
            blob = sorted(attrs.items())
            blob = '<img '+' '.join([f'{k}="{v}"' for k,v in attrs.items()])+'>'
            text = text.replace('<input name="img" type="file" onchange="upload(this)" style="display: none;">'
                              ,f'<img src="{file_url}" name="upload" width="{width}" height="{height}">',1).replace(
                                  '<input type="text" name="descr">'
                                  ,f"<p style='font-size:20px'>{request.POST.getlist('descr')[count]}</p>",1
                                  ).replace(blob,'')
        new = Record(title=title,link=slugify(title),content=text,
                     category=Category.objects.get(pk=request.POST['category']),
                     author=request.user)
        new.save()
        return redirect('record',link=new.link,pk=new.pk)
    return pyxim(request,'NewRecord.html')

class RecordView(DetailView):
    model = Record
    template_name = 'Record.html'
    context_name_object = 'record'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['record'] = self.model.get(pk=self.kwargs['pk'])
        return context

    def test_func(self,**kwargs):
        return self.object.link == self.kwargs['link'] and self.object.pk == self.kwargs['pk']

class TagView(DetailView):
    model = Tag
    template_name = 'Records.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        if 'pg' not in self.kwargs.keys():
            self.kwargs['pg'] = 1
        context['tag'] = self.object
        context['records'] = Paginator(self.object.records,self.kwargs['pg'])
        return context

    def get_object(self, **kwargs):
        return self.model.get(link=self.kwargs['tag'])

class CategoryView(DetailView):
    model = Category
    template_name = 'Records.html'
    context_name_object = 'category'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        if 'pg' not in self.kwargs.keys():
            self.kwargs['pg'] = 1
        context['category'] = self.object
        context['records'] = Paginator(self.object.records,self.kwargs['pg'])
        return context

    def get_object(self, **kwargs):
        return self.model.get(link=self.kwargs['cat'])

def login(request):
    return render(request,'Login.html')
