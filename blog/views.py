from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.generic import ListView
from django.views.decorators.http import require_POST

from .models import Article, Category, Tag
from .forms import CommentForm, ArticleForm, validate_form_data
from marshmallow import ValidationError


def _common_sidebar_data():
    """
    Возвращает данные для сайдбара:
    - последние 5 статей
    - все теги
    - все категории
    """
    return {
        'latest_articles': Article.published.all()[:5],
        'tags': Tag.objects.all(),
        'categories': Category.objects.all(),
    }


def article_list(request):
    """
    Главная страница со списком статей.
    Поддерживает поиск по заголовку, содержимому и тегам.
    """
    query = request.GET.get('q', '').strip()
    articles = Article.published.all()

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    context = {
        'articles': articles,
        'query': query,
        'active_category': None,
        'active_tag': None,
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/article_list.html', context)


def category_articles(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.published.filter(category=category)

    context = {
        'articles': articles,
        'query': None,
        'active_category': category.slug,
        'active_tag': None,
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/article_list.html', context)


def tag_articles(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    articles = Article.published.filter(tags=tag).distinct()

    context = {
        'articles': articles,
        'query': None,
        'active_category': None,
        'active_tag': tag.slug,
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/article_list.html', context)


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related('author', 'category').prefetch_related('tags', 'likes'),
        slug=slug
    )
    
    comments = article.comments.filter(active=True)

    article.views += 1
    article.save(update_fields=['views'])

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.active = False
            comment.save()
            
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


@login_required
def add_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            
            messages.success(request, 'Статья успешно добавлена.')
            return redirect('blog:article_detail', slug=article.slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ArticleForm()

    context = {'form': form}
    context.update(_common_sidebar_data())
    return render(request, 'blog/add_article.html', context)


@login_required
def edit_article(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if article.author != request.user:
        raise Http404("У вас нет прав на редактирование этой статьи")

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, 'Статья успешно обновлена!')
            return redirect('blog:article_detail', slug=article.slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ArticleForm(instance=article)

    context = {
        'form': form,
        'article': article,
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/edit_article.html', context)


class ArticleArchiveView(ListView):
    model = Article
    template_name = 'blog/archive.html'
    context_object_name = 'articles'
    paginate_by = 5

    def get_queryset(self):
        qs = Article.published.all().select_related('category').prefetch_related('tags')
        
        q = self.request.GET.get('q', '').strip()
        year = self.request.GET.get('year', '').strip()
        tag = self.request.GET.get('tag', '').strip()
        category = self.request.GET.get('category', '').strip()

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(tags__name__icontains=q) |
                Q(category__name__icontains=q)
            ).distinct()

        if year:
            qs = qs.filter(publish__year=year)

        if tag:
            qs = qs.filter(tags__slug=tag).distinct()

        if category:
            qs = qs.filter(category__slug=category)

        return qs.order_by('-publish')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_common_sidebar_data())
        context['years'] = Article.published.dates('publish', 'year', order='DESC')
        context['active_category'] = self.request.GET.get('category')
        context['active_tag'] = self.request.GET.get('tag')
        context['query'] = self.request.GET.get('q', '')
        return context


@login_required
@require_POST
def like_article(request, slug):
    """
    Обработка лайков через AJAX.
    """
    article = get_object_or_404(Article, slug=slug)

    if request.user in article.likes.all():
        article.likes.remove(request.user)
        liked = False
    else:
        article.likes.add(request.user)
        liked = True

    return JsonResponse({
        'likes': article.likes.count(),
        'liked': liked,
    })


def demo_validation(request):
    errors = {}
    form_data = {}
    
    if request.method == 'POST':
        form_data = {
            'username': request.POST.get('username', ''),
            'email': request.POST.get('email', ''),
            'age': request.POST.get('age', ''),
        }
        
        errors = validate_form_data(form_data)
        
        if errors:
            messages.error(request, 'Найдены ошибки в данных.')
        else:
            messages.success(request, 'Все данные валидны!')
    
    context = {
        'errors': errors,
        'form_data': form_data,
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/demo_validation.html', context)


def demo_marshmallow(request):
    from .forms import UserRegistrationSchema, MarshmallowDemoForm
    
    result = None
    errors = None
    
    if request.method == 'POST':
        form = MarshmallowDemoForm(request.POST)
        if form.is_valid():
            result = form.cleaned_data
            messages.success(request, 'Данные успешно прошли валидацию!')
        else:
            errors = form.errors
            messages.error(request, 'Найдены ошибки в данных.')
    else:
        form = MarshmallowDemoForm()
    
    context = {
        'form': form,
        'result': result,
        'errors': errors,
    }
    context.update(_common_sidebar_data())
    return render(request, 'blog/demo_marshmallow.html', context)