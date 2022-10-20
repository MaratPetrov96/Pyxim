from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Record)
admin.site.register(Photo)

class Post(admin.TabularInline):
    model = Record.tags.through
    extra = 3

try:
    class OfferAdmin(admin.ModelAdmin):
        inlines = (Post,)
        exclude = ('tags',)
except:
    pass
