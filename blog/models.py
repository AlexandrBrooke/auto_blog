from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings


# ============================================================
# МОДЕЛЬ: Категория
# Для группировки статей по темам
# ============================================================
class Category(models.Model):
    """
    Категория для статей.
    Примеры: 'Обзоры', 'Новости', 'Тест-драйвы'
    """
    
    # Название категории (уникальное)
    name = models.CharField(max_length=120, unique=True)
    
    # URL-идентификатор (генерируется из названия)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    
    # Описание категории (необязательное)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]  # Сортировка по алфавиту

    def __str__(self):
        """Название категории в админке"""
        return self.name

    def save(self, *args, **kwargs):
        """При сохранении создаём slug, если он пустой"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ссылка на страницу со статьями этой категории"""
        return reverse("blog:category_articles", kwargs={"slug": self.slug})


# ============================================================
# МОДЕЛЬ: Тег
# Для ключевых слов статей (поиск, фильтрация)
# ============================================================
class Tag(models.Model):
    """
    Тег для статей.
    Примеры: 'BMW', 'Электромобили', 'Кроссоверы'
    """
    
    # Название тега (уникальное)
    name = models.CharField(max_length=80, unique=True)
    
    # URL-идентификатор (генерируется из названия)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]  # Сортировка по алфавиту

    def __str__(self):
        """Название тега в админке"""
        return self.name

    def save(self, *args, **kwargs):
        """При сохранении создаём slug, если он пустой"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ссылка на страницу со статьями с этим тегом"""
        return reverse("blog:tag_articles", kwargs={"slug": self.slug})


# ============================================================
# МЕНЕДЖЕР: Для фильтрации опубликованных статей
# ============================================================
class PublishedManager(models.Manager):
    """Менеджер для получения только опубликованных статей"""
    
    def get_queryset(self):
        """Возвращает только статьи со статусом 'published'"""
        return super().get_queryset().filter(status="published")


# ============================================================
# МОДЕЛЬ: Статья
# Основная модель блога
# ============================================================
class Article(models.Model):
    """
    Статья блога.
    Содержит заголовок, текст, изображение и мета-информацию.
    """
    
    # ===== СТАТУСЫ СТАТЬИ =====
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"       # Не видна посетителям
        PUBLISHED = "published", "Опубликовано"  # Видна всем

    # ===== ПОЛЯ СТАТЬИ =====
    
    # Заголовок статьи
    title = models.CharField(max_length=255)
    
    # URL-идентификатор (генерируется из заголовка)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Текст статьи
    content = models.TextField()
    
    # Главное изображение (загружается в папку articles/)
    image = models.ImageField(upload_to="articles/", blank=True, null=True)
    
    # Автор (связь с моделью пользователя)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # При удалении пользователя - удаляем статьи
        related_name="articles"    # user.articles - все статьи пользователя
    )
    
    # Категория (связь с Category)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # При удалении категории - оставляем статью
        null=True,
        blank=True,
        related_name="articles"    # category.articles - все статьи категории
    )
    
    # Теги (связь с Tag, многие ко многим)
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="articles"    # tag.articles - все статьи с этим тегом
    )
    
    # Дата публикации (автоматически при создании)
    publish = models.DateTimeField(auto_now_add=True)
    
    # Дата обновления (автоматически при изменении)
    updated = models.DateTimeField(auto_now=True)
    
    # Количество просмотров
    views = models.PositiveIntegerField(default=0)
    
    # Лайки (многие пользователи могут лайкать многие статьи)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="liked_articles"  # user.liked_articles - статьи, которые лайкнул пользователь
    )
    
    # Статус (черновик или опубликовано)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT  # По умолчанию - черновик
    )

    # ===== МЕНЕДЖЕРЫ =====
    objects = models.Manager()          # Стандартный менеджер
    published = PublishedManager()      # Только опубликованные статьи

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["-publish"]  # Сначала новые

    def __str__(self):
        """Заголовок статьи в админке"""
        return self.title

    def save(self, *args, **kwargs):
        """При сохранении создаём slug, если он пустой"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ссылка на страницу статьи"""
        return reverse("blog:article_detail", kwargs={"slug": self.slug})


# ============================================================
# МОДЕЛЬ: Комментарий
# Комментарии к статьям
# ============================================================
class Comment(models.Model):
    """
    Комментарий к статье.
    Требует модерации (active = False по умолчанию).
    """
    
    # Статья, к которой оставлен комментарий
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,  # При удалении статьи - удаляем комментарии
        related_name="comments"    # article.comments - все комментарии статьи
    )
    
    # Имя автора комментария
    name = models.CharField(max_length=100)
    
    # Email автора (необязательный)
    email = models.EmailField(blank=True)
    
    # Текст комментария
    body = models.TextField()
    
    # Дата создания (автоматически)
    created = models.DateTimeField(auto_now_add=True)
    
    # Активен ли комментарий (модерация)
    active = models.BooleanField(default=False)  # По умолчанию - на модерации

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created"]  # Сначала новые

    def __str__(self):
        """Информация о комментарии в админке"""
        return f"Комментарий от {self.name} к {self.article.title}"