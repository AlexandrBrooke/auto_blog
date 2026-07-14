from django.contrib import admin
from .models import Article, Category, Tag, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'publish', 'status')
    list_filter = ('publish', 'category', 'author', 'status')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('-publish',)
    list_select_related = ('category', 'author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'created', 'active')
    list_editable = ('active',)
    list_filter = ('active', 'created')
    search_fields = ('name', 'body', 'article__title')
    ordering = ('-created',)