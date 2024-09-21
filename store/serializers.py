from rest_framework.serializers import ModelSerializer
from .models import Category, Product, User



class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar']
        
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class CategorySerializer(ModelSerializer):

    class Meta: 
        model = Category
        fields = ["id", 'name']


class ProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = [
            'id',  # Thêm id để dễ quản lý
            'product_name',
            'price',
            'sale_price',
            'category',
            'description',
            'image'
            ]


