from typing import Any
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from blog_app.forms import PostForm
from newspaper.models import Post
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


# function based views
# 80 - 90 % => CRUD
# class based views


class PostListView(ListView):
    model = Post
    template_name = "news_admin/post_list.html"
    # queryset = Post.objects.filter(published_at__isnull=False).order_by("-published_at")
    context_object_name = "posts"

    def get_queryset(self):
        queryset = Post.objects.filter(published_at__isnull=False).order_by(
            "-published_at"
        )
        return queryset


class PostDetailView(DetailView):
    model = Post
    template_name = "news_admin/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(pk=self.kwargs["pk"], published_at__isnull=False)
        return queryset


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "news_admin/draft_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        queryset = Post.objects.filter(published_at__isnull=True)
        return queryset


class DraftDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "news_admin/draft_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(pk=self.kwargs["pk"], published_at__isnull=True)
        return queryset


class DraftPublishView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk, published_at__isnull=True)
        post.published_at = timezone.now()
        post.save()
        return redirect("news_admin:post-list")


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        post.delete()
        return redirect("news_admin:post-list")


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "news_admin/post_create.html"
    form_class = PostForm
    success_url = reverse_lazy("news_admin:post-list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "news_admin/post_create.html"
    form_class = PostForm
    success_url = reverse_lazy("news_admin:post-list")

    def get_success_url(self):
        post = self.get_object()
        if post.published_at:
            return reverse_lazy("news_admin:post-detail", kwargs={"pk": post.pk})
        else:
            return reverse_lazy("news_admin:draft-detail", kwargs={"pk": post.pk})


class PostUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        form = PostForm(instance=post)
        return render(
            request,
            "post_create.html",
            {"form": form},
        )

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            if post.published_at:
                return redirect("news_admin:post-detail", post.pk)
            else:
                return redirect("news_admin:draft-detail", post.pk)
        return render(
            request,
            "post_create.html",
            {"form": form},
        )


@login_required
def post_update(request, pk):
    post = Post.objects.get(pk=pk)
    form = PostForm(instance=post)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            if post.published_at:
                return redirect("news_admin:post-detail", post.pk)
            else:
                return redirect("news_admin:draft-detail", post.pk)

    return render(
        request,
        "news_admin/post_create.html",
        {"form": form},
    )
