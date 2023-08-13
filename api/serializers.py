from django.contrib.auth.models import Group, User
from rest_framework import serializers
from newspaper.models import Post, Tag, Category


# ORM => Object Relationship Mapping
# Post.objects.all() => SELECT * FROM posts Queryset[<Post 1>, <Post 2>, <Post 3>]
# Post.objects.create(....)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "groups",
            "first_name",
            "is_active",
            "is_superuser",
        ]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "featured_image",
            "views_count",
            "status",
            "published_at",
            "author",
            "tag",
            "category",
        ]

    def validate(self, data):
        data["author"] = self.context["request"].user
        return data
