from django.contrib import admin
from .models import BundleCategory, Bundle, Tenant

# Customize the Admin Site Header & Title for the platform owner
admin.site.site_header = "Usimamizi wa Mabando SaaS"
admin.site.site_title = "Bando SaaS Admin Portal"
admin.site.index_title = "Usimamizi wa Mfumo wa Mabando (Tenants)"

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'subdomain', 'owner', 'is_active', 'paid_until', 'whatsapp_number', 'updated_at')
    list_editable = ('is_active', 'paid_until')
    search_fields = ('business_name', 'subdomain', 'whatsapp_number', 'owner__username')
    list_filter = ('is_active', 'paid_until', 'created_at')
    ordering = ('subdomain',)


@admin.register(BundleCategory)
class BundleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order',)
    search_fields = ('name',)


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'category', 'price', 'validity', 'is_active', 'is_hot', 'updated_at')
    list_editable = ('price', 'is_active', 'is_hot')
    list_filter = ('tenant', 'category', 'is_active', 'is_hot', 'validity')
    search_fields = ('name', 'description')
    ordering = ('tenant', 'category', 'price')
    list_per_page = 20

    fieldsets = (
        ("Taarifa za Msingi", {
            'fields': ('tenant', 'name', 'category', 'price', 'validity')
        }),
        ("Vipimo vya Mabando", {
            'fields': ('data_limit',),
            'description': 'Jaza vipimo vya bando hili.'
        }),
        ("Hali na Maelezo", {
            'fields': ('description', 'is_active', 'is_hot')
        }),
    )

