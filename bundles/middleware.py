from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from .models import Tenant

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        
        # Retrieve settings configurations
        main_domains = getattr(settings, 'MAIN_DOMAINS', ['localhost', '127.0.0.1'])
        main_domain = getattr(settings, 'MAIN_DOMAIN', 'localhost')
        
        subdomain = None
        
        # Check if the host itself is the main domain or in main domains
        if host in main_domains or host == main_domain:
            request.tenant = None
        elif host.endswith('.testserver'):
            # Handling Django tests
            parts = host.split('.')
            if len(parts) > 1 and parts[-1] == 'testserver':
                subdomain = '.'.join(parts[:-1])
                if subdomain == 'www':
                    subdomain = None
        else:
            # Extract subdomain
            if host.endswith('.' + main_domain):
                subdomain = host[:-len('.' + main_domain)]
            else:
                # General fallback: if host is client1.localhost, extract client1
                parts = host.split('.')
                if len(parts) > 1:
                    # E.g. "client1.localhost" -> parts = ["client1", "localhost"]
                    subdomain = parts[0]
                    if subdomain in ['www', 'admin', 'api']:
                        subdomain = None
                        
        if subdomain:
            try:
                tenant = Tenant.objects.select_related('owner').get(subdomain=subdomain)
                
                # Check for subscription expiration
                if tenant.paid_until and tenant.paid_until < timezone.now().date():
                    if tenant.is_active:
                        tenant.is_active = False
                        tenant.save(update_fields=['is_active'])
                    
                if not tenant.is_active:
                    # Account suspended or expired
                    return render(request, 'bundles/suspended.html', {
                        'tenant': tenant,
                    }, status=403)
                    
                request.tenant = tenant
            except Tenant.DoesNotExist:
                main_host = request.get_host()
                if main_host.startswith(subdomain + '.'):
                    main_host = main_host[len(subdomain) + 1:]
                return render(request, 'bundles/404_tenant.html', {
                    'subdomain': subdomain,
                    'main_host': main_host,
                }, status=404)
        else:
            request.tenant = None
            
        return self.get_response(request)
