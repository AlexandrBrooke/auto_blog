from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.generic import ListView

from .models import Article, Category, Tag
from .forms import CommentForm, ArticleForm


# ============================================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ
# Общие данные для сайдбара (используется во всех представлениях)
# ============================================================
def _common_sidebar_data():
    """
    Возвращает данные, общие для всех страниц:
    - последние статьи (5 шт.)
    - все теги
    - все категории
    Используется в сайдбаре.
    """
    return {
        'latest_articles': Article.published.all()[:5],  # 5 последних статей
        'tags': Tag.objects.all(),                        # Все теги
        'categories': Category.objects.all(),             # Все категории
    }


# ============================================================
# ГЛАВНАЯ СТРАНИЦА (СПИСОК СТАТЕЙ)
# ============================================================
def article_list(request):
    """
    Главная страница со списком статей.
    Поддерживает поиск по заголовку, содержимому и тегам.
    URL: /
    Шаблон: blog/article_list.html
    """
    
    # Получаем поисковый запрос из GET-параметров
    query = request.GET.get('q', '').strip()
    
    # Базовый запрос: только опубликованные статьи
    articles = Article.published.all()

    # Если есть поисковый запрос - фильтруем
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |          # Поиск в заголовке
            Q(content__icontains=query) |        # Поиск в содержимом
            Q(tags__name__icontains=query)       # Поиск по тегам
        ).distinct()  # Убираем дубли (если статья имеет несколько тегов)

    # Контекст для шаблона
    context = {
        'articles': articles,
        'query': query,
        'active_category': None,  # Для подсветки активной категории
        'active_tag': None,       # Для подсветки активного тега
    }
    context.update(_common_sidebar_data())  # Добавляем общие данные
    return render(request, 'blog/article_list.html', context)


# ============================================================
# СТАТЬИ ПО КАТЕГОРИИ
# ============================================================
def category_articles(request, slug):
    """
    Страница со статьями определённой категории.
    URL: /category/<slug>/
    """
    
    # Находим категорию или возвращаем 404
    category = get_object_or_404(Category, slug=slug)
    
    # Берём только опубликованные статьи этой категории
    articles = Article.published.filter(category=category)

    context = {
        'articles': articles,
        'query': None,
        'active_category': category.slug,  # Подсвечиваем категорию
        'active_tag': None,
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/article_list.html', context)


# ============================================================
# СТАТЬИ ПО ТЕГУ
# ============================================================
def tag_articles(request, slug):
    """
    Страница со статьями с определённым тегом.
    URL: /tag/<slug>/
    """
    
    # Находим тег или возвращаем 404
    tag = get_object_or_404(Tag, slug=slug)
    
    # Берём только опубликованные статьи с этим тегом
    articles = Article.published.filter(tags=tag).distinct()

    context = {
        'articles': articles,
        'query': None,
        'active_category': None,
        'active_tag': tag.slug,  # Подсвечиваем тег
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/article_list.html', context)


# ============================================================
# ДЕТАЛЬНАЯ СТРАНИЦА СТАТЬИ
# ============================================================
def article_detail(request, slug):
    """
    Полная страница статьи с комментариями.
    URL: /article/<slug>/
    Шаблон: blog/article_detail.html
    """
    
    # Находим статью со всеми связанными данными (оптимизация)
    article = get_object_or_404(
        Article.objects.select_related('author', 'category').prefetch_related('tags', 'likes'),
        slug=slug
    )
    
    # Берём только активные комментарии (прошедшие модерацию)
    comments = article.comments.filter(active=True)

    # Увеличиваем счётчик просмотров
    article.views += 1
    article.save(update_fields=['views'])

    # Обработка формы комментария
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # Сохраняем комментарий, но не отправляем в БД
            comment = form.save(commit=False)
            comment.article = article  # Привязываем к статье
            comment.active = False     # Отправляем на модерацию
            comment.save()
            
            # Сообщение об успехе
            messages.success(request, 'Комментарий добавлен и ожидает модерации.')
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = CommentForm()

    context = {
        'article': article,
        'comments': comments,
        'form': form,
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/article_detail.html', context)


# ============================================================
# ДОБАВЛЕНИЕ СТАТЬИ (ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ)
# ============================================================
@login_required
def add_article(request):
    """
    Страница добавления новой статьи.
    Требуется авторизация.
    URL: /article/add/
    Шаблон: blog/add_article.html
    """
    
    if request.method == 'POST':
        # Создаём форму с переданными данными и файлами
        form = ArticleForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Сохраняем статью, но пока без автора
            article = form.save(commit=False)
            article.author = request.user  # Устанавливаем текущего пользователя как автора
            article.save()
            form.save_m2m()  # Сохраняем связи "многие ко многим" (теги)
            
            messages.success(request, 'Статья успешно добавлена. Она ожидает публикации.')
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = ArticleForm()

    context = {'form': form}
    context.update(_common_sidebar_data())
    return render(request, 'blog/add_article.html', context)


# ============================================================
# РЕДАКТИРОВАНИЕ СТАТЬИ (ТОЛЬКО ДЛЯ АВТОРОВ)
# ============================================================
@login_required
def edit_article(request, slug):
    """
    Страница редактирования статьи.
    Только автор может редактировать свою статью.
    URL: /article/<slug>/edit/
    Шаблон: blog/edit_article.html
    """
    
    # Находим статью
    article = get_object_or_404(Article, slug=slug)

    # Проверка прав: только автор может редактировать
    if article.author != request.user:
        raise Http404("У вас нет прав на редактирование этой статьи")

    if request.method == 'POST':
        # Обновляем существующую статью
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()  # Сохраняем изменения
            messages.success(request, 'Статья успешно обновлена!')
            return redirect('blog:article_detail', slug=article.slug)
    else:
        # GET-запрос: показываем форму с текущими данными
        form = ArticleForm(instance=article)

    context = {
        'form': form,
        'article': article,
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/edit_article.html', context)


# ============================================================
# АРХИВ СТАТЕЙ (СПИСОК С ФИЛЬТРАЦИЕЙ)
# ============================================================
class ArticleArchiveView(ListView):
    """
    Архив статей с фильтрацией и пагинацией.
    URL: /archive/
    Шаблон: blog/archive.html
    """
    
    model = Article
    template_name = 'blog/archive.html'
    context_object_name = 'articles'
    paginate_by = 5  # 5 статей на страницу

    def get_queryset(self):
        """
        Формирует список статей с учётом фильтров.
        Фильтры: поиск, год, тег, категория.
        """
        
        # Базовый запрос: только опубликованные статьи
        qs = Article.published.all().select_related('category').prefetch_related('tags')
        
        # Получаем параметры фильтрации из GET
        q = self.request.GET.get('q', '').strip()
        year = self.request.GET.get('year', '').strip()
        tag = self.request.GET.get('tag', '').strip()
        category = self.request.GET.get('category', '').strip()

        # Применяем фильтры
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(tags__name__icontains=q) |
                Q(category__name__icontains=q)
            ).distinct()

        if year:
            qs = qs.filter(publish__year=year)  # Фильтр по году

        if tag:
            qs = qs.filter(tags__slug=tag).distinct()  # Фильтр по тегу

        if category:
            qs = qs.filter(category__slug=category)  # Фильтр по категории

        return qs.order_by('-publish')  # Сортировка: сначала новые

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст.
        """
        context = super().get_context_data(**kwargs)
        
        # Общие данные для сайдбара
        context.update(_common_sidebar_data())
        
        # Список всех годов публикаций (для фильтрации)
        context['years'] = Article.published.dates('publish', 'year', order='DESC')
        
        # Активные фильтры (для подсветки)
        context['active_category'] = self.request.GET.get('category')
        context['active_tag'] = self.request.GET.get('tag')
        context['query'] = self.request.GET.get('q', '')
        
        return context


# ============================================================
# ЛАЙК СТАТЬИ (AJAX)
# ============================================================
@login_required
def like_article(request, slug):
    """
    Обработка лайков через AJAX.
    URL: /article/<slug>/like/
    Возвращает JSON с количеством лайков.
    """
    
    # Только POST-запросы
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=400)

    # Находим статью
    article = get_object_or_404(Article, slug=slug)

    # Переключаем лайк: добавляем или удаляем
    if request.user in article.likes.all():
        article.likes.remove(request.user)  # Убираем лайк
        liked = False
    else:
        article.likes.add(request.user)     # Ставим лайк
        liked = True

    # Возвращаем результат в формате JSON
    return JsonResponse({
        'likes': article.likes.count(),  # Общее количество лайков
        'liked': liked,                  # Лайкнул ли текущий пользователь
    })