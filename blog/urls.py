from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('archive/', views.ArticleArchiveView.as_view(), name='archive'),
    path('article/add/', views.add_article, name='add_article'),
    path('article/<slug:slug>/edit/', views.edit_article, name='edit_article'),
    path('article/<slug:slug>/like/', views.like_article, name='like_article'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('category/<slug:slug>/', views.category_articles, name='category_articles'),
    path('tag/<slug:slug>/', views.tag_articles, name='tag_articles'),
]