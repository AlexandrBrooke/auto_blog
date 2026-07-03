from django.test import TestCase
from django.contrib.auth.models import User
from .models import Article, Category, Tag, Comment
from .forms import ArticleForm, CommentForm, validate_form_data, UserRegistrationSchema
from marshmallow import ValidationError as MarshmallowValidationError
from slugify import slugify as slugify_cyrillic


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')

    def test_article_creation(self):
        article = Article.objects.create(
            title='Тест',
            content='Контент',
            author=self.user,
            status='published'
        )
        self.assertEqual(Article.objects.count(), 1)
        self.assertTrue(article.slug)  # slug должен сгенерироваться автоматически

    def test_category_creation(self):
        cat = Category.objects.create(name='Новости')
        self.assertEqual(cat.slug, 'novosti')  # транслитерация


class ValidationTests(TestCase):
    def test_basic_validation_valid(self):
        data = {'username': 'user_123', 'email': 'user@example.com', 'age': '25'}
        errors = validate_form_data(data)
        self.assertEqual(errors, {})

    def test_basic_validation_invalid(self):
        data = {'username': 'a', 'email': 'invalid', 'age': 'abc'}
        errors = validate_form_data(data)
        self.assertIn('username', errors)
        self.assertIn('email', errors)
        self.assertIn('age', errors)

    def test_marshmallow_valid(self):
        schema = UserRegistrationSchema()
        data = {'username': 'new_user', 'email': 'new@example.com', 'password': 'strong123'}
        result = schema.load(data)
        self.assertEqual(result['username'], 'new_user')

    def test_marshmallow_invalid(self):
        schema = UserRegistrationSchema()
        data = {'username': 'a', 'email': 'invalid', 'password': '123'}
        with self.assertRaises(MarshmallowValidationError):
            schema.load(data)

    def test_article_form(self):
        form = ArticleForm(data={
            'title': 'Заголовок',
            'content': 'Достаточно длинное содержание статьи для валидации.',
            'status': 'published'
        })
        self.assertTrue(form.is_valid())

    def test_comment_form(self):
        form = CommentForm(data={
            'name': 'Иван Петров',
            'email': 'ivan@example.com',
            'body': 'Отличный комментарий!'
        })
        self.assertTrue(form.is_valid())