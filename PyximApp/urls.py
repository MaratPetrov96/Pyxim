from django.urls import path
from . import views

urlpatterns = [
    path('',views.main,name='main'),
    path('<str:link>-id<int:pk>',views.RecordView.as_view(),name='record'),
    path('add',views.add,name='add'),
    path('categories/<str:cat>',views.CategoryView.as_view(),name='category'),
    path('categories/<str:cat>/?pg=<int:pg>',views.CategoryView.as_view(),name='category'),
    path('tags/<str:tag>',views.TagView.as_view(),name='tag'),
    path('tags/<str:tag>/?pg=<int:pg>',views.TagView.as_view(),name='tag'),
    path('<int:pk>/comment',views.comment,name='comment'),
    path('#',views.load_more,name='load'),
    path('login',views.Login,name='login'),
    path('sign',views.sign,name='sign'),
    path('logout',views.Logout,name='logout')
    ]
