from rest_framework import serializers
from .models import *

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
        
class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    stock = StockSerializer(read_only=True)  # Include stock info

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'selling_price', 'discounted_price', 'description',
            'composition', 'prodapp', 'category', 'product_image',
            'average_rating', 'stock'  # Add stock here
        ]

    def get_average_rating(self, obj):
        return obj.average_rating

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    total_cost = serializers.ReadOnlyField()
    product = ProductSerializer(read_only=True)  # For reading product details
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        write_only=True  # For writing product ID
    )

    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_id', 'quantity', 'total_cost']
        read_only_fields = ['user']

    def create(self, validated_data):
        return super().create(validated_data)
    
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'razorpay_order_id', 'razorpay_payment_status', 
                 'razorpay_payment_id', 'paid']
        read_only_fields = ['id', 'razorpay_order_id', 'razorpay_payment_status', 
                           'razorpay_payment_id', 'paid']

class OrderPlacedSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Nested product details
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        write_only=True
    )

    class Meta:
        model = OrderPlaced
        fields = ['id', 'user', 'customer', 'product', 'product_id', 'quantity', 'ordered_date', 'status', 'payment', 'total_cost']
        read_only_fields = ['id', 'user', 'ordered_date', 'status', 'total_cost']  # User should be auto-assigned

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'product']
        read_only_fields = ['id']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")  # Show username instead of user ID
    formatted_review = serializers.ReadOnlyField()  # Read-only property from the model

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'review_text', 'created_at', 'formatted_review']
        read_only_fields = ['id', 'user', 'created_at']

