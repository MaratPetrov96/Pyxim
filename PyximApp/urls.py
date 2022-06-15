from django.urls import path
from . import views

urlpatterns = [
    path('',views.main),
    path('<str:link>-id<int:pk>',views.RecordView.as_view(),name='record'),
    path('publish',views.publish),
    path('<str:cat>',views.CategoryView.as_view(),name='category'),
    path('<str:cat>/?pg=<int:pg>',views.CategoryView.as_view(),name='category'),
    path('<str:tag>',views.CategoryView.as_view(),name='tag'),
    path('<str:tag>/?pg=<int:pg>',views.CategoryView.as_view(),name='tag')
    ]

handler404 = "mysite.views.page_not_found_view"
