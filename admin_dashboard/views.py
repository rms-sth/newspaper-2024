from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, View, UpdateView

from admin_dashboard.forms import CategoryForm, PostForm, TagForm
from newspaper.models import Category, Post, Tag

from django.utils import timezone
from django.shortcuts import redirect


# Create your views here.
class AdminPostListView(ListView):
    model = Post
    template_name = "admin_dashboard/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.all().order_by("-published_at")


class AdminPostCreateView(CreateView):
    model = Post
    template_name = "admin_dashboard/post_create.html"
    form_class = PostForm
    success_url = reverse_lazy("admin-post-list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class AdminDraftPublishView(View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk, published_at__isnull=True)
        post.published_at = timezone.now()
        post.save()
        return redirect("admin-post-list")


class AdminPostDeleteView(View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        post.delete()
        return redirect("admin-post-list")


class AdminPostUpdateView(UpdateView):
    model = Post
    template_name = "admin_dashboard/post_create.html"
    form_class = PostForm
    success_url = reverse_lazy("admin-post-list")


######### Tag


class AdminTagListView(ListView):
    model = Tag
    template_name = "admin_dashboard/tag_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        return Tag.objects.all()

class AdminTagCreateView(CreateView):
    model = Tag
    template_name = "admin_dashboard/tag_create.html"
    form_class = TagForm
    success_url = reverse_lazy("admin-tag-list")


class AdminTagDeleteView(View):
    def get(self, request, pk):
        tag = Tag.objects.get(pk=pk)
        tag.delete()
        return redirect("admin-tag-list")


class AdminTagUpdateView(UpdateView):
    model = Tag
    template_name = "admin_dashboard/tag_create.html"
    form_class = TagForm
    success_url = reverse_lazy("admin-tag-list")


######### Category


class AdminCategoryListView(ListView):
    model = Category
    template_name = "admin_dashboard/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.all()


class AdminCategoryCreateView(CreateView):
    model = Category
    template_name = "admin_dashboard/category_create.html"
    form_class = CategoryForm
    success_url = reverse_lazy("admin-category-list")


class AdminCategoryDeleteView(View):
    def get(self, request, pk):
        category = Category.objects.get(pk=pk)
        category.delete()
        return redirect("admin-category-list")


class AdminCategoryUpdateView(UpdateView):
    model = Category
    template_name = "admin_dashboard/category_create.html"
    form_class = CategoryForm
    success_url = reverse_lazy("admin-category-list")
