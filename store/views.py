from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, User, ProductImage, ProductImageForm, Rating
from django.contrib.auth.forms import UserCreationForm
from rest_framework import viewsets, permissions, status, generics
from rest_framework.parsers import MultiPartParser
from .serializers import  UserSerializer
from .serializers import CategorySerializer, ProductSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.forms import modelformset_factory
from django.db.models import Avg
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    # def get_permissions(self):
    #     if self.action == 'list':
    #         return [permissions.AllowAny()]
    #     return [permissions.IsAuthenticated()]

    # list(GET) ==> xem danh sach 
    # ..them(POST) ==> them 
    # detail ==> xem chi tiet 
    # ...(PUT) ==> CAP NHAT
    # ...(DELETE)==> XOA 
    
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        operation_description='API này dùng để ẩn 1 bài viết từ Client',
        responses={
            status.HTTP_200_OK: ProductSerializer()
        }
    )
    @action(methods=['post'], detail=True, url_path="hide-product")
    def hide_product(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            if not product.active:
                return Response({"detail": "Sản phẩm đã bị ẩn rồi."}, status=status.HTTP_400_BAD_REQUEST)

            product.active = False
            product.save()
        except Product.DoesNotExist:
            return Response({"detail": "Sản phẩm không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

        return Response(data=ProductSerializer(product).data, status=status.HTTP_200_OK)


# Create your views here.
def index(request):
    # Lấy tất cả sản phẩm
    products = Product.objects.all()

    # Tính toán điểm đánh giá trung bình cho từng sản phẩm
    for product in products:
        product.average_rating = product.ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    context = {
        'products': products,
    }
    return render(request, 'pages/index.html', {'products': products}, context)


def shop(request):
    return render(request, 'pages/shop.html')


def product_list(request):
    producs = Product.objects.all()
    return render (request , 'pages/product_list.html', {'products': producs})


def upload_images(request, product_id):
    ProductImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, extra=1, can_delete=True)
    product = Product.objects.get(pk=product_id)

    if request.method == 'POST':
        formset = ProductImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.filter(product=product))
        if formset.is_valid():
            for form in formset:
                image_instance = form.save(commit=False)
                image_instance.product = product
                image_instance.save()
            return redirect('product_detail', product_id=product.id)  # Redirect đến trang chi tiết sản phẩm
    else:
        formset = ProductImageFormSet(queryset=ProductImage.objects.filter(product=product))

    return render(request, 'upload_images.html', {'formset': formset, 'product': product})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_images = product.images.all()  # Fetch related images

    # Tính toán điểm đánh giá trung bình
    average_rating = product.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Lấy tất cả đánh giá của sản phẩm
    ratings = product.ratings.all()

    context = {
        'product': product,
        'product_images': product_images,
        'average_rating': average_rating,
        'ratings': ratings,
    }
    return render(request, 'pages/product_detail.html', context)


@receiver(post_save, sender=Rating)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    average_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    product.average_rating = average_rating if average_rating else 0
    product.save()


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Tên người dùng đã tồn tại.')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()
                messages.success(request, 'Đăng ký thành công!')
                return redirect('login')
        else:
            messages.error(request, 'Mật khẩu không khớp.')
    
    return render(request, 'pages/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')  # Chuyển hướng sau khi đăng nhập thành công
        else:
            messages.error(request, 'Tên người dùng hoặc mật khẩu không chính xác.')
    
    return render(request, 'pages/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
