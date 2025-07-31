from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
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
import asyncio

from .serializers import *
from .models import *
from .funcs import *


class StartAPi(APIView):
    def get(self, request):
        data = "meta datas"
        return Response({"status": True, "message": "Hello, World", "data": data})


class GetAppView(View):
	def get(self, request):
		return render(request, "download.html")


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

        return Response({"status": True, "all": {"users": len(users.data), "wait_users": len(wait_users.data), "products": len(products.data), "categories": len(categories.data), "baskets": len(baskets.data)}, "users": users.data, "wait_users": wait_users.data, "products": products.data, "categories": categories.data, "baskets": baskets.data})


class GetProductsApi(APIView):
    def get(self, request):
        products = Product.objects.all()
        products = ProductSerializer(products, many=True)
        return Response({"status": True, "message": "in data", "data": products.data})


class GetUserBasketApi(APIView):
	def get(self, request):
		return Response({"status": False, "error": "get not allowed"})
	
	def post(self, request):
		data = request.data
		user_id = data.get("user_id")
		if user_id:
			user = User.objects.filter(id=user_id).first()
			if user:
				baskets = Basket.objects.filter(user=user)
				baskets = BasketSerializer(baskets, many=True)
				return Response({"status": True, "message": "in data", "data": baskets.data})
			return Response({"status": False, "error": "user not found"})
		return Response({"status": False, "error": "uncorrect datas"})


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
                user.password = make_password(password)
                user.email = email
                user.token = token["token"]
                user.save()
                return Response({"status": True, "message": f"token was sent to {email}"})

            return Response({"status": False, "error_email": token["error"]})

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
                if check_password(password, user.password):
                    user_agent = request.META.get("HTTP_USER_AGENT", "")
                    user_ser = UserSerializer(user)
                    send_login_message_to_mail(user.email, user_agent)
                    return Response({"status": True, "message": "successfully", "data": user_ser.data})
                return Response({"status": False, "error": "uncorrect password", "type": "password", "my": user.password, "your": make_password(password)})
            return Response({"status": False, "error": f"user {username} not found", "type": "username"})

        return Response({"status": False, "error": "uncorrect datas", "type": "all"})


class CheckUserApi(APIView):
	def get(self, request):
		return Response({"status": False, "error": "Get Not Allowed"})
	
	def post(self, request):
		data = request.data
		user_id = data.get("user_id")
		password = data.get("password")
		if user_id and password:
			user = User.objects.filter(id=user_id).first()
			if user:
				if check_password(password, user.password):
					return Response({"status": True, "message": "password successfully checked"})
				return Response({"status": False, "error": "uncorrect password"})
			return Response({"status": False, "error": "user not found"})
		return Response({"status": False, "error": "uncorrect datas"})


class CreateProductApi(APIView):
    def get(self, request):
        return Response({"status": False, "message": "get not allowed"})

    def post(self, request):
        data = request.data
        author, category, title, description, price = data.get("author"), data.get("category"), data.get("title"), data.get("description"), data.get("price")
        images = request.FILES.getlist("images")
        if author and category and title and description and price and images:
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
                for image in images:
                    ProductImage.objects.create(product=product, image=image)
                
                return Response({"status": True, "message": f"product '{title}' was created"})

            return Response({"status": False, "error": "user or category not found"})

        return Response({"status": False, "error": "uncorrect datas"})


class CreateBasketApi(APIView):
    def get(self, request):
        return Response({"status": False, "message": "get not allowed"})

    def post(self, request):
        data = json.loads(request.body)
        user_id = data.get("user_id")
        product_id = data.get("product_id")
        
        if user_id and product_id:
        	user = User.objects.filter(id=user_id).first()
        	product = Product.objects.filter(id=product_id).first()
        	
        	if user:
        		if product:
        			have_basket = Basket.objects.filter(user=user, product=product).first()
        			if have_basket:
        				have_basket.quantity = have_basket.quantity + 1
        				have_basket.save()
        				return Response({"status": True, "message": "basket added"})
        			basket = Basket()
        			basket.user = user
        			basket.product = product
        			basket.save()
        			return Response({"status": True, "message": "basket created"})
        		return Response({"status": False, "error": "product not found"})
        	return Response({"status": False, "error": "user not found"})
        return Response({"statis": False, "error": "uncorrect datas"})


class ClearDatasApi(APIView):
    def get(self, request):
        User.objects.all().delete()
        WaitUser.objects.all().delete()
        Product.objects.all().delete()
        ProductImage.objects.all().delete()
        Basket.objects.all().delete()
        Categories.objects.all().delete()
        return Response({"status": True, "message": "cleaned"})


class CreateUserApi(APIView):
    def get(self, request):
        User.objects.create(username="shaxcoder", password=make_password("shaxcoder"), email="shaxrux243@gmail.com")
        Categories.objects.create(title="Cars")
        Categories.objects.create(title="Houses")
        Categories.objects.create(title="Other")
        return Response({"status": True, "message": "User Created"})


class CreateCategoryApi(APIView):
	def get(self, request):
		return Response({"status": False, "message": "get not allowed"})
	
	def post(self, request):
		data = request.data
		title = data.get("title")
		if title:
			Categories.objects.create(title=title)
			return Response({"status": True, "message": f"category {title} was created!"})
		return Response({"status": False, "error": "uncorrect datas"})


class CreateSalesmanApi(APIView):
	def post(self, request):
		user_id = request.data.get("user_id")
		user = User.objects.filter(id=user_id)
		if user.exists():
			user = user.first()
			user.is_salesman = True
			user.save()
			return Response({"status": True, "message": "been"})	
		return Response({"status": False, "error": "user not found"})


class DeleteProductApi(APIView):
	def get(self, request):
		return Response({"status": False, "error": "GET Not Allowed"})
	
	def post(self, request):
		data = request.data
		product_id = data.get("product_id")
		product = Product.objects.filter(id=product_id)
		if product:
			Product.objects.get(id=product_id).delete()
			return Response({"status": True, "message": "product successfully deleted"})
		return Response({"status": False, "error": "product not found"})


class DeleteBasketApi(APIView):
	def get(self, request):
		return Response({"status": False, "error": "get not allowed"})
	
	def post(self, request):
		data = request.data
		user_id = data.get("user_id")
		product_id = data.get("product_id")
		if user_id and product_id:
			user = User.objects.filter(id=user_id).first()
			if user:
				product = Product.objects.filter(id=product_id).first()
				if product:
					basket = Basket.objects.filter(user=user, product=product).first()
					if basket:
						if basket.quantity == 1:
							basket.delete()
						else:
							basket.quantity -= 1
							basket.save()
						return Response({"status": True, "message": "basket removed"})
				return Response({"status": False, "error": "product not found"})
			return Response({"status": False, "error": "user not found"})
		return Response({"status": False, "error": "uncorrect datas"})


class DeleteBasketFullApi(APIView):
	def get(self, request):
		return Response({"status": False, "error": "get not allowed"})
	
	def post(self, request):
		dara = request.data
		basket_id = data.get("basket_id")
		user_id = data.get("user_id")
		if basket_id and user_id:
			user = User.objects.filter(id=user_id).first()
			basket = Basket.objects.filter(id=basket_id, user=user).first()
			if basket:
				basket.delete()
				return Response({"status": True, "message": "basket successfully deleted"})
			return Response({"status": False, "error": "basket not found"})
		return Response({"status": False, "error": "uncorrect datas"})


class SearchProductsApi(APIView):
	def get(self, request):
		query = request.GET.get("q")
		if query:
			products = Product.objects.all()
			products = ProductSerializer(products, many=True)
			products = search_products(query, products.data)
			return Response({"status": True, "message": "in data", "data": products})
		return Response({"status": False, "error": "uncorrect get"})


class PingPageApi(APIView):
	def get(self, request):
		return Response({"status": True, "message": "Waked!"})





class MyAppsApi(APIView):
	def get(self, request):
		apps = {
		    "tasbih": {
		        "update_id": 5,
		        "version": "1.0.5",
		        "url": "https://t.me/ShaxcoderApps/9"
		    }
		}
		return Response({"status": True, "message": apps})

