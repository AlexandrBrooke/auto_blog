from django import forms
from .models import Article, Comment

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'slug', 'category', 'tags', 'image', 'content', 'status']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 12}),
            'slug': forms.TextInput(attrs={'placeholder': 'auto-generated при пустом поле'}),
        }
        help_texts = {
            'title': 'Краткий и ёмкий заголовок статьи.',
            'slug': 'URL-адрес. Если пуст — будет сгенерирован автоматически.',
            'image': 'Главное изображение. Рекомендуемый размер: 1200×630 px.',
            'content': 'Текст статьи. Поддерживается Markdown.',
            'status': 'Черновик — для редактирования, Опубликовано — видно всем.',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }