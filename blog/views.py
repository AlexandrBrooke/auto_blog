from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic.dates import ArchiveIndexView
from django.utils import timezone
from django.http import Http404
from .models import Article, Category, Tag, Comment
from .forms import CommentForm, ArticleForm


def article_list(request):
    query = request.GET.get('q')
    if query:
        articles = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    else:
        articles = Article.objects.all()

    paginator = Paginator(articles, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    latest_articles = Article.objects.all()[:5]
    tags = Tag.objects.all()

    return render(request, 'blog/article_list.html', {
        'page_obj': page_obj,
        'query': query,
        'latest_articles': latest_articles,
        'tags': tags,
    })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    comments = article.comments.filter(active=True)

    latest_articles = Article.objects.all()[:5]
    tags = Tag.objects.all()

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

    return render(request, 'blog/article_detail.html', {
        'article': article,
        'comments': comments,
        'form': form,
        'latest_articles': latest_articles,
        'tags': tags,
    })


@login_required
def add_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            messages.success(request, 'Статья успешно добавлена Ожидает публикации.')
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = ArticleForm()

    latest_articles = Article.objects.all()[:5]
    tags = Tag.objects.all()

    return render(request, 'blog/add_article.html', {
        'form': form,
        'latest_articles': latest_articles,
        'tags': tags,
    })


@login_required
def edit_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.author != request.user:
        raise Http404("У вас нет прав на редактирование этой статьи")

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья успешно обновлена!')
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    latest_articles = Article.objects.all()[:5]
    tags = Tag.objects.all()

    return render(request, 'blog/edit_article.html', {
        'form': form,
        'article': article,
        'latest_articles': latest_articles,
        'tags': tags,
    })


class ArticleArchiveView(ArchiveIndexView):
    model = Article
    date_field = 'publish'
    template_name = 'blog/archive.html'
    context_object_name = 'articles'
    paginate_by = 5
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_articles'] = Article.objects.all()[:5]
        context['tags'] = Tag.objects.all()
        return context


@login_required
def like_article(request, slug):
    if request.method == 'POST':
        article = get_object_or_404(Article, slug=slug)
        article.likes += 1
        article.save()
        return JsonResponse({'likes': article.likes})
    return JsonResponse({'error': 'Метод не поддерживается'}, status=400)