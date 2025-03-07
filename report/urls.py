from django.urls import path

from report import views

app_name = "report"

urlpatterns = [
    path(
        "users/",
        views.UserReportView.as_view(),
        name="users",
    ),
    path(
        "posts/",
        views.PostReportView.as_view(),
        name="posts",
    ),
    path(
        "pdf-file/post-download/",
        views.PDFFileDownloadView.as_view(),
        name="post-pdf-download",
    ),
    path(
        "pdf-file/post-view/",
        views.PostPdfFileView.as_view(),
        name="post-pdf-view",
    ),
]
