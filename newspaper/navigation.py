from django.db.models import Case, F, Sum, When

from newspaper.models import Category, Post, Tag


def navigation(request):
    categories = Category.objects.all()
    tags = Tag.objects.all()[:10]
    # Get the post with the highest views_count of posts in each category
    top_categories = (
        Post.objects.values("category__pk", "category__name")
        .annotate(
            pk=F("category__pk"), name=F("category__name"), max_views=Sum("views_count")
        )
        .order_by("-views_count")
        .values("pk", "name", "max_views")
    )
    # print(top_categories)
    category_ids = [top_category["pk"] for top_category in top_categories]  # [2,6,5,6]
    order_by_max_views = Case(
        *[
            When(
                id=category["pk"], then=category["max_views"]
            )  # When(id=2, then=11), When(id=6,then=2)
            for category in top_categories
        ]
    )
    whats_new_categories = Category.objects.filter(pk__in=category_ids).order_by(
        -order_by_max_views
    )[:4]
    top_categories = Category.objects.filter(pk__in=category_ids).order_by(
        -order_by_max_views
    )[:3]

    trending_posts = Post.objects.filter(
        published_at__isnull=False, status="active"
    ).order_by("-views_count")[:3]

    # print(top_categories)

    return {
        "categories": categories,
        "tags": tags,
        "trending_posts": trending_posts,
        "top_categories": top_categories,
        "whats_new_categories": whats_new_categories,
    }
