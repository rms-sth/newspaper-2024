from django import forms
from django_summernote.widgets import SummernoteWidget

from newspaper.models import Category, Post, Tag


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ("author", "views_count", "published_at")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter the title of post",
                }
            ),
            "content": SummernoteWidget(),
            "status": forms.Select(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "tag": forms.SelectMultiple(attrs={"class": "form-control"}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        exclude = "__all__"
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter the name of tag",
                }
            ),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = "__all__"
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter the name of category",
                }
            ),
        }