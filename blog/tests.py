from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import Article, Category, Tag, Comment


# ============================================================
# ПРОСТЫЕ ТЕСТЫ ДЛЯ ОСНОВНЫХ МОДЕЛЕЙ
# ============================================================

class SimpleTests(TestCase):
    """
    Класс с базовыми тестами для проверки создания статей и категорий.
    """
    
    def setUp(self):
        """
        setUp() - выполняется ПЕРЕД каждым тестом.
        Создаём тестового пользователя, чтобы использовать его во всех тестах.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_1_create_article_with_explicit_slug(self):
        """
        ТЕСТ 1: Проверяем создание статьи с явным указанием slug.
        
        Что проверяем:
        - Статья сохраняется в базе данных (счетчик = 1)
        - Заголовок сохраняется правильно
        - Slug сохраняется как мы указали
        - Метод __str__ возвращает заголовок
        """
        article = Article.objects.create(
            title='Моя статья',
            content='Контент',
            author=self.user,
            status='published',
            slug='moya-statya'  # Явно указываем slug
        )
        
        # Проверки (assert - "утверждаю, что...")
        self.assertEqual(Article.objects.count(), 1)          # В БД 1 статья
        self.assertEqual(article.title, 'Моя статья')         # Заголовок правильный
        self.assertEqual(article.slug, 'moya-statya')         # Slug правильный
        self.assertEqual(str(article), 'Моя статья')          # __str__ = заголовок
    
    def test_2_create_category(self):
        """
        ТЕСТ 2: Проверяем создание категории.
        
        Что проверяем:
        - Категория сохраняется в базе данных
        - Название сохраняется правильно
        - Метод __str__ возвращает название категории
        """
        category = Category.objects.create(
            name='Новости'
        )
        
        self.assertEqual(Category.objects.count(), 1)        # В БД 1 категория
        self.assertEqual(category.name, 'Новости')           # Название правильное
        self.assertEqual(str(category), 'Новости')           # __str__ = название


# ============================================================
# ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ ТЕГОВ И КОММЕНТАРИЕВ
# ============================================================

class MoreSimpleTests(TestCase):
    """
    Класс с тестами для проверки создания тегов и комментариев.
    """
    
    def setUp(self):
        """
        setUp() - создаём пользователя для всех тестов в этом классе.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_tag(self):
        """
        ТЕСТ 3: Проверяем создание тега.
        
        Что проверяем:
        - Тег сохраняется в базе данных
        - Название тега правильное
        - Метод __str__ возвращает название тега
        """
        tag = Tag.objects.create(
            name='Электромобили'
        )
        
        self.assertEqual(Tag.objects.count(), 1)              # В БД 1 тег
        self.assertEqual(tag.name, 'Электромобили')          # Название правильное
        self.assertEqual(str(tag), 'Электромобили')          # __str__ = название
    
    def test_create_comment(self):
        """
        ТЕСТ 4: Проверяем создание комментария.
        
        Что проверяем:
        - Сначала создаём статью, к которой будет комментарий
        - Комментарий сохраняется в базе данных
        - Имя и текст комментария правильные
        - Комментарий по умолчанию НЕ активен (требует модерации)
        """
        # Создаём статью, к которой привяжем комментарий
        article = Article.objects.create(
            title='Статья для комментария',
            content='Контент',
            author=self.user,
            status='published',
            slug='statya-dlya-kommentariya'
        )
        
        # Создаём комментарий к статье
        comment = Comment.objects.create(
            article=article,                      # Привязываем к статье
            name='Иван',                          # Имя автора
            email='ivan@example.com',             # Email
            body='Отличная статья!'               # Текст комментария
        )
        
        # Проверки
        self.assertEqual(Comment.objects.count(), 1)        # В БД 1 комментарий
        self.assertEqual(comment.name, 'Иван')              # Имя правильное
        self.assertEqual(comment.body, 'Отличная статья!')  # Текст правильный
        self.assertFalse(comment.active)                   # Неактивен (на модерации)


# ============================================================
# ТЕСТЫ ДЛЯ ФОРМ
# ============================================================

class FormTests(TestCase):
    """
    Класс для проверки работы форм.
    """
    
    def test_article_form_valid(self):
        """
        ТЕСТ 5: Проверяем, что форма создания статьи работает правильно.
        
        Что проверяем:
        - Передаём в форму валидные данные
        - Форма проходит валидацию (is_valid() = True)
        """
        from .forms import ArticleForm  # Импортируем форму
        
        # Подготавливаем данные для формы (как будто пользователь их ввел)
        form_data = {
            'title': 'Новая статья',     # Заголовок
            'content': 'Контент',        # Содержание
            'status': 'published'        # Статус "опубликовано"
        }
        
        # Создаём экземпляр формы с нашими данными
        form = ArticleForm(data=form_data)
        
        # Проверяем, что форма валидна (нет ошибок)
        self.assertTrue(form.is_valid())  # True = форма правильная