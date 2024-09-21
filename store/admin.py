from django.contrib import admin
from django import forms
from django.contrib.auth.models import Permission
from .models import Category, Product, User, ProductImage
from django.utils.html import mark_safe
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.html import format_html


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', ]
    search_fields = ['name']


class ProductForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Product
        fields = '__all__'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Số lượng ảnh mặc định trống để thêm mới (1 dòng trống)
    readonly_fields = ['image_tag']
    
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />'.format(obj.image.url))
        return None

    image_tag.short_description = 'Image Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm  # Đảm bảo rằng bạn đã tạo một form phù hợp
    list_display = ('id', 'product_name', 'price', 'sale_price', 'category', 'avatar', 'active')
    search_fields = ['product_name', 'created_date']
    list_filter = ['category', 'active']
    ordering = ['created_date']
    inlines = [ProductImageInline]
    list_per_page = 3

    def avatar(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return mark_safe('<img src="{url}" alt="{alt}" width="130px"/>'.format(url=obj.image.url, alt=obj.product_name))
        return "No image"

    avatar.short_description = 'Image'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_tag', 'uploaded_at']
    list_per_page = 5

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />'.format(obj.image.url))
        return "No image"
    
    image_tag.short_description = 'Image Preview'


admin.site.register(Category, CategoryAdmin)
admin.site.register(User)
admin.site.register(Permission)
