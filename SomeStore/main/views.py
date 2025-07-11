from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.views import LoginView
from rest_framework.response import Response
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.urls import reverse
from django.views import View
import requests, secrets
import json, time

from .serializers import *
from .models import *
from .funcs import *

bot_token = "8158445939:AAHmoesq6Em6F5QdxcNhRJYSVL2pTLpUyn0"


class StartAPi(APIView):
    def get(self, request):
        data = "meta"
        return Response({"status": True, "message": "Hello, World", "data": data})


class GetDataApi(APIView):
    def get(self, request):
        data = request.GET
        print(data)
        user_id, product_id, basket_id = data.get("user_id"), data.get("product_id"), data.get("basket_id")
        result = []
        if data.get("user_id"):
            user = User.objects.filter(id=user_id).first()
            user_ser = UserSerializer(user)
            result.append({"user": user_ser.data} if user else None)
        if product_id:
            product = Product.objects.filter(id=product_id).first()
            product_ser = ProductSerializer(product)
            result.append({"product": product_ser.data} if product else None)
        if basket_id:
            basket = Basket.objects.filter(id=basket_id).first()
            basket_ser = BasketSerializer(basket)
            result.append({"basket": basket_ser.data} if basket else None)

        return Response({"status": True, "result": result})


class GetAllDatasApi(APIView):
    def get(self, request):
        users = User.objects.all()
        wait_users = WaitUser.objects.all()
        products = Product.objects.all()
        categories = Categories.objects.all()
        baskets = Basket.objects.all()
        users = UserSerializer(users, many=True)
        wait_users = WaitUserSerializer(wait_users, many=True)
        products = ProductSerializer(products, many=True)
        categories = CategoriesSerializer(categories, many=True)
        baskets = BasketSerializer(baskets, many=True)

        return Response({"status": True, "all": {"users": len(users.data), "wait_users": len(wait_users.data), "products": len(products.data), "baskets": len(baskets.data)}, "users": users.data, "wait_users": wait_users.data, "products": products.data, "categories": categories.data, "baskets": baskets.data})


class GetProductsApi(APIView):
    def get(self, request):
        products = Product.objects.all()
        response_data = []
        # products = ProductSerializer(products, many=True)
        for product in products:
            serialized_product = ProductSerializer(product)
            serialized_product.images = []
            images = TgProductImage.objects.filter(product=product)

            for img in images:
                file_id = img.image_id
                file_info = requests.get(f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}")

                if file_info.status_code == 200:
                    file_path = file_info.json()["result"]["file_path"]
                    image_download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                    image_response = requests.get(image_download_url)

                    if image_response.status_code == 200:
                        serialized_product["images"].append(image_response.content)
                    else:
                        serialized_product["images"].append(None)
                else:
                    serialized_product["images"].append(None)

            response_data.append(serialized_product)
        return Response({"status": True, "message": "in data", "data": response_data})


class RegisterUserApi(APIView):
    def get(self, request):
        return Response({"status": False, "error": "get not allowed"})

    def post(self, request):
        data = json.loads(request.body)
        username, password, password2, email = data.get("username"), data.get("password"), data.get("password2"), data.get("email")
        if username and password and email and password2:
            username_is_have = User.objects.filter(username=username)
            email_is_have = User.objects.filter(email=email)
            if username_is_have:
                return Response({"status": False, "error": "username already taked", "type": "username"})
            if email_is_have:
                return Response({"status": False, "error": "email already taked", "type": "email"})

            check_username = check_datas("username", username)
            if not check_username["status"]:
                return Response({"status": False, "error": check_username["error"], "type": "username"})
            check_email = check_datas("email", email)
            if not check_email["status"]:
                return Response({"status": False, "error": check_email["error"], "type": "email"})
            check_password = check_datas("password", password, password2)
            if not check_password["status"]:
                return Response({"status": False, "error": check_password["error"], "type": "password"})

            user = WaitUser()
            token = send_token_to_email(email)
            if token["status"]:
                user.username = username
                user.password = password
                user.email = email
                user.token = token["token"]
                user.save()
                return Response({"status": True, "message": f"token was sent to {email}"})

            return Response({"status": False, "error": token["error"]})

        return Response({"statis": False, "error": "uncorrect datas"})


class AuthUserApi(APIView):
    def get(self, request):
        token = request.GET.get("token")
        if token:
            wait_user = WaitUser.objects.filter(token=token).first()
            if wait_user:
                user = User()
                user.username = wait_user.username
                user.password = wait_user.password
                user.email = wait_user.email
                user.save()

                del_username = WaitUser.objects.filter(username=wait_user.username)
                del_email = WaitUser.objects.filter(email=wait_user.email)
                del_username.delete()
                del_email.delete()

                return Response({"status": True, "message": f"user {wait_user.username} was registered"})
            return Response({"status": False, "error": "user not found or token was broken"})

        return Response({"status": False, "error": "token not found"})


class LoginUserApi(APIView):
    def get(self, request):
        return Response({"status": False, "error": "get not allowed"})

    def post(self, request):
        data = json.loads(request.body)
        username, password = data.get("username"), data.get("password")
        if username and password:
            user = User.objects.filter(username=username).first()
            if user:
                if password == user.password:
                    user_agent = request.META.get("HTTP_USER_AGENT", "")
                    user_ser = UserSerializer(user)
                    send_login_message_to_mail(user.email, user_agent)
                    return Response({"status": True, "message": "successfully", "data": user_ser.data})
                return Response({"status": False, "error": "uncorrect password", "type": "password"})
            return Response({"status": False, "error": f"user {username} not found", "type": "username"})

        return Response({"status": False, "error": "uncorrect datas", "type": "all"})


class CreateProductApi(APIView):
    def get(self, request):
        return Response({"status": False, "message": "get not allowed"})

    def post(self, request):
        data = json.loads(request.body)
        author, category, title, description, price = data.get("author"), data.get("category"), data.get("title"), data.get("description"), data.get("price")
        images = request.FILES.getlist("images")
        tg_images = data.get("tg_images")
        if author and category and title and description and price:
            user = User.objects.filter(id=author).first()
            category = Categories.objects.filter(id=category).first()
            if user and category:
                product = Product()
                product.author = user
                product.category = category
                product.title = title
                product.description = description
                product.price = price
                product.save()
                if images:
                    for image in images:
                        ProductImage.objects.create(product=product, image=image)
                    return Response({"status": True, "message": f"product {title} was created"})
                if tg_images:
                    for image in tg_images:
                        # file_path = get_tg_file_path(image)
                        TgProductImage.objects.create(product=product, image_id=image)
                    return Response({"status": True, "message": f"product {title} was created"})
                return Response({"status": False, "error": "uncorrect datas"})

            return Response({"status": False, "error": "user or category not found"})

        return Response({"status": False, "error": "uncorrect datas"})


class CreateBasketApi(APIView):
    def get(self, request):
        return Response({"status": False, "message": "get not allowed"})

    def post(self, request):
        data = json.loads(request.body)
        author = data.get("author")
        product = data.get("product")
        user = User.objects.get(id=author)
        product = Product.objects.get(id=product)

        if author and product:
            basket = Basket()
            basket.author = user
            basket.product = product
            basket.save()
            return Response({"status": True, "message": "basket created"})

        return Response({"statis": False, "error": "uncorrect datas"})


class WatchClassApi(APIView):
    def get(self, request):
        return Response({"status": True, "message": "Thanks for check"})


class ClearDatasApi(APIView):
    def get(self, request):
        User.objects.all().delete()
        WaitUser.objects.all().delete()
        Product.objects.all().delete()
        Basket.objects.all().delete()
        return Response({"status": True, "message": "cleaned"})


class CreateUserApi(APIView):
    def get(self, request):
        User.objects.create(username="shaxrux", password="shaxcoder", email="shaxrux243@gmail.com")
        Categories.objects.create(title="Cars")
        Categories.objects.create(title="Houses")
        Categories.objects.create(title="Other")
        return Response({"status": True, "message": "User Created"})
