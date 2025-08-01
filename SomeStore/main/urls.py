from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.StartAPi.as_view()),
    path('get_all_datas/', views.GetAllDatasApi.as_view()),
    path('get_data/', views.GetDataApi.as_view()),
    path('get_products/', views.GetProductsApi.as_view()),
    path('get_user_baskets/', views.GetUserBasketApi.as_view()),
    path('register/', views.RegisterUserApi.as_view()),
    path('login/', views.LoginUserApi.as_view()),
    path('auth/', views.AuthUserApi.as_view()),
    path('check_user/', views.CheckUserApi.as_view()),
    path('create_product/', views.CreateProductApi.as_view()),
    path('create_basket/', views.CreateBasketApi.as_view()),
    path('clear_datas/', views.ClearDatasApi.as_view()),
    path('create_user/', views.CreateUserApi.as_view()),
    path('create_salesman/', views.CreateSalesmanApi.as_view()),
    path('ping/', views.PingPageApi.as_view()),
    path('create_category/', views.CreateCategoryApi.as_view()),
    path('delete_product/', views.DeleteProductApi.as_view()),
    path('delete_basket/', views.DeleteBasketApi.as_view()),
    path('delete_basket_full/', views.DeleteBasketFullApi.as_view()),
    
    path('search/', views.SearchProductsApi.as_view()),
    path('get_app/', views.GetAppView.as_view()),
    
    path('my_apps/', views.MyAppsApi.as_view()),
]