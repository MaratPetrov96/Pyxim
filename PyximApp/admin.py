from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Record)
admin.site.register(Photo)

try:
    admin.site.register(Tag)
except:
    pass

class Post(admin.TabularInline):
    model = Record.tags.through
    extra = 3

try:
    #@admin.register(Record)
    class OfferAdmin(admin.ModelAdmin):
        inlines = (Post,)
        exclude = ('tags',)
except:
    pass
