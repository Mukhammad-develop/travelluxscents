from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.utils.text import slugify
from shop.models import Product, ProductVariant, BottleSize, BottleColor, Gender
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time

class Command(BaseCommand):
    help = 'Scrape and import products from swperfumeria.uk into the local database'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None, help='Limit the number of products imported')

    def handle(self, *args, **options):
        limit = options['limit']

        self.stdout.write('Clearing existing products, variants, and product images...')
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared database successfully.'))

        # Get or create default BottleColor
        transparent_color, _ = BottleColor.objects.get_or_create(
            name='Transparent',
            defaults={'hex_color': '#E8E8E8', 'order': 10}
        )

        base_url = "https://swperfumeria.uk/"
        pages = [
            "decanted-original-perfume-samples-16-c.asp",
            "decanted-original-perfume-samples-e11f4nproducts16curpage-2-16-c.asp",
            "decanted-original-perfume-samples-e11f4nproducts16curpage-3-16-c.asp",
            "decanted-original-perfume-samples-e11f4nproducts16curpage-4-16-c.asp"
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # 1. Fetch category pages and compile list of product URLs
        product_entries = []
        for idx, page in enumerate(pages, 1):
            url = base_url + page
            self.stdout.write(f"Fetching page {idx}/{len(pages)}: {url}...")
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                items = soup.find_all(class_='aerial-product-item')
                for item in items:
                    title_a = item.find(class_='product-name').find('a') if item.find(class_='product-name') else None
                    if title_a and 'href' in title_a.attrs:
                        prod_url = base_url + title_a['href']
                        prod_title = title_a.text.strip()
                        product_entries.append((prod_url, prod_title))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching page {idx}: {e}"))

        # Deduplicate URLs
        unique_products = []
        seen_urls = set()
        for u, t in product_entries:
            if u not in seen_urls:
                seen_urls.add(u)
                unique_products.append((u, t))

        total_to_import = len(unique_products)
        self.stdout.write(self.style.SUCCESS(f"Found {total_to_import} unique products to crawl."))

        if limit:
            unique_products = unique_products[:limit]
            self.stdout.write(f"Limiting import to first {len(unique_products)} products.")

        common_brands = [
            "Chanel", "Gucci", "Dior", "Tom Ford", "Creed", "Versace", "Paco Rabanne", 
            "YSL", "Yves Saint Laurent", "Lancôme", "Lancome", "Giorgio Armani", "Armani", 
            "Hugo Boss", "Jean Paul Gaultier", "Jo Malone", "Hermès", "Hermes", "Kenzo", 
            "Ralph Lauren", "Prada", "Calvin Klein", "Diesel", "Thierry Mugler", "Mugler", 
            "Maison Francis Kurkdjian", "Carolina Herrera", "Amouage", "Christian Dior"
        ]

        imported_count = 0

        # 2. Scrape each product detail page and create/merge models
        for idx, (prod_url, category_title) in enumerate(unique_products, 1):
            self.stdout.write(f"[{idx}/{len(unique_products)}] Processing: {category_title}...")
            try:
                response = requests.get(prod_url, headers=headers, timeout=15)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')

                # A. Parse LD+JSON for schemas
                brand = None
                description = ""
                large_image = None
                
                for script in soup.find_all('script', type='application/ld+json'):
                    try:
                        data = json.loads(script.string)
                        product_data = None
                        if isinstance(data, list):
                            for item in data:
                                if item.get('@type') == 'Product':
                                    product_data = item
                                    break
                        elif isinstance(data, dict):
                            if data.get('@type') == 'Product':
                                product_data = data
                        
                        if product_data:
                            brand_val = product_data.get('brand')
                            brand = brand_val.get('name') if isinstance(brand_val, dict) else brand_val
                            description = product_data.get('description', '')
                            large_image = product_data.get('image')
                            break
                    except Exception:
                        continue

                # Fallback brand parsing from title
                if not brand:
                    for b in common_brands:
                        if re.search(rf'\b{re.escape(b)}\b', category_title, re.IGNORECASE):
                            brand = b
                            break
                if not brand:
                    brand = category_title.split()[0] if category_title.split() else "Generic"

                # Clean Title (strip size suffixes and extra P&P/atomizer text)
                clean_title = category_title
                clean_title = re.sub(r'100%\s*genuine', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'\b\d+\s*ml\b', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'free\s*(p&p|pp|postage)', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'sample\s*(size)?\s*(glass)?\s*(vial)?\s*(bottle)?', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'refillable\s*travel\s*atomise?r', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'travel\s*(fragrance|perfume)?\s*spray', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'\b(atomisers?|atomizers?|spray|sprays|vial|bottle)\b', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'in\s+atomisers?\s+free\s+p&p', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'perfect\s+travel\s+size', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'special\s+offer', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'multi\s+buy\s+sample\s+set', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'3\s+different\s+sizes?', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'new\s+for\s+\d{4}', '', clean_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'best\s+quality', '', clean_title, flags=re.IGNORECASE)
                
                # clean up extra spaces, punctuation and symbols
                clean_title = re.sub(r'[-–—🍃🌸⭐️*~•:,\(\)/]', ' ', clean_title)
                clean_title = ' '.join(clean_title.split())
                clean_title = clean_title.strip(' .–—🍃🌸⭐️*~•:,\(\)/-')

                slug = slugify(clean_title)

                # Check if a product with the same clean_title/slug already exists to merge variants
                product = Product.objects.filter(slug=slug).first()
                
                if not product:
                    # Decide Gender
                    gender_name = 'Unisex'
                    search_text = (category_title + " " + description).lower()
                    if any(x in search_text for x in ['for him', 'pour homme', 'for men', 'mens']):
                        gender_name = 'For Him'
                    elif any(x in search_text for x in ['for her', 'pour femme', 'for women', 'womens', 'lady million', 'good girl']):
                        gender_name = 'For Her'
                    
                    gender_obj, _ = Gender.objects.get_or_create(name=gender_name)

                    # Ensure unique slug
                    base_slug = slug
                    counter = 1
                    while Product.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1

                    short_desc = description[:250] + "..." if len(description) > 250 else description
                    product = Product.objects.create(
                        name=clean_title,
                        slug=slug,
                        brand=brand,
                        description=description,
                        short_description=short_desc,
                        gender=gender_obj,
                        in_stock=True,
                        order=idx
                    )

                    # Download Image
                    image_url = large_image or (soup.find(class_='aerial-product-item_header').find('img').get('data-src') if soup.find(class_='aerial-product-item_header') else None)
                    if image_url:
                        try:
                            img_response = requests.get(image_url, timeout=10)
                            if img_response.status_code == 200:
                                ext = os.path.splitext(image_url.split('?')[0])[1] or '.jpg'
                                img_temp = NamedTemporaryFile(delete=True)
                                img_temp.write(img_response.content)
                                img_temp.flush()
                                product.image.save(f"{slug}{ext}", File(img_temp), save=True)
                        except Exception as img_err:
                            self.stdout.write(self.style.WARNING(f" -> Could not download image: {img_err}"))

                # Parse variants from script
                variants_list = []
                scripts = [s.string for s in soup.find_all('script') if s.string and 'ekmProductVariantData.unshift' in s.string]
                var_script = next((s for s in scripts if '_EKM_PRODUCTPRICE' in s), None)

                if var_script:
                    chunks = re.split(r'"selector"\s*:\s*', var_script)
                    for chunk in chunks[1:]:
                        size_match = re.search(r'"option"\s*:\s*"Size"\s*,\s*"value"\s*:\s*"([^"]+)"', chunk)
                        if not size_match:
                            continue
                        size_str = size_match.group(1)
                        
                        price_match = re.search(r'"elementId"\s*:\s*"_EKM_PRODUCTPRICE"\s*,\s*"innerHTML"\s*:\s*"([^"]+)"', chunk)
                        price = price_match.group(1) if price_match else None
                        
                        stock_match = re.search(r'"elementId"\s*:\s*"_EKM_INSTOCK_VALUE"\s*,\s*"value"\s*:\s*"([^"]+)"', chunk)
                        in_stock = stock_match.group(1) == "True" if stock_match else False

                        if price:
                            variants_list.append({
                                "size": size_str,
                                "price": float(price),
                                "in_stock": in_stock
                            })

                # Fallback: if no variants parsed but we have a base price
                if not variants_list:
                    base_price = None
                    price_meta = soup.find(attrs={"itemprop": "price"}) or soup.find(class_='aerial-product-item_price')
                    if price_meta:
                        price_str = price_meta.get('content') or price_meta.text
                        price_match = re.search(r'£?\s*([0-9.]+)', price_str)
                        if price_match:
                            base_price = float(price_match.group(1))
                    
                    if base_price:
                        variants_list.append({
                            "size": "5ml",
                            "price": base_price,
                            "in_stock": True
                        })

                # Create variants in the database
                for v in variants_list:
                    size_str = v['size']
                    ml_match = re.search(r'(\d+)', size_str)
                    ml_val = int(ml_match.group(1)) if ml_match else 5
                    
                    bottle_size, _ = BottleSize.objects.get_or_create(
                        size_ml=ml_val,
                        defaults={'label': f"{ml_val}ml", 'order': ml_val}
                    )

                    # Ensure unique SKU across different products to avoid database constraint failures
                    base_sku = f"{product.slug[:25]}-{bottle_size.size_ml}ml-{transparent_color.slug}"[:45]
                    variant_sku = base_sku
                    counter = 1
                    while ProductVariant.objects.filter(sku=variant_sku).exclude(product=product).exists():
                        variant_sku = f"{base_sku}-{counter}"
                        counter += 1

                    variant, created = ProductVariant.objects.get_or_create(
                        product=product,
                        bottle_size=bottle_size,
                        bottle_color=transparent_color,
                        defaults={
                            'price': v['price'],
                            'stock_quantity': 20 if v['in_stock'] else 0,
                            'sku': variant_sku
                        }
                    )
                    if not created:
                        variant.price = v['price']
                        variant.stock_quantity = 20 if v['in_stock'] else 0
                        variant.save()

                imported_count += 1
                self.stdout.write(self.style.SUCCESS(f" -> Processed successfully. Variants: {len(variants_list)}"))
                time.sleep(0.5)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing product {category_title}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\nImport finished! Successfully imported/merged {imported_count} products."))
