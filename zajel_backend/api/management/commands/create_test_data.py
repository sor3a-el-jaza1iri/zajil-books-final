from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Author, Book
from decimal import Decimal
from datetime import date

class Command(BaseCommand):
    help = 'Create test data for books and authors'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create authors
        authors_data = [
            {
                'name': 'نجيب محفوظ',
                'biography': 'كاتب مصري حائز على جائزة نوبل في الأدب عام 1988. من أشهر أعماله الثلاثية والحرافيش.'
            },
            {
                'name': 'طه حسين',
                'biography': 'كاتب ومفكر مصري، لقب بعميد الأدب العربي. من أشهر أعماله الأيام.'
            },
            {
                'name': 'أحمد شوقي',
                'biography': 'شاعر مصري، لقب بأمير الشعراء. من أشهر أعماله الشوقيات.'
            },
            {
                'name': 'إبراهيم الكوني',
                'biography': 'كاتب ليبي، من أشهر كتاب الرواية العربية المعاصرة. من أشهر أعماله التبر.'
            },
            {
                'name': 'أحمد خالد توفيق',
                'biography': 'كاتب مصري، من أشهر كتاب الرعب والخيال العلمي في العالم العربي.'
            },
            {
                'name': 'محمد بن عبد الوهاب',
                'biography': 'مصلح ديني سعودي، مؤسس الحركة الوهابية.'
            },
            {
                'name': 'ابن خلدون',
                'biography': 'مؤرخ وعالم اجتماع عربي، من أشهر أعماله مقدمة ابن خلدون.'
            },
            {
                'name': 'ابن سينا',
                'biography': 'طبيب وفيلسوف وعالم مسلم، من أشهر أعماله القانون في الطب.'
            }
        ]
        
        authors = []
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                name=author_data['name'],
                defaults={'biography': author_data['biography']}
            )
            authors.append(author)
            if created:
                self.stdout.write(f'Created author: {author.name}')
            else:
                self.stdout.write(f'Author already exists: {author.name}')
        
        # Create books
        books_data = [
            {
                'name': 'الحرافيش',
                'author': authors[0],  # نجيب محفوظ
                'description': 'رواية من أشهر أعمال نجيب محفوظ، تتناول قصة عائلة مصرية عبر ثلاثة أجيال.',
                'publisher': 'دار الشروق',
                'price': Decimal('45.00'),
                'publishing_date': date(1977, 1, 1),
                'category': 'روايات',
                'stock': 15
            },
            {
                'name': 'الأيام',
                'author': authors[1],  # طه حسين
                'description': 'سيرة ذاتية للكاتب طه حسين، تتناول حياته منذ الطفولة حتى الشباب.',
                'publisher': 'دار المعارف',
                'price': Decimal('35.00'),
                'publishing_date': date(1929, 1, 1),
                'category': 'أدب',
                'stock': 20
            },
            {
                'name': 'الشوقيات',
                'author': authors[2],  # أحمد شوقي
                'description': 'ديوان شعر من أشهر أعمال أمير الشعراء أحمد شوقي.',
                'publisher': 'دار الكتب المصرية',
                'price': Decimal('40.00'),
                'publishing_date': date(1898, 1, 1),
                'category': 'أدب',
                'stock': 12
            },
            {
                'name': 'التبر',
                'author': authors[3],  # إبراهيم الكوني
                'description': 'رواية تتناول قصة البحث عن الذهب في الصحراء الليبية.',
                'publisher': 'دار الآداب',
                'price': Decimal('50.00'),
                'publishing_date': date(1990, 1, 1),
                'category': 'روايات',
                'stock': 8
            },
            {
                'name': 'يوتوبيا',
                'author': authors[4],  # أحمد خالد توفيق
                'description': 'رواية خيال علمي تتناول مستقبل مصر في عام 2023.',
                'publisher': 'دار الشروق',
                'price': Decimal('30.00'),
                'publishing_date': date(2008, 1, 1),
                'category': 'روايات',
                'stock': 25
            },
            {
                'name': 'كتاب التوحيد',
                'author': authors[5],  # محمد بن عبد الوهاب
                'description': 'كتاب في العقيدة الإسلامية يتناول موضوع التوحيد.',
                'publisher': 'دار السلام',
                'price': Decimal('25.00'),
                'publishing_date': date(1750, 1, 1),
                'category': 'دين',
                'stock': 30
            },
            {
                'name': 'مقدمة ابن خلدون',
                'author': authors[6],  # ابن خلدون
                'description': 'مقدمة في فلسفة التاريخ وعلم الاجتماع.',
                'publisher': 'دار الكتب العلمية',
                'price': Decimal('60.00'),
                'publishing_date': date(1377, 1, 1),
                'category': 'فلسفة',
                'stock': 10
            },
            {
                'name': 'القانون في الطب',
                'author': authors[7],  # ابن سينا
                'description': 'موسوعة طبية شاملة من أشهر أعمال ابن سينا.',
                'publisher': 'دار المعارف',
                'price': Decimal('80.00'),
                'publishing_date': date(1025, 1, 1),
                'category': 'علوم',
                'stock': 5
            },
            {
                'name': 'تاريخ الطبري',
                'author': authors[6],  # ابن خلدون
                'description': 'تاريخ الأمم والملوك من أشهر كتب التاريخ الإسلامي.',
                'publisher': 'دار الكتب العلمية',
                'price': Decimal('70.00'),
                'publishing_date': date(915, 1, 1),
                'category': 'تاريخ',
                'stock': 7
            },
            {
                'name': 'المنقذ من الضلال',
                'author': authors[7],  # ابن سينا
                'description': 'كتاب في الفلسفة والمنطق من أشهر أعمال ابن سينا.',
                'publisher': 'دار المعارف',
                'price': Decimal('45.00'),
                'publishing_date': date(1100, 1, 1),
                'category': 'فلسفة',
                'stock': 15
            },
            {
                'name': 'فتح الباري',
                'author': authors[5],  # محمد بن عبد الوهاب
                'description': 'شرح صحيح البخاري من أشهر شروح الحديث النبوي.',
                'publisher': 'دار السلام',
                'price': Decimal('120.00'),
                'publishing_date': date(1400, 1, 1),
                'category': 'دين',
                'stock': 3
            },
            {
                'name': 'تاريخ مصر الحديث',
                'author': authors[1],  # طه حسين
                'description': 'كتاب في تاريخ مصر الحديث من عهد محمد علي حتى الثورة.',
                'publisher': 'دار المعارف',
                'price': Decimal('55.00'),
                'publishing_date': date(1950, 1, 1),
                'category': 'تاريخ',
                'stock': 18
            }
        ]
        
        for book_data in books_data:
            book, created = Book.objects.get_or_create(
                name=book_data['name'],
                author=book_data['author'],
                defaults={
                    'description': book_data['description'],
                    'publisher': book_data['publisher'],
                    'price': book_data['price'],
                    'publishing_date': book_data['publishing_date'],
                    'category': book_data['category'],
                    'stock': book_data['stock'],
                    'available': True
                }
            )
            if created:
                self.stdout.write(f'Created book: {book.name} by {book.author.name}')
            else:
                self.stdout.write(f'Book already exists: {book.name} by {book.author.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(authors)} authors and {len(books_data)} books!'
            )
        ) 