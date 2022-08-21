from django import forms

from posts.models import Comment, Post, Group


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        widgets = {'text': forms.Textarea}

    def clean_text(self):
        data = self.cleaned_data['text']
        if 'youtube' in data.lower():
            raise forms.ValidationError(
                'Не упоминайте название популярного видеохостинга.'
            )
        return data


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Напишите текст поста:',
            'group': 'Выберите к какой группе относится пост:',
            'image': 'Выберите картинку:'
        }
        help_texts = {
            'text': 'Не упоминайте название популярного видеохостинга.',
            'group': 'Это необязательное поле.',
            'image': ('Это необязательное поле. '
                      'Файл должен быть графическим.')
        }

    def clean_text(self) -> str:
        data: str = self.cleaned_data['text']
        if 'youtube' in data.lower():
            raise forms.ValidationError(
                'Не упоминайте название популярного видеохостинга.'
            )
        return data


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('title', 'slug', 'description')
        labels = {
            'title': 'Название группы:',
            'slug': 'Уникальный адрес группы:',
            'description': 'Описание группы:'
        }
        help_texts = {
            'title': 'Название должно содержать не более 200 символов.',
            'slug': 'Только буквы латиницы, цифры и символы -/_.',
            'description': 'Не упоминайте название популярного видеохостинга.'
        }

    def clean_description(self) -> str:
        data: str = self.cleaned_data['description']
        if 'youtube' in data.lower():
            raise forms.ValidationError(
                'Не упоминайте название популярного видеохостинга.'
            )
        return data
