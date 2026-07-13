from django.core.management.base import BaseCommand
from django.utils import timezone
from bundles.models import Tenant

class Command(BaseCommand):
    help = 'Kagua wateja wote na kufunga subdomains ambazo muda wao wa malipo umekwisha'

    def handle(self, *args, **options):
        today = timezone.now().date()
        expired_tenants = Tenant.objects.filter(is_active=True, paid_until__lt=today)
        count = expired_tenants.count()
        
        for tenant in expired_tenants:
            tenant.is_active = False
            tenant.save(update_fields=['is_active'])
            self.stdout.write(
                self.style.WARNING(f"Mteja {tenant.business_name} ({tenant.subdomain}) amefungiwa. Lipa mpaka: {tenant.paid_until}")
            )
            
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f"Jumla ya wateja {count} wamefungiwa kwa kuisha kwa muda wa matumizi."))
        else:
            self.stdout.write(self.style.SUCCESS("Hakuna mteja yeyote aliyevuka muda wa malipo kwa sasa."))
