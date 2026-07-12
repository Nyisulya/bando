from django.core.management.base import BaseCommand
from bundles.models import BundleCategory, Bundle, ResellerConfig

class Command(BaseCommand):
    help = 'Seeds initial duration categories, internet bundles, and config for Halotel reseller'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database for Internet-only bundles...')

        # 1. Clear existing data to prevent duplicate slug errors
        Bundle.objects.all().delete()
        BundleCategory.objects.all().delete()

        # 2. Create Duration categories
        cat_daily = BundleCategory.objects.create(
            name='Siku 1',
            slug='siku-1',
            icon='calendar-day',
            display_order=1
        )
        cat_weekly = BundleCategory.objects.create(
            name='Siku 7 (Wiki)',
            slug='siku-7',
            icon='calendar-week',
            display_order=2
        )
        cat_monthly = BundleCategory.objects.create(
            name='Siku 30 (Mwezi)',
            slug='siku-30',
            icon='calendar-days',
            display_order=3
        )

        self.stdout.write('Created Duration Categories.')

        # 3. Create Internet-only Bundles
        # Daily
        Bundle.objects.create(
            name='Halotel Internet - 500 MB',
            category=cat_daily,
            price=500,
            validity='Masaa 24',
            data_limit='500 MB',
            description='Kasi ya 4G, inafaa kwa matumizi madogo.'
        )
        Bundle.objects.create(
            name='Halotel Internet Super - 1.5 GB',
            category=cat_daily,
            price=1000,
            validity='Masaa 24',
            data_limit='1.5 GB',
            is_hot=True,
            description='Bando maarufu la siku la Halotel.'
        )
        
        # Weekly
        Bundle.objects.create(
            name='Halotel Internet Wiki - 3.5 GB',
            category=cat_weekly,
            price=3000,
            validity='Siku 7',
            data_limit='3.5 GB',
            description='Bando la wiki la bei nafuu sana.'
        )
        Bundle.objects.create(
            name='Halotel Internet Heavy - 10 GB',
            category=cat_weekly,
            price=8000,
            validity='Siku 7',
            data_limit='10 GB',
            is_hot=True,
            description='Kwa wanaodownload na kuangalia video sana.'
        )
        
        # Monthly
        Bundle.objects.create(
            name='Halotel Internet Mwezi Lite - 15 GB',
            category=cat_monthly,
            price=12000,
            validity='Siku 30',
            data_limit='15 GB',
            description='Bando la mwezi la matumizi ya kawaida.'
        )
        Bundle.objects.create(
            name='Halotel Internet Mwezi Mega - 25 GB',
            category=cat_monthly,
            price=20000,
            validity='Siku 30',
            data_limit='25 GB',
            description='Bando la mwezi mzima kwa matumizi makubwa.'
        )

        self.stdout.write('Created Internet Bundles.')

        # 4. Create ResellerConfig
        ResellerConfig.objects.all().delete()
        ResellerConfig.objects.create(
            business_name='Halotel Mabando Express',
            whatsapp_number='255620123456',
            welcome_message='Karibu Halotel Mabando Express! Pata mabando ya internet ya Halotel kwa bei nafuu sana. Huduma yetu ni ya haraka masaa 24/7.',
            payment_instructions='Lipa kwa:\n1. HaloPesa: Lipa Namba (Till) 998877 (Halotel Mabando Express)\n2. M-Pesa: Lipa Namba (Till) 554433 (Halotel Mabando Express)\n\nBaada ya kufanya muamala, weka namba yako hapo juu na ubonyeze kitufe kuwasilisha malipo WhatsApp.',
            is_active_config=True
        )

        self.stdout.write('Created ResellerConfig.')
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
