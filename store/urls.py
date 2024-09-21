
from django.urls import path, re_path, include
from . import views
# from django.contrib.auth
from rest_framework.routers import DefaultRouter
# from .views import authView
router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('users', views.UserViewSet)

urlpatterns = [
    
    path('', views.index, name="index"),
    path('', include(router.urls)),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/upload/', views.upload_images, name='upload_images'),
    path('shop/', views.shop, name='shop'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
