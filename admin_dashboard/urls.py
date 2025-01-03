from django.urls import path

from admin_dashboard import views

urlpatterns = [
    path(
        "",
        views.AdminPostListView.as_view(),
        name="admin-post-list",
    ),
    path(
        "post-create/",
        views.AdminPostCreateView.as_view(),
        name="admin-post-create",
    ),
    path(
        "draft-publish/<int:pk>/",
        views.AdminDraftPublishView.as_view(),
        name="admin-draft-publish",
    ),
    path(
        "post-delete/<int:pk>/",
        views.AdminPostDeleteView.as_view(),
        name="admin-post-delete",
    ),
    path(
        "post-update/<int:pk>/",
        views.AdminPostUpdateView.as_view(),
        name="admin-post-update",
    ),
    ## tag
    path(
        "tags/",
        views.AdminTagListView.as_view(),
        name="admin-tag-list",
    ),
    path(
        "tag-create/",
        views.AdminTagCreateView.as_view(),
        name="admin-tag-create",
    ),
    path(
        "tag-delete/<int:pk>/",
        views.AdminTagDeleteView.as_view(),
        name="admin-tag-delete",
    ),
    path(
        "tag-update/<int:pk>/",
        views.AdminTagUpdateView.as_view(),
        name="admin-tag-update",
    ),
    ## category
    path(
        "categories/",
        views.AdminCategoryListView.as_view(),
        name="admin-category-list",
    ),
    path(
        "category-create/",
        views.AdminCategoryCreateView.as_view(),
        name="admin-category-create",
    ),
    path(
        "category-delete/<int:pk>/",
        views.AdminCategoryDeleteView.as_view(),
        name="admin-category-delete",
    ),
    path(
        "category-update/<int:pk>/",
        views.AdminCategoryUpdateView.as_view(),
        name="admin-category-update",
    ),
]
