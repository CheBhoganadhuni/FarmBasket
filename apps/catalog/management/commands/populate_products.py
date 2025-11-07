from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Category, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with sample products'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🌱 Starting to populate products...'))
        
        # Clear existing data (optional - comment out if you want to keep existing)
        self.stdout.write('Clearing existing products...')
        Product.objects.all().delete()
        Category.objects.all().delete()
        
        # Create Categories
        categories_data = [
            {
                'name': 'Fruits',
                'icon': '🍎',
                'description': 'Fresh, organic fruits handpicked from local farms',
                'display_order': 1
            },
            {
                'name': 'Vegetables',
                'icon': '🥬',
                'description': 'Farm-fresh vegetables, grown without pesticides',
                'display_order': 2
            },
            {
                'name': 'Dairy',
                'icon': '🥛',
                'description': 'Pure, organic dairy products from healthy farms',
                'display_order': 3
            },
            {
                'name': 'Pantry',
                'icon': '🌾',
                'description': 'Organic grains, pulses, and pantry essentials',
                'display_order': 4
            },
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = Category.objects.create(**cat_data)
            categories[category.name] = category
            self.stdout.write(f'  ✅ Created category: {category}')
        
        # Create Products
        products_data = [
            # FRUITS
            {
                'category': categories['Fruits'],
                'name': 'Organic Apples',
                'description': 'Crisp and juicy organic apples from Himachal Pradesh. Rich in fiber and antioxidants. Perfect for snacking or baking.',
                'farm_story': '🍎 These apples come from the orchards of Sharma Family Farm in Shimla. The farm has been using organic farming methods for over 20 years, ensuring the healthiest and tastiest apples you can find.',
                'price': Decimal('120.00'),
                'discount_price': Decimal('99.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 50,
                'is_featured': True,
                'is_organic_certified': True,
            },
            {
                'category': categories['Fruits'],
                'name': 'Fresh Bananas',
                'description': 'Sweet and creamy bananas, perfect for smoothies, breakfast, or snacking. Rich in potassium and natural energy.',
                'farm_story': '🍌 Sourced from organic farms in Kerala, these bananas are grown naturally without any chemical ripening agents.',
                'price': Decimal('60.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 100,
                'is_featured': True,
            },
            {
                'category': categories['Fruits'],
                'name': 'Organic Mangoes',
                'description': 'Sweet, juicy Alphonso mangoes - the king of fruits! Perfectly ripe and bursting with flavor.',
                'farm_story': '🥭 Our mangoes are grown in Ratnagiri by farmers who have perfected the art of growing this premium variety over generations.',
                'price': Decimal('250.00'),
                'discount_price': Decimal('199.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 30,
                'is_featured': True,
            },
            {
                'category': categories['Fruits'],
                'name': 'Fresh Oranges',
                'description': 'Juicy, vitamin C-rich oranges perfect for fresh juice or eating. Sweet and tangy flavor.',
                'price': Decimal('80.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 60,
            },
            {
                'category': categories['Fruits'],
                'name': 'Organic Grapes',
                'description': 'Seedless green grapes, sweet and crunchy. Perfect for kids and wine lovers alike!',
                'price': Decimal('150.00'),
                'discount_price': Decimal('120.00'),
                'unit': 'KG',
                'unit_value': Decimal('0.5'),
                'stock_quantity': 25,
            },
            
            # VEGETABLES
            {
                'category': categories['Vegetables'],
                'name': 'Organic Tomatoes',
                'description': 'Vine-ripened organic tomatoes, perfect for salads, cooking, or making fresh tomato sauce.',
                'farm_story': '🍅 Grown in the fertile fields of Punjab by the Kumar family, who use traditional organic farming methods passed down for three generations.',
                'price': Decimal('40.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 80,
                'is_featured': True,
            },
            {
                'category': categories['Vegetables'],
                'name': 'Fresh Spinach',
                'description': 'Dark green, nutrient-rich spinach leaves. Perfect for salads, smoothies, or cooking.',
                'farm_story': '🥬 Harvested fresh every morning from local farms around Delhi NCR.',
                'price': Decimal('30.00'),
                'unit': 'BUNCH',
                'unit_value': Decimal('1'),
                'stock_quantity': 50,
            },
            {
                'category': categories['Vegetables'],
                'name': 'Organic Carrots',
                'description': 'Sweet, crunchy organic carrots loaded with beta-carotene. Great for salads, juices, or cooking.',
                'price': Decimal('50.00'),
                'discount_price': Decimal('40.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 70,
                'is_featured': True,
            },
            {
                'category': categories['Vegetables'],
                'name': 'Fresh Potatoes',
                'description': 'Premium quality potatoes, perfect for curries, fries, or any dish you love.',
                'price': Decimal('35.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 120,
            },
            {
                'category': categories['Vegetables'],
                'name': 'Organic Broccoli',
                'description': 'Fresh, green broccoli florets packed with vitamins and minerals. A superfood for your table.',
                'price': Decimal('80.00'),
                'unit': 'PC',
                'unit_value': Decimal('1'),
                'stock_quantity': 40,
            },
            {
                'category': categories['Vegetables'],
                'name': 'Bell Peppers Mix',
                'description': 'Colorful mix of red, yellow, and green bell peppers. Crispy and sweet!',
                'price': Decimal('120.00'),
                'discount_price': Decimal('100.00'),
                'unit': 'KG',
                'unit_value': Decimal('0.5'),
                'stock_quantity': 35,
            },
            
            # DAIRY
            {
                'category': categories['Dairy'],
                'name': 'Organic Full Cream Milk',
                'description': 'Fresh, pure organic milk from grass-fed cows. No hormones, no antibiotics. Just pure goodness.',
                'farm_story': '🥛 Our milk comes from Gir cows at the Organic Dairy Farm in Gujarat, where cows are treated with love and care.',
                'price': Decimal('70.00'),
                'unit': 'L',
                'unit_value': Decimal('1'),
                'stock_quantity': 60,
                'is_featured': True,
            },
            {
                'category': categories['Dairy'],
                'name': 'Organic Yogurt',
                'description': 'Creamy, probiotic-rich organic yogurt. Made with live cultures for gut health.',
                'price': Decimal('60.00'),
                'unit': 'G',
                'unit_value': Decimal('500'),
                'stock_quantity': 45,
            },
            {
                'category': categories['Dairy'],
                'name': 'Farm Fresh Butter',
                'description': 'Rich, creamy butter made from organic cream. Perfect for spreading or cooking.',
                'price': Decimal('120.00'),
                'discount_price': Decimal('99.00'),
                'unit': 'G',
                'unit_value': Decimal('250'),
                'stock_quantity': 30,
            },
            {
                'category': categories['Dairy'],
                'name': 'Organic Paneer',
                'description': 'Soft, fresh cottage cheese made from organic milk. High in protein and delicious!',
                'price': Decimal('150.00'),
                'unit': 'G',
                'unit_value': Decimal('250'),
                'stock_quantity': 25,
                'is_featured': True,
            },
            
            # PANTRY
            {
                'category': categories['Pantry'],
                'name': 'Organic Basmati Rice',
                'description': 'Premium aged basmati rice with extra-long grains. Perfect for biryanis and pulaos.',
                'farm_story': '🌾 Grown in the fields of Dehradun, this basmati rice is aged naturally for over a year to develop its unique aroma and flavor.',
                'price': Decimal('180.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 100,
                'is_featured': True,
            },
            {
                'category': categories['Pantry'],
                'name': 'Organic Whole Wheat Flour',
                'description': 'Stone-ground whole wheat flour, perfect for making rotis, parathas, and bread.',
                'price': Decimal('60.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 80,
            },
            {
                'category': categories['Pantry'],
                'name': 'Organic Toor Dal',
                'description': 'Premium quality split pigeon peas. A staple for Indian dal recipes.',
                'price': Decimal('120.00'),
                'discount_price': Decimal('99.00'),
                'unit': 'KG',
                'unit_value': Decimal('1'),
                'stock_quantity': 70,
            },
            {
                'category': categories['Pantry'],
                'name': 'Organic Honey',
                'description': 'Raw, unprocessed honey from Himalayan wildflowers. Rich in antioxidants and natural enzymes.',
                'farm_story': '🍯 Collected by local beekeepers in Uttarakhand who practice sustainable beekeeping.',
                'price': Decimal('350.00'),
                'discount_price': Decimal('299.00'),
                'unit': 'G',
                'unit_value': Decimal('500'),
                'stock_quantity': 40,
                'is_featured': True,
            },
            {
                'category': categories['Pantry'],
                'name': 'Organic Quinoa',
                'description': 'Protein-rich superfood grain. Perfect for salads, bowls, or as a rice substitute.',
                'price': Decimal('280.00'),
                'unit': 'G',
                'unit_value': Decimal('500'),
                'stock_quantity': 30,
            },
        ]
        
        for product_data in products_data:
            product = Product.objects.create(**product_data)
            self.stdout.write(f'  ✅ Created product: {product}')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Successfully created {len(categories_data)} categories and {len(products_data)} products!'))
        self.stdout.write(self.style.SUCCESS('✨ Your catalog is ready!'))
