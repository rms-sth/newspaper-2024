from django.db.models import Sum
from django.db.models.functions import Coalesce

from newspaper.models import Category, Post, Tag


def navigation(request):
    categories = Category.objects.all()
    tags = Tag.objects.all()[:10]
    # Calculate total views per category and get top categories directly
    categories_with_views = Category.objects.annotate(
        total_views=Coalesce(Sum("post__views_count"), 0)
    ).order_by("-total_views")

    # print(categories_with_views.query)

    whats_new_categories = categories_with_views[:4]
    top_categories = categories_with_views[:3]

    # Print results (optional)
    # print(top_categories.values("pk", "name", "total_views"))
    # [
    #     {"pk": 3, "name": "economy", "total_views": 55},
    #     {"pk": 1, "name": "cover", "total_views": 42},
    #     {"pk": 5, "name": "technology", "total_views": 8},
    # ]

    trending_posts = Post.objects.filter(
        published_at__isnull=False, status="active"
    ).order_by("-views_count")[:3]

    return {
        "categories": categories,
        "tags": tags,
        "trending_posts": trending_posts,
        "top_categories": top_categories,
        "whats_new_categories": whats_new_categories,
    }


# from django.db.models import Case, F, Sum, When

# from newspaper.models import Category, Post, Tag

# def navigation(request):
#     categories = Category.objects.all()
#     tags = Tag.objects.all()[:10]
#     # Get the post with the highest views_count of posts in each category
#     top_categories = (
#         Post.objects.annotate(
#             pk=F("category__pk"), name=F("category__name"), max_views=Sum("views_count")
#         )
#         .order_by("-views_count")
#         .values("pk", "name", "max_views")
#     )
#     print(top_categories)

#     # output of pk=F("category__pk"), name=F("category__name")
#     # [
#     #     {"pk": 3, "name": "economy", "max_views": 27},
#     #     {"pk": 1, "name": "cover", "max_views": 25},
#     #     {"pk": 1, "name": "cover", "max_views": 17},
#     #     {"pk": 5, "name": "technology", "max_views": 8},
#     #     {"pk": 4, "name": "politics", "max_views": 6},
#     #     {"pk": 3, "name": "economy", "max_views": 4},
#     #     {"pk": 2, "name": "society", "max_views": 0},
#     # ]

#     #### FInal result
#     # {"pk":1, "name":"politics", "views_count": 3}
#     # {"pk":2, "name":"technology", "views_count": 2}

#     category_ids = [top_category["pk"] for top_category in top_categories]  # [2,6,5,6]
#     order_by_max_views = Case(
#         *[
#             When(
#                 id=category["pk"], then=category["max_views"]
#             )  # When(id=2, then=11), When(id=6,then=2)
#             for category in top_categories
#         ]
#     )
#     whats_new_categories = Category.objects.filter(pk__in=category_ids).order_by(
#         -order_by_max_views
#     )[:4]
#     top_categories = Category.objects.filter(pk__in=category_ids).order_by(
#         -order_by_max_views
#     )[:3]

#     trending_posts = Post.objects.filter(
#         published_at__isnull=False, status="active"
#     ).order_by("-views_count")[:3]

#     # print(top_categories)

#     return {
#         "categories": categories,
#         "tags": tags,
#         "trending_posts": trending_posts,
#         "top_categories": top_categories,
#         "whats_new_categories": whats_new_categories,
#     }
