from django.contrib import admin
from .models import Article, Category, Tag, Comment


# ============================================================
# НАСТРОЙКА АДМИНКИ ДЛЯ КАТЕГОРИЙ
# ============================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для модели Category (категории статей)"""
    
    # Поля, которые показываются в списке категорий
    list_display = ('name', 'slug')
    
    # Автоматическое заполнение slug из названия
    prepopulated_fields = {'slug': ('name',)}
    
    # Поиск по названию категории
    search_fields = ('name',)
    
    # Сортировка по названию (по алфавиту)
    ordering = ('name',)


# ============================================================
# НАСТРОЙКА АДМИНКИ ДЛЯ ТЕГОВ
# ============================================================
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag (теги статей)"""
    
    # Поля, которые показываются в списке тегов
    list_display = ('name', 'slug')
    
    # Автоматическое заполнение slug из названия
    prepopulated_fields = {'slug': ('name',)}
    
    # Поиск по названию тега
    search_fields = ('name',)
    
    # Сортировка по названию (по алфавиту)
    ordering = ('name',)


# ============================================================
# НАСТРОЙКА АДМИНКИ ДЛЯ СТАТЕЙ
# ============================================================
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Админка для модели Article (статьи)"""
    
    # Поля, которые показываются в списке статей
    list_display = ('title', 'category', 'author', 'publish', 'status')
    
    # Фильтры для списка статей
    list_filter = ('publish', 'category', 'author', 'status')
    
    # Поиск по заголовку и содержанию статьи
    search_fields = ('title', 'content')
    
    # Автоматическое заполнение slug из заголовка
    prepopulated_fields = {'slug': ('title',)}
    
    # Поле author отображается как ID (для оптимизации)
    raw_id_fields = ('author',)
    
    # Иерархия по дате (навигация по датам в админке)
    date_hierarchy = 'publish'
    
    # Сортировка: сначала новые (по убыванию даты)
    ordering = ('-publish',)
    
    # Оптимизация запросов (подгружаем связанные данные)
    list_select_related = ('category', 'author')


# ============================================================
# НАСТРОЙКА АДМИНКИ ДЛЯ КОММЕНТАРИЕВ
# ============================================================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для модели Comment (комментарии)"""
    
    # Поля, которые показываются в списке комментариев
    list_display = ('name', 'article', 'created', 'active')
    
    # Поле active можно редактировать прямо в списке (галочка)
    list_editable = ('active',)
    
    # Фильтры для списка комментариев
    list_filter = ('active', 'created')
    
    # Поиск по имени, тексту и названию статьи
    search_fields = ('name', 'body', 'article__title')
    
    # Сортировка: сначала новые (по убыванию даты)
    ordering = ('-created',)