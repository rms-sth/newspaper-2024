from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from newspaper.models import (
    Category,
    Comment,
    Contact,
    Newsletter,
    Post,
    Tag,
    UserProfile,
)

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Contact)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Newsletter)


class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ("content",)
    list_display = ["title", "category", "author", "created_at"]
    date_hierarchy = "published_at"


admin.site.register(Post, PostAdmin)


# from django.contrib import admin
# from django_summernote.admin import SummernoteModelAdmin
# from .models import Category, Comment, Contact, Newsletter, Post, Tag, UserProfile


# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ("name", "created_at", "updated_at")
#     search_fields = ("name",)
#     ordering = ("name",)
#     date_hierarchy = "created_at"


# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ("name", "created_at", "updated_at")
#     search_fields = ("name",)
#     ordering = ("name",)
#     date_hierarchy = "created_at"


# @admin.register(Post)
# class PostAdmin(SummernoteModelAdmin):
#     summernote_fields = ("content",)
#     list_display = (
#         "title",
#         "category",
#         "author",
#         "status",
#         "views_count",
#         "created_at",
#         "published_at",
#     )
#     list_filter = ("status", "category", "author", "created_at", "published_at")
#     search_fields = ("title", "content", "author__username", "category__name")
#     date_hierarchy = "published_at"
#     ordering = ("-published_at",)
#     list_editable = ("status",)
#     autocomplete_fields = (
#         "category",
#         "author",
#     )  # Improves performance for large datasets
#     filter_horizontal = ("tag",)  # Better UI for ManyToManyField
#     readonly_fields = ("views_count",)  # Prevent modification
#     fieldsets = (
#         (
#             "Post Details",
#             {
#                 "fields": (
#                     "title",
#                     "content",
#                     "featured_image",
#                     "author",
#                     "category",
#                     "tag",
#                 )
#             },
#         ),
#         ("Status & Publication", {"fields": ("status", "views_count", "published_at")}),
#     )


