from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from slugify import slugify as slugify_cyrillic


class Category(models.Model):
    """
    Категория для статей.
    Примеры: 'Обзоры', 'Новости', 'Тест-драйвы'
    """
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_cyrillic(self.name, separator='-')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category_articles", kwargs={"slug": self.slug})


class Tag(models.Model):
    """
    Тег для статей.
    Примеры: 'BMW', 'Электромобили', 'Кроссоверы'
    """
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_cyrillic(self.name, separator='-')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:tag_articles", kwargs={"slug": self.slug})


class PublishedManager(models.Manager):
    """Менеджер для получения только опубликованных статей"""
    def get_queryset(self):
        return super().get_queryset().filter(status="published")


class Article(models.Model):
    """
    Статья блога.
    Содержит заголовок, текст, изображение и мета-информацию.
    """
    
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PUBLISHED = "published", "Опубликовано"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="articles/", blank=True, null=True)
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles"
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles"
    )
    
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="articles"
    )
    
    publish = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="liked_articles"
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["-publish"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_cyrillic(self.title, separator='-')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:article_detail", kwargs={"slug": self.slug})


class Comment(models.Model):
    """
    Комментарий к статье.
    Требует модерации (active = False по умолчанию).
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created"]

    def __str__(self):
        return f"Комментарий от {self.name} к {self.article.title}"