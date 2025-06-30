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


class StartAPi(APIView):
    def get(self, request):
        return Response({"status": True, "message": "Hello, World"})


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


class RegisterUserApi(APIView):
    def get(self, request):
        return Response({"status": False, "error": "get not allowed"})

    def post(self, request):
        data = json.loads(request.body)
        username, password, email = data.get("username"), data.get("password"), data.get("email")
        if username and password and email:
            username_is_have = User.objects.filter(username=username)
            email_is_have = User.objects.filter(email=email)
            if username_is_have:
                return Response({"status": False, "error": "username already taked"})
            if email_is_have:
                return Response({"status": False, "error": "email already taked"})
            
            check_username = check_datas("username", username)
            if not check_username["status"]:
            	return Response({"status": False, "error": check_username["error"]})
            check_email = check_datas("email", email)
            if not check_email["status"]:
            	return Response({"status": False, "error": check_email["error"]})

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


class CreateProductApi(APIView):
    def get(self, request):
        return Response({"status": False, "message": "get not allowed"})

    def post(self, request):
        data = json.loads(request.body)
        author, category, title, description, price = data.get("author"), data.get("category"), data.get("title"), data.get("description"), data.get("price")
        if author and category and title and description and price:
            user = User.objects.get(id=author)
            category = Categories.objects.get(id=category)
            if user and category:
                product = Product()
                product.author = user
                product.category = category
                product.title = title
                product.description = description
                product.price = price
                product.save()
                return Response({"status": True, "message": f"product {title} was created"})

            return Response({"statis": False, "error": "user or category not found"})

        return Response({"statis": False, "error": "uncorrect datas"})


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

try:
	user = User.objects.get(id=1)
	user.delete()
	user = User.objects.get(id=2)
	user.delete()
except Exception as e:
	pass