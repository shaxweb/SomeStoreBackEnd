from django.db import models


class User(models.Model):
    username = models.CharField(max_length=24)
    password = models.CharField(max_length=32)
    email = models.EmailField()
    is_salesman = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)


class WaitUser(models.Model):
    username = models.CharField(max_length=24)
    password = models.CharField(max_length=32)
    email = models.EmailField()
    token = models.TextField()
    registered_at = models.DateTimeField(auto_now_add=True)


class Categories(models.Model):
    title = models.CharField(max_length=24)


class Product(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    title = models.CharField(max_length=32)
    description = models.TextField()
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/")
    registered_at = models.DateTimeField(auto_now_add=True)


# class TgProductImage(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     image_id = models.TextField()


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    registered_at = models.DateTimeField(auto_now_add=True)

