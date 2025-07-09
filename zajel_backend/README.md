# Zajil Books - Django Backend

A comprehensive Django REST Framework backend for the Zajil online bookstore, featuring user authentication, book management, shopping cart, order processing, and admin functionality.

## Features

- **User Management**: Custom user model with profile management
- **Book Catalog**: Complete book management with authors and inventory
- **Shopping Cart**: Session-based cart with real-time updates
- **Order Processing**: Complete order lifecycle with email notifications
- **Search**: Live search functionality for books and authors
- **Admin Interface**: Comprehensive admin panel for all operations
- **API**: RESTful API endpoints for frontend integration

## Tech Stack

- Django 5.2.4
- Django REST Framework 3.14.0
- PostgreSQL (database)
- Django CORS Headers
- Pillow (image processing)

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- Virtual environment

### Installation

1. **Clone the repository and navigate to the backend directory:**
   ```bash
   cd zajel_backend
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   ..\venv\Scripts\activate
   
   # macOS/Linux
   source ../venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**
   ```sql
   CREATE DATABASE zajil_db;
   CREATE USER postgres WITH PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE zajil_db TO postgres;
   ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### User Profile
- `GET /api/account/profile/` - Get user profile
- `PUT /api/account/profile/` - Update user profile
- `POST /api/account/change-password/` - Change password
- `DELETE /api/account/delete/` - Delete account

### Books
- `GET /api/books/` - List all books
- `GET /api/books/{id}/` - Get book details
- `GET /api/books/?author=author_name` - Filter by author

### Search
- `GET /api/search/?q=query` - Search books and authors

### Cart
- `GET /api/cart/` - Get cart contents
- `POST /api/cart/` - Add item to cart
- `PUT /api/cart/` - Update cart item
- `DELETE /api/cart/` - Remove item from cart

### Checkout
- `POST /api/checkout/` - Create order from cart

### Orders
- `GET /api/orders/` - List user orders
- `GET /api/orders/{id}/` - Get order details

### Utilities
- `GET /api/wilayas/` - List Algerian wilayas
- `GET /api/order-statuses/` - List order statuses

### Admin (Admin users only)
- `GET /api/admin/orders/` - List all orders
- `GET /api/admin/orders/?status=pending` - Filter orders by status
- `GET /api/admin/orders/?wilaya=16` - Filter orders by wilaya

## API Usage Examples

### User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "full_name": "John Doe",
    "wilaya": "16",
    "address": "123 Main St",
    "postal_code": "16000",
    "phone_number": "+213123456789",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

### User Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Add Item to Cart
```bash
curl -X POST http://localhost:8000/api/cart/ \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "quantity": 2
  }'
```

### Search Books
```bash
curl "http://localhost:8000/api/search/?q=harry+potter"
```

### Create Order
```bash
curl -X POST http://localhost:8000/api/checkout/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+213123456789",
    "address": "123 Main St",
    "wilaya": "16",
    "postal_code": "16000"
  }'
```

## Admin Interface

Access the admin interface at `http://localhost:8000/admin/`

### Admin Features
- **User Management**: View and manage all users
- **Book Management**: Add, edit, and manage books and authors
- **Order Management**: View all orders with filtering options
- **Inventory Management**: Update book stock and availability

## Environment Variables

Create a `.env` file in the project root for production settings:

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/zajil_db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_EMAIL=admin@zajil.com
```

## Database Schema

### User Model
- Custom user model extending AbstractUser
- Email-based authentication
- Profile fields: full_name, wilaya, address, postal_code, phone_number
- Profile update restriction (once per week)

### Book Model
- Book information with cover images
- Author relationship
- Inventory management (stock, availability)
- Pricing and publishing details

### Order Model
- UUID-based order identification
- Customer information (guest and authenticated users)
- Order status tracking
- Total price calculation

### OrderItem Model
- Individual items in orders
- Quantity and pricing information
- Automatic subtotal calculation

## Security Features

- Custom user model with email authentication
- Password validation and change requirements
- CORS configuration for frontend integration
- Session-based cart management
- Admin-only endpoints for sensitive operations

## Email Notifications

The system sends email notifications for:
- Order confirmations to customers (if logged in)
- Order notifications to admin
- Password reset functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 