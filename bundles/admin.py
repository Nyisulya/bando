from django.contrib import admin
from .models import BundleCategory, Bundle, ResellerConfig

# Customize the Admin Site Header & Title for the reseller
admin.site.site_header = "Usimamizi wa Mabando (Halotel Reseller)"
admin.site.site_title = "Halotel Reseller Admin Portal"
admin.site.index_title = "Karibu kwenye Mfumo wa Mabando"

@admin.register(BundleCategory)
class BundleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order',)
    search_fields = ('name',)


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'validity', 'is_active', 'is_hot', 'updated_at')
    list_editable = ('price', 'is_active', 'is_hot')
    list_filter = ('category', 'is_active', 'is_hot', 'validity')
    search_fields = ('name', 'description')
    ordering = ('category', 'price')
    list_per_page = 20

    fieldsets = (
        ("Taarifa za Msingi", {
            'fields': ('name', 'category', 'price', 'validity')
        }),
        ("Vipimo vya Mabando", {
            'fields': ('data_limit', 'voice_limit', 'sms_limit'),
            'description': 'Jaza vipimo vinavyohusika tu kwa bando hili.'
        }),
        ("Hali na Maelezo", {
            'fields': ('description', 'is_active', 'is_hot')
        }),
    )


@admin.register(ResellerConfig)
class ResellerConfigAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'whatsapp_number', 'is_active_config')
    list_editable = ('is_active_config',)
    
    def save_model(self, request, obj, form, change):
        # Ensure only one ResellerConfig is active at a time
        if obj.is_active_config:
            ResellerConfig.objects.exclude(pk=obj.pk).update(is_active_config=False)
        super().save_model(request, obj, form, change)
