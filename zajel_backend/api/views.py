from django.shortcuts import render
from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from decimal import Decimal

from .models import User, Author, Book, Order, OrderItem, WILAYA_CHOICES, ORDER_STATUS_CHOICES
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    ChangePasswordSerializer, AuthorSerializer, BookSerializer, BookListSerializer,
    OrderSerializer, OrderCreateSerializer, CartItemSerializer, CartSerializer,
    SearchSerializer, OrderItemSerializer
)

# Authentication Views
class UserRegistrationView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User registered successfully',
                'token': token.key,
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """User login endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'token': token.key,
                'user': UserProfileSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logout(request)
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})

# User Profile Views
class UserProfileView(APIView):
    """User profile management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    """Change password endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    """Delete account endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'Account deleted successfully'})

# Book Views
class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """Book viewset for listing and retrieving books"""
    queryset = Book.objects.filter(available=True)
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookSerializer
        return BookListSerializer
    
    def get_queryset(self):
        queryset = Book.objects.filter(available=True)
        author = self.request.query_params.get('author', None)
        category = self.request.query_params.get('category', None)
        
        if author:
            queryset = queryset.filter(author__name__icontains=author)
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset

# Search View
class SearchView(APIView):
    """Live search endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'results': []})
        
        books = Book.objects.filter(
            Q(name__icontains=query) | Q(author__name__icontains=query),
            available=True
        )[:10]  # Limit to 10 results
        
        serializer = BookListSerializer(books, many=True)
        return Response({
            'query': query,
            'results': serializer.data
        })

# Cart Views
class CartView(APIView):
    """Shopping cart management"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get current cart"""
        cart = request.session.get('cart', {})
        items = []
        total_price = Decimal('0.00')
        total_items = 0
        
        for book_id, quantity in cart.items():
            try:
                book = Book.objects.get(id=book_id, available=True)
                if book.stock >= quantity:
                    subtotal = book.price * quantity
                    items.append({
                        'book_id': book.id,
                        'quantity': quantity,
                        'book_name': book.name,
                        'book_price': book.price,
                        'book_cover': book.cover_image.url if book.cover_image else None,
                        'subtotal': subtotal,
                        'available_stock': book.stock
                    })
                    total_price += subtotal
                    total_items += quantity
                else:
                    # Remove item if insufficient stock
                    del cart[book_id]
            except Book.DoesNotExist:
                # Remove item if book doesn't exist
                del cart[book_id]
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return Response({
            'items': items,
            'total_items': total_items,
            'total_price': total_price
        })
    
    def post(self, request):
        """Add item to cart"""
        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            book = Book.objects.get(id=book_id, available=True)
            if book.stock < quantity:
                return Response(
                    {'error': f'Only {book.stock} copies available'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart = request.session.get('cart', {})
            current_quantity = cart.get(str(book_id), 0)
            new_quantity = current_quantity + quantity
            
            if new_quantity > book.stock:
                return Response(
                    {'error': f'Cannot add {quantity} more copies. Only {book.stock - current_quantity} available'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart[str(book_id)] = new_quantity
            request.session['cart'] = cart
            request.session.modified = True
            
            return Response({'message': 'Item added to cart'})
            
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        """Update cart item quantity"""
        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            book = Book.objects.get(id=book_id, available=True)
            if quantity > book.stock:
                return Response(
                    {'error': f'Only {book.stock} copies available'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart = request.session.get('cart', {})
            if quantity <= 0:
                cart.pop(str(book_id), None)
            else:
                cart[str(book_id)] = quantity
            
            request.session['cart'] = cart
            request.session.modified = True
            
            return Response({'message': 'Cart updated'})
            
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request):
        """Remove item from cart or clear cart"""
        book_id = request.data.get('book_id')
        cart = request.session.get('cart', {})
        
        if book_id:
            # Remove specific item
            cart.pop(str(book_id), None)
        else:
            # Clear entire cart
            cart.clear()
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return Response({'message': 'Item removed from cart'})

# Checkout View
class CheckoutView(APIView):
    """Checkout endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare order data
        order_data = {
            'full_name': request.data.get('full_name'),
            'email': request.data.get('email'),
            'phone_number': request.data.get('phone_number'),
            'address': request.data.get('address'),
            'wilaya': request.data.get('wilaya'),
            'postal_code': request.data.get('postal_code'),
            'items': []
        }
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone_number', 'address', 'wilaya', 'postal_code']
        for field in required_fields:
            if not order_data[field]:
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare items data
        for book_id, quantity in cart.items():
            try:
                book = Book.objects.get(id=book_id, available=True)
                if book.stock < quantity:
                    return Response(
                        {'error': f'Insufficient stock for {book.name}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                order_data['items'].append({
                    'book_id': book.id,
                    'quantity': quantity,
                    'unit_price': book.price
                })
            except Book.DoesNotExist:
                return Response({'error': f'Book with id {book_id} not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create order
        serializer = OrderCreateSerializer(data=order_data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            
            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True
            
            # Send confirmation email
            self.send_order_confirmation_email(order)
            
            return Response({
                'message': 'Order created successfully',
                'order_id': order.id,
                'order': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_order_confirmation_email(self, order):
        """Send order confirmation email"""
        subject = f'Order Confirmation - {order.id}'
        message = f"""
        New order received:
        
        Order ID: {order.id}
        Customer: {order.full_name}
        Email: {order.email}
        Phone: {order.phone_number}
        Address: {order.address}
        Wilaya: {order.get_wilaya_display()}
        Postal Code: {order.postal_code}
        Total: ${order.total_price}
        
        Items:
        """
        
        for item in order.items.all():
            message += f"- {item.book.name} x{item.quantity} = ${item.subtotal}\n"
        
        # Send to admin
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True
        )
        
        # Send to customer if logged in
        if order.user:
            customer_message = f"""
            Thank you for your order!
            
            Order ID: {order.id}
            Total: ${order.total_price}
            
            We will process your order and contact you soon.
            """
            
            send_mail(
                'Order Confirmation - Zajil Books',
                customer_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.email],
                fail_silently=True
            )

# Order Views
class OrderListView(APIView):
    """List user orders"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderDetailView(APIView):
    """Get order details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# Utility Views
class WilayaListView(APIView):
    """Get list of Algerian wilayas"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response(WILAYA_CHOICES)

class CategoriesListView(APIView):
    """Get list of book categories"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        from .models import BOOK_CATEGORY_CHOICES
        return Response(BOOK_CATEGORY_CHOICES)

class OrderStatusListView(APIView):
    """Get list of order statuses"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response(ORDER_STATUS_CHOICES)

# Admin Views (for managing orders)
class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin viewset for managing orders"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = Order.objects.all()
        status_filter = self.request.query_params.get('status', None)
        wilaya_filter = self.request.query_params.get('wilaya', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if wilaya_filter:
            queryset = queryset.filter(wilaya=wilaya_filter)
        
        return queryset

# Legacy view for compatibility
@api_view(['GET'])
def get_example_data(request):
    data = {
        'message': 'Hello from Django!',
        'status': 'success'
    }
    return Response(data)

def main(request):
    return HttpResponse("hello world")