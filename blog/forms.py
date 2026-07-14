from django import forms
from .models import Article, Comment
import re
from marshmallow import Schema, fields, ValidationError, validates_schema


def validate_form_data(data):
    """
    Базовая валидация данных формы.
    Возвращает словарь с ошибками или пустой словарь.
    """
    errors = {}

    username = data.get('username', '')
    email = data.get('email', '')
    age_str = data.get('age', '')

    if not username or len(username) < 3 or len(username) > 20:
        errors['username'] = 'Имя пользователя должно быть от 3 до 20 символов.'
    elif not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors['username'] = 'Имя пользователя содержит недопустимые символы.'

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(email_pattern, email):
        errors['email'] = 'Пожалуйста, введите корректный адрес электронной почты.'

    try:
        age = int(age_str)
        if age < 0 or age > 120:
            errors['age'] = 'Возраст должен быть числом от 0 до 120.'
    except ValueError:
        errors['age'] = 'Поле возраста должно быть числовым.'

    return errors


class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=lambda x: 3 <= len(x) <= 20)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 8)
    
    @validates_schema
    def validate_username(self, data, **kwargs):
        username = data.get('username')
        if username and not username.replace('_', '').isalnum():
            raise ValidationError(
                'Имя пользователя может содержать только буквы, цифры и _.', 
                'username'
            )


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'tags', 'image', 'content', 'status']
        
        labels = {
            'title': 'Заголовок',
            'category': 'Категория',
            'tags': 'Теги',
            'image': 'Изображение',
            'content': 'Содержание',
            'status': 'Статус',
        }
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Введите заголовок статьи'}),
            'category': forms.Select(),
            'tags': forms.SelectMultiple(),
            'image': forms.ClearableFileInput(),
            'content': forms.Textarea(attrs={'rows': 12}),
            'status': forms.Select(),
        }
        
        help_texts = {
            'title': 'Краткий и ёмкий заголовок статьи.',
            'image': 'Главное изображение. Рекомендуемый размер: 1200x630 px.',
            'content': 'Текст статьи.',
            'status': 'Черновик — для редактирования, Опубликовано — видно всем.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-input'

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            if len(title) < 5:
                raise forms.ValidationError('Заголовок должен содержать минимум 5 символов.')
            if len(title) > 200:
                raise forms.ValidationError('Заголовок не может быть длиннее 200 символов.')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            if len(content) < 20:
                raise forms.ValidationError(
                    'Содержание статьи должно быть не менее 20 символов.'
                )
            url_count = len(re.findall(r'http[s]?://', content))
            if url_count > 10:
                raise forms.ValidationError(
                    'Слишком много ссылок в статье. Пожалуйста, уменьшите их количество.'
                )
        return content
    
    def clean(self):
        cleaned_data = super().clean()
        
        class ArticleSchema(Schema):
            title = fields.Str(required=True, validate=lambda x: 5 <= len(x) <= 200)
            content = fields.Str(required=True, validate=lambda x: len(x) >= 20)
        
        schema = ArticleSchema()
        try:
            validation_data = {
                'title': cleaned_data.get('title'),
                'content': cleaned_data.get('content'),
            }
            validation_data = {k: v for k, v in validation_data.items() if v is not None}
            schema.load(validation_data)
        except ValidationError as err:
            for field, messages in err.messages.items():
                for message in messages:
                    self.add_error(field, message)
        
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш комментарий'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-input'

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            if len(name) < 2:
                raise forms.ValidationError('Имя должно содержать минимум 2 символа.')
            if len(name) > 50:
                raise forms.ValidationError('Имя не может быть длиннее 50 символов.')
            if not re.match(r'^[a-zA-Zа-яА-Я\s-]+$', name):
                raise forms.ValidationError(
                    'Имя может содержать только буквы, пробелы и дефисы.'
                )
        return name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise forms.ValidationError(
                    'Пожалуйста, введите корректный адрес электронной почты.'
                )
            temp_email_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
            for domain in temp_email_domains:
                if domain in email.lower():
                    raise forms.ValidationError(
                        'Использование временных email-адресов запрещено.'
                    )
        return email
    
    def clean_body(self):
        body = self.cleaned_data.get('body')
        if body:
            if len(body) < 3:
                raise forms.ValidationError(
                    'Комментарий должен содержать минимум 3 символа.'
                )
            if len(body) > 1000:
                raise forms.ValidationError(
                    'Комментарий не может быть длиннее 1000 символов.'
                )
            
            url_count = len(re.findall(r'http[s]?://', body))
            if url_count > 2:
                raise forms.ValidationError(
                    'Слишком много ссылок в комментарии. Пожалуйста, напишите текст.'
                )
            
            bad_words = ['мат', 'ругательство', 'спам']
            for word in bad_words:
                if word.lower() in body.lower():
                    raise forms.ValidationError(
                        f'Комментарий содержит запрещенное слово: "{word}"'
                    )
        return body


class MarshmallowDemoForm(forms.Form):
    username = forms.CharField(max_length=20, label='Имя пользователя')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    
    def clean(self):
        cleaned_data = super().clean()
        
        schema = UserRegistrationSchema()
        
        try:
            validated = schema.load({
                'username': cleaned_data.get('username'),
                'email': cleaned_data.get('email'),
                'password': cleaned_data.get('password'),
            })
            cleaned_data.update(validated)
        except ValidationError as err:
            for field, messages in err.messages.items():
                for message in messages:
                    self.add_error(field, message)
        
        return cleaned_data


def demo_validation():
    """
    Демонстрация работы всех методов валидации.
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ВАЛИДАЦИИ ДАННЫХ")
    print("=" * 60)
    
    print("\n1. БАЗОВАЯ ВАЛИДАЦИЯ:")
    form_data = {
        'username': 'user_123',
        'email': 'user@example.com',
        'age': '25'
    }
    errors = validate_form_data(form_data)
    if errors:
        print(f"Ошибки: {errors}")
    else:
        print("Данные валидны")
    
    print("\n2. MARSHMALLOW ВАЛИДАЦИЯ:")
    schema = UserRegistrationSchema()
    
    valid_data = {
        'username': 'new_user',
        'email': 'new@example.com',
        'password': 'strongpassword123'
    }
    try:
        result = schema.load(valid_data)
        print("Валидные данные:", result)
    except ValidationError as err:
        print("Ошибки:", err.messages)
    
    invalid_data = {
        'username': 'a',
        'email': 'invalid-email',
        'password': '123'
    }
    try:
        result = schema.load(invalid_data)
        print("Валидные данные:", result)
    except ValidationError as err:
        print("Ошибки:", err.messages)
    
    print("\n3. DJANGO FORM ВАЛИДАЦИЯ:")
    form = ArticleForm({
        'title': 'Краткий заголовок',
        'slug': 'short-title',
        'content': 'Это содержимое статьи.',
    })
    if form.is_valid():
        print("Форма валидна")
    else:
        print("Ошибки формы:", form.errors)
    
    print("\n" + "=" * 60)