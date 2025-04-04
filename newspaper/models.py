from django.db import models


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Don't create table in DB


class Category(TimeStampModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Tag(TimeStampModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(TimeStampModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("in_active", "Inactive"),
    ]
    title = models.CharField(max_length=200)
    content = models.TextField()
    featured_image = models.ImageField(upload_to="post_images/%Y/%m/%d", blank=False)
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    views_count = models.PositiveBigIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title

    # Fat model and thin views
    @property
    def latest_comments(self):
        comments = Comment.objects.filter(post=self).order_by("-created_at")
        return comments

    def humanized_published_at(self):
        from django.utils import timezone
        from django.utils.timesince import timesince

        now = timezone.now()
        diff = now - self.published_at

        if diff.total_seconds() < 60:  # Less than 1 minute
            return "Just now"
        elif diff < timezone.timedelta(days=1):  # Less than 24 hours
            return f"{timesince(self.published_at)} ago"
        else:
            return self.published_at.strftime("%B %d, %Y")  # "January 12, 2025"


class Contact(TimeStampModel):
    message = models.TextField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["created_at"]
        # db_table = 'contact'


class UserProfile(TimeStampModel):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="user_images/%Y/%m/%d", blank=False)
    address = models.CharField(max_length=200)
    biography = models.TextField()

    def __str__(self):
        return self.user.username


class Comment(TimeStampModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()
    name = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return f"{self.email} | {self.comment[:70]}"

    @property
    def initials(self):
        name_parts = self.name.split()
        if len(name_parts) > 1:
            return f"{name_parts[0][0]}{name_parts[-1][0]}"
        return name_parts[0][0] * 2


class Newsletter(TimeStampModel):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


## 1 - 1 Relationship
# 1 user can have 1 profile => 1
# 1 profile is associated to 1 user  => 1
# OneToOneField() => Can be used in Any Model


## 1 - M Relationship
# 1 user can post M post  => M
# 1 post is associated to only 1 user => 1
# In django use ForeignKey() => Must be used in Many side

# 1 category can have M posts => M
# 1 post is associated to only 1 category => 1


# 1 tag can have M posts => M
# 1 post can have M tags => M


## M - M Relationship
# 1 student can learn from M teachers => M
# 1 teacher can teach M students => M
# ManyToManyField() => Can be used in Any Model

# 1 post can contain M tag => M
# 1 tag can be used in M post => M

# 1 post can be associated to only 1 category => 1
# 1 category can contains M post => M
