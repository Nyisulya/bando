from django.db import models
from django.contrib.auth.models import User

class Tenant(models.Model):
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tenants', 
        verbose_name="Mmiliki (Mteja)"
    )
    subdomain = models.SlugField(
        unique=True, 
        db_index=True, 
        verbose_name="Subdomain (Mfano: juma)"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Subdomain Ipo Wazi (Inafanya kazi)?"
    )
    paid_until = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Imelipiwa Mpaka Tarehe"
    )
    
    # Reseller configuration fields merged here
    business_name = models.CharField(
        max_length=100, 
        default="Halotel Bundle Reseller", 
        verbose_name="Jina la Biashara"
    )
    whatsapp_number = models.CharField(
        max_length=20, 
        verbose_name="Namba ya WhatsApp"
    )
    welcome_message = models.TextField(
        default="Habari! Karibu kwenye duka letu la mabando ya Halotel ya bei nafuu na ya haraka sana. Chagua bando lako hapa chini kupata huduma.",
        verbose_name="Ujumbe wa Karibu (Hero Welcome)"
    )
    payment_instructions = models.TextField(
        default="Lipa kwa:\n1. HaloPesa: Lipa Namba (Till) 123456\n2. M-Pesa: Lipa Namba (Till) 654321\n\nBaada ya kulipia, oda yako itashughulikiwa mara moja na utapokea bando.",
        verbose_name="Maelekezo ya Malipo"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tarehe ya Kuundwa")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Tarehe ya Kurekebishwa")

    class Meta:
        verbose_name = "Mteja (Tenant)"
        verbose_name_plural = "Wateja (Tenants)"

    def __str__(self):
        return f"{self.business_name} ({self.subdomain})"


class BundleCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name="Kundi la Muda (Mfano: Siku 1, Wiki 1, Mwezi 1)")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    icon = models.CharField(
        max_length=50, 
        default="wifi", 
        help_text="Mfano: calendar-day, calendar-week, calendar-days (hizi ni icon za FontAwesome)",
        verbose_name="Picha ya Kundi (Icon Class)"
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name="Mpangilio wa Kuonyesha")

    class Meta:
        verbose_name = "Kundi la Muda"
        verbose_name_plural = "Makundi ya Muda"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Bundle(models.Model):
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name="bundles", 
        verbose_name="Mteja (Tenant)",
        null=True, 
        blank=True
    )
    name = models.CharField(max_length=100, verbose_name="Jina la Bando (Mfano: Internet 1.5GB)")
    category = models.ForeignKey(
        BundleCategory, 
        on_delete=models.CASCADE, 
        related_name="bundles", 
        verbose_name="Kundi la Muda"
    )
    price = models.PositiveIntegerField(verbose_name="Bei (TSH)")
    validity = models.CharField(
        max_length=50, 
        help_text="Mfano: Masaa 24, Siku 7, Siku 30", 
        verbose_name="Muda wa Matumizi"
    )
    data_limit = models.CharField(
        max_length=50, 
        default='1.5 GB',
        help_text="Mfano: 1.5 GB, 500 MB, 10 GB", 
        verbose_name="Kiasi cha Internet"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        help_text="Maelezo ya ziada ya bando (Mfano: WhatsApp bure usiku, nk.)", 
        verbose_name="Maeleze ya Ziada"
    )
    is_active = models.BooleanField(default=True, verbose_name="Bando Lipo Wazi?")
    is_hot = models.BooleanField(default=False, verbose_name="Bando Maarufu (Hot)?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tarehe ya Kuwekwa")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Tarehe ya Kurekebishwa")

    class Meta:
        verbose_name = "Bando la Internet"
        verbose_name_plural = "Mabando ya Internet"
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - TSH {self.price:,}"

