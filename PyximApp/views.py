from django.shortcuts import render,redirect
from django.core.paginator
from django.views.generic import DetailView,UpdateView
from .forms import *
from django.core.paginator import Paginator
from transliterate import slugify

def pyxim(request,template,data):
    fresh = Paginator(Record.objects.all(),3)
    fresh = fresh.page(fresh.num_pages)
    data['fresh'] = fresh
    return render(request,template,data)

def main(request):
    return pyxim(request,'Main.html')

def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)

@login_required
def publish(request):
    if request.method == 'POST':
        new = RecordForm(request.POST)
        new.save()
        new.link = slugify(request.POST['title'])
        new.save()
        return redirect('record',link=new.link,pk=new.pk)
    return render(request,'NewRecord.html')

class RecordView(DetailView):
    model = Record
    template_name = 'Record.html'
    context_name_object = 'record'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['record'] = self.model.get(link=self.kwargs['tag'])
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
