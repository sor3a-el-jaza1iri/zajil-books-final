from django.core.management.base import BaseCommand
from api.models import Book, User, Order, OrderItem
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add test items to cart for testing'

    def handle(self, *args, **options):
        self.stdout.write('Adding test items to cart...')
        
        # Get the first book
        try:
            book = Book.objects.first()
            if not book:
                self.stdout.write(self.style.ERROR('No books found. Please run create_test_data first.'))
                return
            
            self.stdout.write(f'Found book: {book.name}')
            
            # Create a test user if none exists
            user, created = User.objects.get_or_create(
                email='test@example.com',
                defaults={
                    'username': 'testuser',
                    'full_name': 'Test User',
                    'wilaya': '16',  # Algiers
                    'address': '123 Test Street',
                    'postal_code': '16000',
                    'phone_number': '0123456789',
                }
            )
            
            if created:
                self.stdout.write(f'Created test user: {user.full_name}')
            else:
                self.stdout.write(f'Using existing user: {user.full_name}')
            
            # Create a test order (cart) for the user
            order, created = Order.objects.get_or_create(
                user=user,
                status='pending',
                defaults={
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'address': user.address,
                    'wilaya': user.wilaya,
                    'postal_code': user.postal_code,
                    'total_price': Decimal('0.00'),
                }
            )
            
            if created:
                self.stdout.write(f'Created test order: {order.id}')
            else:
                self.stdout.write(f'Using existing order: {order.id}')
            
            # Add some items to the cart
            items_to_add = [
                {'book': book, 'quantity': 2, 'unit_price': book.price},
            ]
            
            # Add a second book if available
            second_book = Book.objects.filter(id__gt=book.id).first()
            if second_book:
                items_to_add.append({
                    'book': second_book, 
                    'quantity': 1, 
                    'unit_price': second_book.price
                })
            
            total_price = Decimal('0.00')
            
            for item_data in items_to_add:
                book_obj = item_data['book']
                quantity = item_data['quantity']
                unit_price = item_data['unit_price']
                subtotal = quantity * unit_price
                total_price += subtotal
                
                order_item, created = OrderItem.objects.get_or_create(
                    order=order,
                    book=book_obj,
                    defaults={
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'subtotal': subtotal,
                    }
                )
                
                if created:
                    self.stdout.write(f'Added {quantity}x {book_obj.name} to cart')
                else:
                    # Update existing item
                    order_item.quantity = quantity
                    order_item.unit_price = unit_price
                    order_item.subtotal = subtotal
                    order_item.save()
                    self.stdout.write(f'Updated {quantity}x {book_obj.name} in cart')
            
            # Update order total
            order.total_price = total_price
            order.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully added {len(items_to_add)} items to cart. Total: {total_price} دج'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}')) 