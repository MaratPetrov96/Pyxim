from django.forms import *
from .models import *

class RecordForm(ModelForm):
    class Meta:
        model = Record
        fields = ['title','content']
        widgets = {'title':TextInput()
                   ,'content':Textarea(attrs={'rows':5,'cols':27})}
        labels = {'title':'','content':''}
