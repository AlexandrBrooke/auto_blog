from django import forms
from .models import Article, Comment


# ============================================================
# ФОРМА ДЛЯ СТАТЬИ
# Используется для создания и редактирования статей
# ============================================================
class ArticleForm(forms.ModelForm):
    """
    Форма для работы со статьями.
    Используется в: add_article.html, edit_article.html
    """
    
    class Meta:
        # Модель, с которой работает форма
        model = Article
        
        # Поля, которые будут отображаться в форме
        fields = ['title', 'slug', 'category', 'tags', 'image', 'content', 'status']
        
        # Настройка виджетов (внешний вид полей)
        widgets = {
            # Текстовое поле с подсказкой внутри
            'title': forms.TextInput(attrs={'placeholder': 'Введите заголовок статьи'}),
            
            # Текстовое поле с подсказкой про автогенерацию
            'slug': forms.TextInput(attrs={'placeholder': 'auto-generated при пустом поле'}),
            
            # Выпадающий список для выбора категории
            'category': forms.Select(),
            
            # Множественный выбор для тегов
            'tags': forms.SelectMultiple(),
            
            # Поле для загрузки изображения
            'image': forms.ClearableFileInput(),
            
            # Большое текстовое поле для содержимого (12 строк)
            'content': forms.Textarea(attrs={'rows': 12}),
            
            # Выпадающий список для статуса (черновик/опубликовано)
            'status': forms.Select(),
        }
        
        # Подсказки для пользователя (отображаются под полями)
        help_texts = {
            'title': 'Краткий и ёмкий заголовок статьи.',
            'slug': 'URL-адрес. Если пуст — будет сгенерирован автоматически.',
            'image': 'Главное изображение. Рекомендуемый размер: 1200×630 px.',
            'content': 'Текст статьи. Поддерживается Markdown.',
            'status': 'Черновик — для редактирования, Опубликовано — видно всем.',
        }

    def __init__(self, *args, **kwargs):
        """
        Конструктор формы.
        Добавляет CSS-класс 'form-input' ко всем полям.
        """
        super().__init__(*args, **kwargs)
        
        # Перебираем все поля формы
        for field in self.fields.values():
            # Добавляем класс 'form-input' к каждому полю
            # Если класс уже есть - добавляем через пробел
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-input'


# ============================================================
# ФОРМА ДЛЯ КОММЕНТАРИЯ
# Используется для добавления комментариев к статье
# ============================================================
class CommentForm(forms.ModelForm):
    """
    Форма для добавления комментариев.
    Используется в: article_detail.html
    """
    
    class Meta:
        # Модель, с которой работает форма
        model = Comment
        
        # Поля, которые будут отображаться в форме
        fields = ['name', 'email', 'body']
        
        # Настройка виджетов (внешний вид полей)
        widgets = {
            # Поле для имени с подсказкой
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
            
            # Поле для email с примером формата
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
            
            # Большое текстовое поле для комментария (4 строки)
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш комментарий'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Конструктор формы.
        Добавляет CSS-класс 'form-input' ко всем полям.
        """
        super().__init__(*args, **kwargs)
        
        # Перебираем все поля формы
        for field in self.fields.values():
            # Добавляем класс 'form-input' к каждому полю
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-input'