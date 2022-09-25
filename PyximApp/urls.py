from django.urls import path
from . import views

urlpatterns = [
    path('',views.main),
    path('<str:link>-id<int:pk>',views.RecordView.as_view(),name='record'),
    path('add',views.add,name='add'),
    path('categories/<str:cat>',views.CategoryView.as_view(),name='category'),
    path('categories/<str:cat>/?pg=<int:pg>',views.CategoryView.as_view(),name='category'),
    path('tags/<str:tag>',views.TagView.as_view(),name='tag'),
    path('tags/<str:tag>/?pg=<int:pg>',views.TagView.as_view(),name='tag'),
    path('<int:pk>/comment',views.comment,name='comment'),
    path('#',views.load_more,name='load')
    ]
