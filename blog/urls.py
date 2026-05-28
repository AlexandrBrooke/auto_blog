from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('article/create/', views.add_article, name='add_article'),
    path('article/<slug:slug>/edit/', views.edit_article, name='edit_article'),
    path('archive/', views.ArticleArchiveView.as_view(), name='archive'),
    path('like/<slug:slug>/', views.like_article, name='like_article'),
    path('category/<slug:slug>/', views.article_list, name='category'),
    path('tag/<slug:slug>/', views.article_list, name='tag'),
]