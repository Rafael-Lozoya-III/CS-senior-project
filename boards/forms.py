from django import forms
from .models import Thread, Post


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Thread title...'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Start the discussion...'
            }),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write a reply...'
            }),
        }