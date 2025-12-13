from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Product
from django.utils.text import slugify
from decimal import Decimal
import random
import os
from django.conf import settings
from django.core.files import File

class Command(BaseCommand):
    help = 'Seeds the database with initial products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Categories
        categories = [
            {'name': 'Vegetables', 'icon': '🥦', 'slug': 'vegetables', 'description': 'Fresh organic vegetables from local farms'},
            {'name': 'Fruits', 'icon': '🍎', 'slug': 'fruits', 'description': 'Seasonal sweet and juicy fruits'},
            {'name': 'Dairy', 'icon': '🥛', 'slug': 'dairy', 'description': 'Fresh milk, ghee, and dairy products'},
            {'name': 'Grains', 'icon': '🌾', 'slug': 'grains', 'description': 'Organic rice, wheat, and millets'},
        ]
        
        cat_objs = {}
        for cat_data in categories:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'icon': cat_data['icon'],
                    'description': cat_data['description']
                }
            )
            cat_objs[cat_data['slug']] = cat
            if created:
                self.stdout.write(f"Created category: {cat.name}")

        # Products with Rich Data
        products = [
            # Vegetables
            {
                'name': 'Organic Tomatoes',
                'category': 'vegetables',
                'price': 40,
                'unit': 'KG',
                'is_featured': True,
                'description': 'Our organic tomatoes are vine-ripened to perfection, offering a burst of tangy sweetness in every bite. Grown using sustainable farming practices, these tomatoes are free from harmful chemicals and are hand-picked at peak maturity to ensure the highest nutrient density. Perfect for fresh salads, rich curries, or homemade sauces.',
                'farm_story': 'Harvested from the sunny fields of Lakshmi Farms in Nellore. The farmers use traditional composting methods and crop rotation to enrich the soil naturally, ensuring the tomatoes are robust and flavorful.',
                'image': 'products/tomato.jpg'
            },
            {
                'name': 'Fresh Spinach',
                'category': 'vegetables',
                'price': 25,
                'unit': 'BUNCH',
                'description': 'Experience the crunch of our pesticide-free spinach. Harvested before sunrise to retain moisture and sweetness, these vibrant green leaves are a powerhouse of iron and vitamins. Ideal for wholesome smoothies, salads, or the classic Palak Paneer.',
                'farm_story': 'Grown in the hydroponic setup of GreenLeaf Urban Farms. This innovative method uses 90% less water and ensures the spinach is clean, grit-free, and protected from soil-borne diseases.',
                'image': 'products/spinach.jpg'
            },
            {
                'name': 'Red Onions',
                'category': 'vegetables',
                'price': 35,
                'unit': 'KG',
                'description': 'These pungent, flavorful red onions are a kitchen essential. With their crisp texture and deep purple layers, they add a perfect zest to any dish. Naturally cured to enhance their shelf life without artificial preservatives.',
                'farm_story': 'Sourced from the arid regions of Kurnool, where the climate is perfect for alliums. Farmers here have perfected the art of natural sun-curing to seal in the flavor.',
                'image': 'products/onion.jpg'
            },
             {
                'name': 'Organic Potatoes',
                'category': 'vegetables',
                'price': 45,
                'unit': 'KG',
                'description': 'Versatile and earthy, our organic potatoes are grown without sprout inhibitors. Whether mashed, baked, or fried, they offer a creamy texture and authentic taste that commercially grown varieties lack.',
                'farm_story': 'Cultivated in the cool, elevated terraced farms of Ooty. The unique soil composition and drainage produce potatoes that are firm, nutty, and devoid of water-logging.',
                'image': 'products/potato.jpg'
            },
            {
                'name': 'Organic Broccoli',
                'category': 'vegetables',
                'price': 80,
                'unit': 'PC',
                'description': 'Fresh, dense, and vibrant green broccoli heads rich in antioxidants. Grown in cool conditions to prevent bolting and ensure a tender stalk and tight florets.',
                'farm_story': 'Grown by the misty hills of Coorg using organic pest management. Ladybugs are introduced to naturally control aphids, keeping the crop pristine.',
                'image': 'products/broccoli.jpg'
            },
            {
                'name': 'Organic Carrots',
                'category': 'vegetables',
                'price': 50,
                'unit': 'KG',
                'description': 'Crunchy, sweet, and bright orange. Our organic carrots are harvested with their greens to prove freshness. Excellent for juicing or raw snacking.',
                'farm_story': 'From the sandy loam soils of Punjab. The loose soil allow roots to grow deep and straight, drawing up mineral-rich water.',
                'image': 'products/carrots.jpg'
            },
            {
                'name': 'Bell Peppers Mix',
                'category': 'vegetables',
                'price': 120,
                'unit': 'KG',
                'description': 'A colorful trio of Red, Yellow, and Green capsicums. Sweet, crisp, and perfect for roasting or stir-frys. Grown in protected polyhouses to ensuring blemish-free skin.',
                'farm_story': 'Cultivated in precision-climate polyhouses near Bangalore. This controlled environment reduces water usage and eliminates the need for pesticide sprays.',
                'image': 'products/bell_peppers.jpg'
            },
            
            # Fruits
            {
                'name': 'Kashmir Apples',
                'category': 'fruits',
                'price': 180,
                'unit': 'KG',
                'description': 'Crisp, juicy, and intensely aromatic. These apples are hand-picked from the high-altitude orchards of Kashmir and are never coated with wax.',
                'farm_story': 'Brought to you by the Ahmed family orchard in Sopore. They have been growing apples for four generations using traditional grafting techniques.',
                'image': 'products/apples.jpg'
            },
            {
                'name': 'Robusta Bananas',
                'category': 'fruits',
                'price': 60,
                'unit': 'DOZEN',
                'description': 'Naturally ripened Robusta bananas with a creamy texture and honey-like sweetness. Free from carbide ripening, ensuring they are safe and healthy.',
                'farm_story': 'Grown in the fertile Kaveri delta region. The rich alluvial soil gives these bananas their distinct sweetness and size.',
                'image': 'products/banana.jpg'
            },
            {
                'name': 'Alphonso Mangoes',
                'category': 'fruits',
                'price': 600,
                'unit': 'DOZEN',
                'description': 'The world-renowned Hapus (Alphonso). Known for its saffron-colored pulp, rich aroma, and buttery texture. Naturally hay-ripened.',
                'farm_story': 'Authentic Ratnagiri Alphonsos. The rocky laterite soil and sea breeze of the Konkan coast create the unique flavor profile that cannot be replicated elsewhere.',
                'image': 'products/mango.jpg'
            },
            {
                'name': 'Pomegranate',
                'category': 'fruits',
                'price': 140,
                'unit': 'KG',
                'is_featured': True,
                'description': 'Jewel-like ruby arils bursting with sweet-tart juice. A superfood loaded with antioxidants. Our pomegranates are thin-skinned and heavy with juice.',
                'farm_story': 'From the arid lands of Solapur. The stress-water irrigation technique used here concentrates the sugars in the fruit, making them intensely sweet.',
                'image': 'products/pomegranate.jpg'
            },
            {
                'name': 'Fresh Oranges',
                'category': 'fruits',
                'price': 80,
                'unit': 'KG',
                'description': 'Juicy Nagpur oranges with a perfect balance of sweet and tangy. Easy to peel and brimming with Vitamin C.',
                'farm_story': 'Sourced directly from the orange city, Nagpur. The farmers practice rain-fed agriculture which intensifies the citrus flavor.',
                'image': 'products/oranges.jpg'
            },

            # Dairy
            {
                'name': 'A2 Cow Milk',
                'category': 'dairy',
                'price': 80,
                'unit': 'L',
                'description': 'Raw, unprocessed A2 milk from free-grazing Desi cows. Creamy, easy to digest, and delivered within hours of milking.',
                'farm_story': 'Collected from a cooperative of small dairy farmers who let their Gir cows graze freely in open pastures. No hormones or antibiotics used.',
                'image': 'products/milk.jpg'
            },
            {
                'name': 'Desi Ghee',
                'category': 'dairy',
                'price': 900,
                'unit': 'L',
                'description': 'Golden, granular (Danedar) ghee made using the traditional Bilona method. Its nutty aroma and high smoke point make it perfect for Indian cooking.',
                'farm_story': 'Hand-churned from curd (not cream) by village artisans. It takes 30 liters of A2 milk to produce just 1 liter of this medicinal-grade ghee.',
                'image': 'products/ghee.jpg'
            },
            {
                'name': 'Farm Fresh Butter',
                'category': 'dairy',
                'price': 500,
                'unit': 'KG',
                'is_featured': True,
                'description': 'Unsalted, cultured white butter churned from fresh cream. Pure taste without any preservatives or added colors. Melts perfectly on hot parathas.',
                'farm_story': 'Churned daily at the Krishna Dairy farm in Gujarat. The buffaloes are fed a diet of cotton seeds and fresh grass, resulting in high-fat rich milk.',
                'image': 'products/butter.jpg'
            },
            {
                'name': 'Farm Fresh Eggs',
                'category': 'dairy',
                'price': 90,
                'unit': 'BOX', # Box of 6
                'description': 'Free-range brown eggs with varied shell colors and vibrant orange yolks. Laid by hens that forage on pasture.',
                'farm_story': 'From Happy Hens Farm given strict free-range access. Their diet of bugs, worms, and greens results in eggs rich in Omega-3.',
                'image': 'products/eggs.jpg'
            },
            
            # Grains
            {
                'name': 'Basmati Rice',
                'category': 'grains',
                'price': 120,
                'unit': 'KG',
                'description': 'Extra-long grain Basmati aged for 2 years to reduce moisture. Cooks to fluffy, non-sticky grains with a floral aroma.',
                'farm_story': 'Sourced from the foothills of the Himalayas. The glacier water irrigation imparts a unique aroma that defines true Basmati.',
                'image': 'products/rice.jpg'
            },
            {
                'name': 'Whole Wheat Atta',
                'category': 'grains',
                'price': 55,
                'unit': 'KG',
                'description': 'Traditionally stone-ground (Chakki Fresh) flour. Includes the bran and germ, ensuring your rotis are soft, nutritious, and full of fiber.',
                'farm_story': 'Grown using natural farming (ZBNF) methods in Madhya Pradesh. The Sharbati wheat variety is known for its sweet taste and softness.',
                'image': 'products/wheat.jpg'
            }
        ]
        
        for p_data in products:
            cat = cat_objs[p_data['category']]
            
            # Check if product exists
            product, created = Product.objects.get_or_create(
                name=p_data['name'],
                defaults={
                    'category': cat,
                    'slug': slugify(p_data['name']),
                    'description': p_data['description'],
                    'farm_story': p_data['farm_story'],
                    'price': Decimal(str(p_data['price'])),
                    'unit': p_data['unit'],
                    'stock_quantity': random.randint(20, 100),
                    'is_active': True,
                    'in_stock': True,
                }
            )

            # Always update fields
            if not created:
                product.category = cat
                product.description = p_data['description']
                product.farm_story = p_data['farm_story']
                product.price = Decimal(str(p_data['price']))
                product.unit = p_data['unit']
                
            # Handle is_featured manually if present in data
            if 'is_featured' in p_data:
                product.is_featured = p_data['is_featured']
            
            product.save()

            if created:
                self.stdout.write(f"Created Product: {product.name}")
            else:
                 self.stdout.write(f"Updated Product: {product.name}")
                
            # Always Attempt Image Upload (Fixes missing cloud images)
            image_rel_path = p_data['image'] # e.g. "products/tomato.jpg"
            local_image_path = os.path.join(settings.BASE_DIR, 'media', image_rel_path)
            
            if os.path.exists(local_image_path):
                # Optional: Check if we want to overwrite even if it has an image?
                # User wants to "Redo", so let's overwrite.
                try:
                    with open(local_image_path, 'rb') as f:
                        # save=True triggers Cloudinary upload
                        # Use image_rel_path to preserve folder structure (e.g. products/tomato.jpg)
                        product.featured_image.save(image_rel_path, File(f), save=True)
                    self.stdout.write(f"  -> Uploaded/Updated image for {product.name}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  -> Failed to upload image: {e}"))
            else:
                self.stdout.write(self.style.WARNING(f"  -> Source image not found at {local_image_path}"))

        self.stdout.write(self.style.SUCCESS('Successfully seeded products!'))
