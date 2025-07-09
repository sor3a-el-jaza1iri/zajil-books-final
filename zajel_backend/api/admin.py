from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, Author, Book, Order, OrderItem, WILAYA_CHOICES, ORDER_STATUS_CHOICES

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""
    list_display = ['email', 'full_name', 'wilaya', 'phone_number', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'wilaya', 'date_joined']
    search_fields = ['email', 'full_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'wilaya', 'address', 'postal_code', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_profile_update')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'wilaya', 'address', 'postal_code', 'phone_number', 'password1', 'password2'),
        }),
    )

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin for Author model"""
    list_display = ['name', 'book_count']
    search_fields = ['name']
    ordering = ['name']
    
    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = 'Number of Books'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin for Book model"""
    list_display = ['name', 'author', 'publisher', 'price', 'stock', 'available', 'cover_preview']
    list_filter = ['available', 'publishing_date', 'author', 'publisher']
    search_fields = ['name', 'author__name', 'publisher']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'author', 'publisher', 'description')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'available', 'stock')
        }),
        ('Media', {
            'fields': ('cover_image', 'cover_preview')
        }),
        ('Dates', {
            'fields': ('publishing_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.cover_image.url)
        return "No cover"
    cover_preview.short_description = 'Cover Preview'

class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem"""
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['book', 'quantity', 'unit_price', 'subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model"""
    list_display = ['id', 'full_name', 'email', 'wilaya', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'wilaya', 'created_at']
    search_fields = ['id', 'full_name', 'email', 'phone_number']
    ordering = ['-created_at']
    readonly_fields = ['id', 'total_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'status', 'total_price')
        }),
        ('Customer Information', {
            'fields': ('full_name', 'email', 'phone_number')
        }),
        ('Shipping Information', {
            'fields': ('address', 'wilaya', 'postal_code')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items__book')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user', 'total_price')
        return self.readonly_fields

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for OrderItem model"""
    list_display = ['order', 'book', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['order__id', 'book__name']
    ordering = ['-order__created_at']
    readonly_fields = ['subtotal']

# Customize admin site
admin.site.site_header = "Zajil Books Admin"
admin.site.site_title = "Zajil Books Admin Portal"
admin.site.index_title = "Welcome to Zajil Books Administration"
