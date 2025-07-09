from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

# Algerian Wilayas choices
WILAYA_CHOICES = [
    ('01', 'Adrar'), ('02', 'Chlef'), ('03', 'Laghouat'), ('04', 'Oum El Bouaghi'),
    ('05', 'Batna'), ('06', 'Béjaïa'), ('07', 'Biskra'), ('08', 'Béchar'),
    ('09', 'Blida'), ('10', 'Bouira'), ('11', 'Tamanrasset'), ('12', 'Tébessa'),
    ('13', 'Tlemcen'), ('14', 'Tiaret'), ('15', 'Tizi Ouzou'), ('16', 'Alger'),
    ('17', 'Djelfa'), ('18', 'Jijel'), ('19', 'Sétif'), ('20', 'Saïda'),
    ('21', 'Skikda'), ('22', 'Sidi Bel Abbès'), ('23', 'Annaba'), ('24', 'Guelma'),
    ('25', 'Constantine'), ('26', 'Médéa'), ('27', 'Mostaganem'), ('28', "M'Sila"),
    ('29', 'Mascara'), ('30', 'Ouargla'), ('31', 'Oran'), ('32', 'El Bayadh'),
    ('33', 'Illizi'), ('34', 'Bordj Bou Arréridj'), ('35', 'Boumerdès'), ('36', 'El Tarf'),
    ('37', 'Tindouf'), ('38', 'Tissemsilt'), ('39', 'El Oued'), ('40', 'Khenchela'),
    ('41', 'Souk Ahras'), ('42', 'Tipaza'), ('43', 'Mila'), ('44', 'Aïn Defla'),
    ('45', 'Naâma'), ('46', 'Aïn Témouchent'), ('47', 'Ghardaïa'), ('48', 'Relizane'),
    ('49', "El M'Ghair"), ('50', 'El Meniaa'), ('51', 'Ouled Djellal'), ('52', 'Bordj Baji Mokhtar'),
    ('53', 'Béni Abbès'), ('54', 'Timimoun'), ('55', 'Touggourt'), ('56', 'Djanet'),
    ('57', "Aïn Salah"), ('58', 'Aïn Guezzam'),
]

# Book Category Choices
BOOK_CATEGORY_CHOICES = [
    ('روايات', 'روايات'),
    ('تاريخ', 'تاريخ'),
    ('علوم', 'علوم'),
    ('فلسفة', 'فلسفة'),
    ('أدب', 'أدب'),
    ('دين', 'دين'),
]

# Order Status Choices
ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
]

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        username = extra_fields.get('username')
        if not username:
            username = email
        extra_fields['username'] = username
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Custom User model for Zajil bookstore"""
    full_name = models.CharField(max_length=255)
    wilaya = models.CharField(max_length=2, choices=WILAYA_CHOICES)
    address = models.TextField()
    postal_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)
    last_profile_update = models.DateTimeField(auto_now_add=True)
    
    # Override username to use email
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'wilaya', 'address', 'postal_code', 'phone_number']

    objects = UserManager()
    
    def __str__(self):
        return self.full_name
    
    def can_update_profile(self):
        """Check if user can update profile (once per week)"""
        from django.utils import timezone
        from datetime import timedelta
        return (timezone.now() - self.last_profile_update) > timedelta(days=7)

class Author(models.Model):
    """Author model for books"""
    name = models.CharField(max_length=255)
    biography = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Book(models.Model):
    """Book model for the bookstore"""
    name = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    publishing_date = models.DateField()
    category = models.CharField(max_length=50, choices=BOOK_CATEGORY_CHOICES, default='روايات')
    available = models.BooleanField(default=True)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} by {self.author.name}"
    
    class Meta:
        ordering = ['-created_at']

class Order(models.Model):
    """Order model for customer orders"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    wilaya = models.CharField(max_length=2, choices=WILAYA_CHOICES)
    postal_code = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.full_name}"
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    """OrderItem model for individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        # Calculate subtotal automatically
        from decimal import Decimal
        self.subtotal = Decimal(int(self.quantity)) * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity}x {self.book.name} in Order {self.order.pk}"
    
    class Meta:
        unique_together = ['order', 'book']
