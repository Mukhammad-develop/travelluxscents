from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import (
    SiteSettings, TrustBadge, Badge, Longevity, OccasionTag,
    MoodCollection, FragranceNote, Gender, BottleSize, BottleColor,
    Product, ProductVariant, DiscoverySet,
)
from quiz.models import QuizQuestion, QuizAnswer, QuizRecommendation


class Command(BaseCommand):
    help = 'Load sample data for the perfume decants store'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')

        # Site Settings
        settings = SiteSettings.load()
        settings.site_name = 'TravelLuxScents'
        settings.tagline = 'Premium Fragrance Decants'
        settings.free_delivery_threshold = 40.00
        settings.free_delivery_text = '✦ Free Delivery Over £40 ✦'
        settings.whatsapp_number = '+447000000000'
        settings.delivery_info = 'Royal Mail 1st Class • 1-2 Business Days'
        settings.save()

        # Trust Badges
        trust_data = [
            ('🔒', 'Original Perfumes Only', 'Authentic fragrances guaranteed'),
            ('🧪', 'Hand Decanted', 'Carefully decanted with precision'),
            ('💳', 'Secure Stripe Checkout', 'Your payment details are safe'),
            ('🚀', 'Fast UK Shipping', '1-2 business day delivery'),
        ]
        for i, (icon, title, desc) in enumerate(trust_data):
            TrustBadge.objects.get_or_create(title=title, defaults={'icon': icon, 'description': desc, 'order': i})

        # Badges
        badge_data = [
            ('Best Seller', '#D4AF37', '#FFFFFF'),
            ('New', '#1E40AF', '#FFFFFF'),
            ('For Men', '#000000', '#FFFFFF'),
            ('For Women', '#E91E63', '#FFFFFF'),
            ('Unisex', '#6B7280', '#FFFFFF'),
            ('Limited', '#DC2626', '#FFFFFF'),
        ]
        badges = {}
        for i, (name, color, text) in enumerate(badge_data):
            b, _ = Badge.objects.get_or_create(name=name, defaults={'color': color, 'text_color': text, 'order': i})
            badges[name] = b

        # Longevity
        longevity_data = [('4h+', 4), ('6h+', 6), ('8h+', 8), ('All Day', 12)]
        longevities = {}
        for i, (label, hours) in enumerate(longevity_data):
            l, _ = Longevity.objects.get_or_create(label=label, defaults={'hours': hours, 'order': i})
            longevities[label] = l

        # Occasions
        occ_data = [
            ('Date Night', '🌙'), ('Office', '💼'), ('Daily', '☀️'),
            ('Summer', '🏖️'), ('Winter', '❄️'), ('Luxury', '✨'), ('Party', '🎉'),
            ('Special Occasion', '🎁'),
        ]
        occasions = {}
        for i, (name, icon) in enumerate(occ_data):
            o, _ = OccasionTag.objects.get_or_create(name=name, defaults={'icon': icon, 'order': i})
            occasions[name] = o

        # Moods
        mood_data = [
            ('Clean & Fresh', '🌊', '#00BCD4', 'Light, aquatic, and refreshing scents for everyday wear.'),
            ('Dark & Mysterious', '🖤', '#1a1a1a', 'Deep, intense, and captivating fragrances.'),
            ('Sweet & Addictive', '🍯', '#FF6B6B', 'Warm, sweet, and irresistible scents.'),
            ('Luxury Evening', '✨', '#D4AF37', 'Opulent fragrances for special occasions.'),
            ('Summer Essentials', '☀️', '#FF9800', 'Fresh and vibrant scents for warm days.'),
            ('Woody & Earthy', '🌲', '#4CAF50', 'Rich, earthy, and grounding fragrances.'),
        ]
        moods = {}
        for i, (name, icon, color, desc) in enumerate(mood_data):
            m, _ = MoodCollection.objects.get_or_create(name=name, defaults={
                'icon': icon, 'color': color, 'description': desc, 'order': i
            })
            moods[name] = m

        # Genders
        gender_data = ['For Him', 'For Her', 'Unisex']
        genders = {}
        for i, name in enumerate(gender_data):
            g, _ = Gender.objects.get_or_create(name=name, defaults={'order': i})
            genders[name] = g

        # Fragrance Notes
        note_data = [
            ('Bergamot', '🍊', 'top'), ('Rose', '🌹', 'middle'), ('Oud', '🪵', 'base'),
            ('Vanilla', '🍦', 'base'), ('Jasmine', '🌸', 'middle'), ('Sandalwood', '🪵', 'base'),
            ('Amber', '💎', 'base'), ('Lavender', '💜', 'top'), ('Musk', '🦌', 'base'),
            ('Citrus', '🍋', 'top'), ('Pepper', '🌶️', 'middle'), ('Iris', '🪻', 'middle'),
            ('Tonka Bean', '🫘', 'base'), ('Patchouli', '🌿', 'base'), ('Neroli', '🌼', 'top'),
            ('Cedar', '🌲', 'base'), ('Tobacco', '🍂', 'base'), ('Saffron', '🌺', 'middle'),
            ('Apple', '🍎', 'top'), ('Coconut', '🥥', 'middle'), ('Mint', '🌿', 'top'),
            ('Vetiver', '🌾', 'base'), ('Incense', '🕯️', 'base'), ('Cardamom', '🫛', 'top'),
        ]
        notes = {}
        for name, icon, cat in note_data:
            n, _ = FragranceNote.objects.get_or_create(name=name, defaults={'icon': icon, 'category': cat})
            notes[name] = n

        # Bottle Sizes
        size_data = [(2, '2ml'), (5, '5ml'), (10, '10ml')]
        sizes = {}
        for i, (ml, label) in enumerate(size_data):
            s, _ = BottleSize.objects.get_or_create(size_ml=ml, defaults={'label': label, 'order': i})
            sizes[label] = s

        # Bottle Colors
        color_data = [
            ('Black', '#000000'), ('Blue', '#1E40AF'), ('Green', '#166534'),
            ('Gold', '#D4AF37'), ('White', '#F5F5F5'), ('Transparent', '#E8E8E8'),
        ]
        colors = {}
        for i, (name, hex_c) in enumerate(color_data):
            c, _ = BottleColor.objects.get_or_create(name=name, defaults={'hex_color': hex_c, 'order': i})
            colors[name] = c

        # Products
        products_data = [
            {
                'name': 'Aventus', 'brand': 'Creed', 'gender': 'For Him',
                'description': 'A bold and masculine fragrance with notes of pineapple, birch, and musk. Aventus embodies power, vision, and success.',
                'short_description': 'Iconic masculine powerhouse',
                'notes': ['Bergamot', 'Apple', 'Patchouli', 'Musk'],
                'longevity': '8h+', 'badges': ['Best Seller', 'For Men'],
                'occasions': ['Office', 'Date Night', 'Special Occasion'],
                'moods': ['Luxury Evening'],
                'featured': True,
                'prices': {'2ml': 7.99, '5ml': 14.99, '10ml': 24.99},
            },
            {
                'name': 'Baccarat Rouge 540', 'brand': 'Maison Francis Kurkdjian', 'gender': 'Unisex',
                'description': 'An alchemy of saffron, jasmine, and ambergris that creates a poetic and luminous fragrance.',
                'short_description': 'Iconic crystal-clear amber',
                'notes': ['Saffron', 'Jasmine', 'Amber', 'Cedar'],
                'longevity': 'All Day', 'badges': ['Best Seller', 'Unisex'],
                'occasions': ['Date Night', 'Luxury', 'Special Occasion'],
                'moods': ['Sweet & Addictive', 'Luxury Evening'],
                'featured': True,
                'prices': {'2ml': 9.99, '5ml': 18.99, '10ml': 32.99},
            },
            {
                'name': 'Bleu de Chanel', 'brand': 'Chanel', 'gender': 'For Him',
                'description': 'A woody aromatic fragrance for the man who defies convention. Fresh, clean, and powerful.',
                'short_description': 'The quintessential blue fragrance',
                'notes': ['Citrus', 'Mint', 'Cedar', 'Sandalwood'],
                'longevity': '8h+', 'badges': ['For Men'],
                'occasions': ['Office', 'Daily', 'Date Night'],
                'moods': ['Clean & Fresh'],
                'featured': True,
                'prices': {'2ml': 6.99, '5ml': 12.99, '10ml': 21.99},
            },
            {
                'name': 'Black Orchid', 'brand': 'Tom Ford', 'gender': 'Unisex',
                'description': 'Luxurious and sensual. A rich, dark, and ambitious fragrance with notes of black truffle and orchid.',
                'short_description': 'Dark floral masterpiece',
                'notes': ['Vanilla', 'Oud', 'Patchouli', 'Incense'],
                'longevity': 'All Day', 'badges': ['Unisex'],
                'occasions': ['Date Night', 'Luxury', 'Party'],
                'moods': ['Dark & Mysterious', 'Luxury Evening'],
                'featured': True,
                'prices': {'2ml': 7.49, '5ml': 14.49, '10ml': 23.99},
            },
            {
                'name': 'Oud Wood', 'brand': 'Tom Ford', 'gender': 'Unisex',
                'description': 'Rare oud, sandalwood, and vetiver create a composition of exotic beauty.',
                'short_description': 'Exquisite oud elegance',
                'notes': ['Oud', 'Sandalwood', 'Vetiver', 'Cardamom'],
                'longevity': '8h+', 'badges': ['Unisex', 'Limited'],
                'occasions': ['Luxury', 'Date Night', 'Special Occasion'],
                'moods': ['Dark & Mysterious', 'Woody & Earthy'],
                'featured': True,
                'prices': {'2ml': 8.99, '5ml': 16.99, '10ml': 28.99},
            },
            {
                'name': 'La Vie Est Belle', 'brand': 'Lancôme', 'gender': 'For Her',
                'description': 'A sweet and elegant fragrance that celebrates happiness with iris, praline, and vanilla.',
                'short_description': 'Life is beautiful in a bottle',
                'notes': ['Iris', 'Vanilla', 'Jasmine', 'Tonka Bean'],
                'longevity': '6h+', 'badges': ['Best Seller', 'For Women'],
                'occasions': ['Daily', 'Office', 'Date Night'],
                'moods': ['Sweet & Addictive'],
                'featured': True,
                'prices': {'2ml': 5.99, '5ml': 10.99, '10ml': 18.99},
            },
            {
                'name': 'Sauvage', 'brand': 'Dior', 'gender': 'For Him',
                'description': 'Raw and noble. A powerful and fresh fragrance inspired by wide-open spaces.',
                'short_description': 'Wild masculine freshness',
                'notes': ['Bergamot', 'Pepper', 'Lavender', 'Amber'],
                'longevity': '8h+', 'badges': ['Best Seller', 'For Men'],
                'occasions': ['Daily', 'Office', 'Summer'],
                'moods': ['Clean & Fresh', 'Summer Essentials'],
                'featured': True,
                'prices': {'2ml': 6.49, '5ml': 11.99, '10ml': 19.99},
            },
            {
                'name': 'Tobacco Vanille', 'brand': 'Tom Ford', 'gender': 'Unisex',
                'description': 'Opulent. Warm. Inviting. Tobacco leaf and aromatic spices with vanilla.',
                'short_description': 'Warm tobacco luxury',
                'notes': ['Tobacco', 'Vanilla', 'Tonka Bean', 'Pepper'],
                'longevity': 'All Day', 'badges': ['Unisex'],
                'occasions': ['Winter', 'Date Night', 'Luxury'],
                'moods': ['Dark & Mysterious', 'Sweet & Addictive'],
                'prices': {'2ml': 8.49, '5ml': 15.99, '10ml': 27.99},
            },
            {
                'name': 'Acqua di Gio', 'brand': 'Giorgio Armani', 'gender': 'For Him',
                'description': 'A fresh aquatic fragrance inspired by the Mediterranean. Clean, refreshing, timeless.',
                'short_description': 'Mediterranean freshness',
                'notes': ['Citrus', 'Neroli', 'Cedar', 'Musk'],
                'longevity': '6h+', 'badges': ['For Men', 'New'],
                'occasions': ['Daily', 'Summer', 'Office'],
                'moods': ['Clean & Fresh', 'Summer Essentials'],
                'prices': {'2ml': 5.49, '5ml': 9.99, '10ml': 16.99},
            },
            {
                'name': 'Good Girl', 'brand': 'Carolina Herrera', 'gender': 'For Her',
                'description': 'A bold and elegant scent that captures the dual nature of a modern woman.',
                'short_description': 'Bold feminine elegance',
                'notes': ['Jasmine', 'Tonka Bean', 'Rose', 'Vanilla'],
                'longevity': '8h+', 'badges': ['For Women'],
                'occasions': ['Party', 'Date Night', 'Luxury'],
                'moods': ['Sweet & Addictive', 'Luxury Evening'],
                'prices': {'2ml': 6.49, '5ml': 11.99, '10ml': 20.99},
            },
            {
                'name': 'Lost Cherry', 'brand': 'Tom Ford', 'gender': 'Unisex',
                'description': 'Luscious, sweet, and seductive. A playful yet sophisticated cherry-almond fragrance.',
                'short_description': 'Irresistible cherry indulgence',
                'notes': ['Vanilla', 'Tonka Bean', 'Rose', 'Sandalwood'],
                'longevity': '8h+', 'badges': ['Unisex', 'New'],
                'occasions': ['Date Night', 'Party', 'Special Occasion'],
                'moods': ['Sweet & Addictive'],
                'prices': {'2ml': 9.49, '5ml': 17.99, '10ml': 30.99},
            },
            {
                'name': 'Interlude Man', 'brand': 'Amouage', 'gender': 'For Him',
                'description': 'A masterpiece of Middle Eastern perfumery. Oud, frankincense, and smoky incense.',
                'short_description': 'Intense oriental masterpiece',
                'notes': ['Oud', 'Amber', 'Incense', 'Saffron'],
                'longevity': 'All Day', 'badges': ['For Men', 'Limited'],
                'occasions': ['Winter', 'Luxury', 'Special Occasion'],
                'moods': ['Dark & Mysterious', 'Woody & Earthy'],
                'prices': {'2ml': 10.99, '5ml': 19.99, '10ml': 34.99},
            },
        ]

        created_products = []
        for i, pd in enumerate(products_data):
            p, created = Product.objects.get_or_create(
                name=pd['name'],
                defaults={
                    'brand': pd['brand'],
                    'description': pd['description'],
                    'short_description': pd['short_description'],
                    'gender': genders[pd['gender']],
                    'longevity': longevities[pd['longevity']],
                    'featured': pd.get('featured', False),
                    'in_stock': True,
                    'order': i,
                }
            )
            if created:
                p.notes.set([notes[n] for n in pd['notes']])
                p.badges.set([badges[b] for b in pd['badges']])
                p.occasions.set([occasions[o] for o in pd['occasions']])
                p.mood_collections.set([moods[m] for m in pd['moods']])

                # Create variants for all sizes × all colors
                for size_label, price in pd['prices'].items():
                    for color_name, color_obj in colors.items():
                        ProductVariant.objects.get_or_create(
                            product=p,
                            bottle_size=sizes[size_label],
                            bottle_color=color_obj,
                            defaults={'price': price, 'stock_quantity': 20}
                        )

            created_products.append(p)

        # Discovery Sets
        ds_data = [
            ('Pick Any 3', 3, 19.99, 23.97, '2ml', 'Try 3 premium fragrance samples at a special price.'),
            ('Pick Any 5', 5, 29.99, 39.95, '2ml', 'Our most popular discovery set. 5 fragrances to explore.'),
            ('Pick Any 10', 10, 49.99, 79.90, '2ml', 'The ultimate fragrance exploration. 10 premium decants.'),
        ]
        for i, (name, count, price, orig, size, desc) in enumerate(ds_data):
            DiscoverySet.objects.get_or_create(
                name=name,
                defaults={
                    'pick_count': count,
                    'price': price,
                    'original_price': orig,
                    'bottle_size': sizes[size],
                    'description': desc,
                    'is_active': True,
                    'order': i,
                }
            )

        # Quiz Questions
        quiz_data = [
            (1, "Who is this fragrance for?", "Let's find the perfect scent", [
                ('For Men', '👨', 'men', 'Bold, masculine fragrances'),
                ('For Women', '👩', 'women', 'Elegant, feminine scents'),
                ('Unisex', '🌟', 'unisex', 'Gender-neutral fragrances'),
            ]),
            (2, "What vibe are you going for?", "Choose the mood that speaks to you", [
                ('Fresh & Clean', '🌊', 'fresh', 'Light, aquatic, refreshing'),
                ('Sweet & Addictive', '🍯', 'sweet', 'Warm, gourmand, irresistible'),
                ('Dark & Mysterious', '🖤', 'dark', 'Deep, smoky, intense'),
                ('Elegant & Luxury', '✨', 'luxury', 'Sophisticated, refined, premium'),
                ('Soft & Daily', '☁️', 'soft', 'Gentle, easy-wearing, comfortable'),
            ]),
            (3, "When will you wear it?", "Pick your main occasion", [
                ('Daily', '☀️', 'daily', 'Everyday versatile scent'),
                ('Office', '💼', 'office', 'Professional and clean'),
                ('Date Night', '🌙', 'date_night', 'Alluring and romantic'),
                ('Party', '🎉', 'party', 'Bold and noticeable'),
                ('Special Occasion', '🎁', 'special', 'For memorable moments'),
            ]),
            (4, "What season?", "When do you want to wear it most?", [
                ('Summer', '☀️', 'summer', 'Light, fresh, airy'),
                ('Winter', '❄️', 'winter', 'Warm, cosy, rich'),
                ('Spring', '🌸', 'spring', 'Floral, green, vibrant'),
                ('Autumn', '🍂', 'autumn', 'Earthy, spicy, warm'),
                ('All Year', '🌍', 'all_year', 'Versatile for any season'),
            ]),
            (5, "How strong do you like it?", "Choose your preferred intensity", [
                ('Light', '💨', 'light', 'Subtle and close to skin'),
                ('Moderate', '🌤️', 'moderate', 'Noticeable but not overpowering'),
                ('Strong', '💪', 'strong', 'Bold and long-lasting'),
                ('Very Strong', '🔥', 'very_strong', 'Beast mode projection'),
            ]),
        ]

        for step, title, subtitle, answers in quiz_data:
            q, _ = QuizQuestion.objects.get_or_create(step_number=step, defaults={'title': title, 'subtitle': subtitle})
            for i, (text, icon, value, desc) in enumerate(answers):
                QuizAnswer.objects.get_or_create(
                    question=q, value=value,
                    defaults={'text': text, 'icon': icon, 'description': desc, 'order': i}
                )

        # Quiz Recommendations
        rec_map = [
            ('Aventus', 'men', 'luxury', 'office', 'all_year', 'strong'),
            ('Aventus', 'men', 'fresh', 'date_night', 'summer', 'strong'),
            ('Baccarat Rouge 540', 'unisex', 'sweet', 'date_night', 'winter', 'very_strong'),
            ('Baccarat Rouge 540', 'women', 'luxury', 'special', 'all_year', 'strong'),
            ('Bleu de Chanel', 'men', 'fresh', 'office', 'all_year', 'moderate'),
            ('Bleu de Chanel', 'men', 'soft', 'daily', 'summer', 'moderate'),
            ('Black Orchid', 'unisex', 'dark', 'date_night', 'winter', 'strong'),
            ('Black Orchid', 'women', 'dark', 'party', 'autumn', 'very_strong'),
            ('Oud Wood', 'unisex', 'dark', 'special', 'winter', 'strong'),
            ('Oud Wood', 'men', 'luxury', 'date_night', 'autumn', 'strong'),
            ('La Vie Est Belle', 'women', 'sweet', 'daily', 'spring', 'moderate'),
            ('La Vie Est Belle', 'women', 'soft', 'office', 'all_year', 'light'),
            ('Sauvage', 'men', 'fresh', 'daily', 'summer', 'moderate'),
            ('Sauvage', 'men', 'fresh', 'office', 'spring', 'moderate'),
            ('Tobacco Vanille', 'unisex', 'sweet', 'date_night', 'winter', 'very_strong'),
            ('Tobacco Vanille', 'men', 'dark', 'party', 'winter', 'strong'),
            ('Acqua di Gio', 'men', 'fresh', 'daily', 'summer', 'light'),
            ('Acqua di Gio', 'men', 'soft', 'office', 'spring', 'moderate'),
            ('Good Girl', 'women', 'sweet', 'party', 'autumn', 'strong'),
            ('Good Girl', 'women', 'luxury', 'date_night', 'all_year', 'strong'),
            ('Lost Cherry', 'unisex', 'sweet', 'date_night', 'autumn', 'strong'),
            ('Lost Cherry', 'women', 'sweet', 'party', 'winter', 'strong'),
            ('Interlude Man', 'men', 'dark', 'special', 'winter', 'very_strong'),
            ('Interlude Man', 'men', 'luxury', 'date_night', 'autumn', 'very_strong'),
        ]

        for name, gender, vibe, occasion, season, strength in rec_map:
            try:
                product = Product.objects.get(name=name)
                QuizRecommendation.objects.get_or_create(
                    product=product,
                    gender_value=gender,
                    vibe_value=vibe,
                    occasion_value=occasion,
                    defaults={'season_value': season, 'strength_value': strength, 'score_weight': 1}
                )
            except Product.DoesNotExist:
                pass

        # Create superuser
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.WARNING('Superuser created: admin / admin123'))

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded sample data: {len(created_products)} products'))
