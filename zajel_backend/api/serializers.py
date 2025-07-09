from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User, Author, Book, Order, OrderItem, WILAYA_CHOICES, ORDER_STATUS_CHOICES

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'wilaya', 'address', 'postal_code', 'phone_number', 'password', 'password_confirm']
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'wilaya', 'address', 'postal_code', 'phone_number', 'last_profile_update']
        read_only_fields = ['id', 'email', 'last_profile_update']
    
    def validate(self, attrs):
        user = self.instance
        if not user.can_update_profile():
            raise serializers.ValidationError("Profile can only be updated once per week")
        return attrs
    
    def update(self, instance, validated_data):
        instance.last_profile_update = timezone.now()
        return super().update(instance, validated_data)

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author model"""
    class Meta:
        model = Author
        fields = ['id', 'name', 'biography']

class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model"""
    author = AuthorSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'name', 'cover_image', 'description', 'author', 'author_id', 
                 'publisher', 'price', 'publishing_date', 'category', 'available', 'stock', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class BookListSerializer(serializers.ModelSerializer):
    """Simplified serializer for book listing"""
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'name', 'cover_image', 'author', 'publisher', 'price', 'category', 'available', 'stock']

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    book = BookListSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'book_id', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['unit_price', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserProfileSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    wilaya_display = serializers.CharField(source='get_wilaya_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'full_name', 'email', 'phone_number', 'address', 
                 'wilaya', 'wilaya_display', 'postal_code', 'status', 'status_display', 
                 'total_price', 'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone_number', 'address', 'wilaya', 
                 'postal_code', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        
        # Calculate total price
        total_price = sum(item['quantity'] * item['unit_price'] for item in items_data)
        
        # Create order
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            **validated_data
        )
        
        # Create order items and update book stock
        for item_data in items_data:
            book = Book.objects.get(id=item_data['book_id'])
            if book.stock < item_data['quantity']:
                raise serializers.ValidationError(f"Insufficient stock for {book.name}")
            
            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            
            # Update book stock
            book.stock -= item_data['quantity']
            book.save()
        
        return order

class CartItemSerializer(serializers.Serializer):
    """Serializer for cart items"""
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    book_name = serializers.CharField(read_only=True)
    book_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    book_cover = serializers.CharField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    available_stock = serializers.IntegerField(read_only=True)

class CartSerializer(serializers.Serializer):
    """Serializer for shopping cart"""
    items = CartItemSerializer(many=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

class SearchSerializer(serializers.Serializer):
    """Serializer for search functionality"""
    query = serializers.CharField(max_length=255)
    results = BookListSerializer(many=True, read_only=True)
        