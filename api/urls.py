from django.urls import include, path
from rest_framework import routers

from api import views

app_name = "api"

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r"tags", views.TagViewSet)
router.register(r"categories", views.CategoryViewSet)
router.register(r"posts", views.PostViewSet)
router.register(r"newsletters", views.NewsletterViewSet)
router.register(r"contacts", views.ContactViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path(
        "api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
    path(
        "draft-list/",
        views.DraftListViewSet.as_view(),
        name="draft-list-api",
    ),
    path(
        "draft-detail/<int:pk>/",
        views.DraftDetailView.as_view(),
        name="draft-detail-api",
    ),
    path(
        "post-by-category/<int:category_id>/",
        views.PostListByCategoryViewSet.as_view(),
        name="post-list-by-category-api",
    ),
    path(
        "post-by-tag/<int:tag_id>/",
        views.PostListByTagViewSet.as_view(),
        name="post-list-by-tag-api",
    ),
    path(
        "post-publish/",
        views.PostPublishViewSet.as_view(),
        name="post-publish-api",
    ),
    path(
        "post/<int:post_id>/comments/",
        views.CommentViewSet.as_view(),
        name="comment-api",
    ),
    path(
        "top-categories/",
        views.TopCategoriesListViewSet.as_view(),
        name="top-categories-api",
    ),
]


from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns += [
    path(
        "token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),  # Login to get tokens
    path(
        "token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),  # Refresh token
]
