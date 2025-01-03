# from django.db import models


# # Create your models here.
# class Offer(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     product_image = models.ImageField(upload_to="offer_images/")


# class Tag(models.Model):
#     name = models.CharField(max_length=100)


# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     image = models.ImageField(upload_to="category_images/")


# class CustomerReview(models.Model):
#     description = models.TextField()
#     rating = models.IntegerField(max_value=5, min_value=1)
#     product = models.ForeignKey("Product", on_delete=models.CASCADE)


# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     discount = models.IntegerField(default=0)
#     product_image = models.ImageField(upload_to="product_images/")
#     tag = models.ManyToManyField(Tag)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     is_offer = models.BooleanField(default=False)


# # 1 product can have multiple reviews => M
# # 1 review can be in only 1 product => 1


# #
# # 1 product can have multiple tag => M
# # 1 tag can be used in multiple product => M


# # 1 category can have multiple products => M
# # 1 product can be in only 1 category => 1
