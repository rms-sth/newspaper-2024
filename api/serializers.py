from django.contrib.auth.models import Group, User
from rest_framework import serializers

from newspaper.models import Category, Comment, Contact, Newsletter, Post, Tag


# ORM => Object Relationship Mapping
# Post.objects.all() => SELECT * FROM posts; => Queryset[<Post 1>, <Post 2>, <Post 3>]
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
            "status",
            "tag",
            "category",
            # read only
            "author",
            "views_count",
            "published_at",
        ]
        extra_kwargs = {
            "author": {"read_only": True},
            "views_count": {"read_only": True},
            "published_at": {"read_only": True},
        }

    def validate(self, data):
        data["author"] = self.context["request"].user
        return data


class PostPublishSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


# class CommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Comment
#         fields = "__all__"
#         extra_kwargs = {"post": {"required": False}}

#     def create(self, validated_data):
#         post_id = self.context["view"].kwargs.get("post_id")
#         validated_data["post_id"] = post_id
#         return super().create(validated_data)


from django.contrib.auth.models import User
from rest_framework import serializers
from newspaper.models import UserProfile


# UserProfile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["image", "address", "biography"]


# User Serializer with embedded UserProfile data
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(
        source="userprofile", read_only=True
    )  # Fetch related UserProfile

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile"]


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def get_token(self, user):
        token = super().get_token(user)

        # Serialize the user data
        user_data = UserSerializer(user).data

        # Add user information to the token
        token["user"] = user_data  # Embedding full user data (including profile)

        return token


# from rest_framework_simplejwt.serializers import TokenRefreshSerializer
# from rest_framework_simplejwt.tokens import RefreshToken


# class CustomTokenRefreshSerializer(TokenRefreshSerializer):
#     def validate(self, attrs):
#         data = super().validate(attrs)  # Get the new access token

#         # Decode refresh token to get the user
#         refresh = RefreshToken(attrs["refresh"])
#         user = User.objects.get(id=refresh["user_id"])  # Retrieve user from token

#         # Add user data to the response
#         data["user"] = UserSerializer(user).data  # Embed full user details

#         return data
