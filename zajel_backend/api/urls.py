from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'books', views.BookViewSet, basename='book')
router.register(r'admin/orders', views.AdminOrderViewSet, basename='admin-order')

# URL patterns
urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='user-logout'),
    
    # User profile endpoints
    path('account/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('account/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('account/delete/', views.DeleteAccountView.as_view(), name='delete-account'),
    
    # Book and search endpoints
    path('', include(router.urls)),  # Includes /books/ and /admin/orders/
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Cart endpoints
    path('cart/', views.CartView.as_view(), name='cart'),
    
    # Checkout endpoint
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    
    # Order endpoints
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<uuid:order_id>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Utility endpoints
    path('wilayas/', views.WilayaListView.as_view(), name='wilaya-list'),
    path('categories/', views.CategoriesListView.as_view(), name='categories-list'),
    path('order-statuses/', views.OrderStatusListView.as_view(), name='order-status-list'),
    
    # Legacy endpoint for compatibility
    path('example/', views.get_example_data, name='example'),
]