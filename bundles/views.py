import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import BundleCategory, Bundle, Tenant
from .forms import BundleForm, ResellerConfigForm

def index(request):
    if not request.tenant:
        # Main domain landing page
        tenants = Tenant.objects.filter(is_active=True).order_by('subdomain')[:12]
        return render(request, 'bundles/landing.html', {'tenants': tenants})
    
    # Reseller shop domain
    tenant = request.tenant
    
    # Only get categories that have active bundles for this tenant
    categories = BundleCategory.objects.filter(
        bundles__tenant=tenant, 
        bundles__is_active=True
    ).distinct().order_by('display_order', 'name')
    
    active_bundles = Bundle.objects.filter(
        tenant=tenant, 
        is_active=True
    ).select_related('category').order_by('price')

    context = {
        'config': tenant, # Passed as config so the old templates work out-of-the-box
        'categories': categories,
        'bundles': active_bundles,
    }
    return render(request, 'bundles/index.html', context)


def dashboard_login(request):
    if not request.tenant:
        return redirect('bundles:index')
        
    if request.user.is_authenticated:
        # Check permissions
        if request.user == request.tenant.owner or request.user.is_superuser:
            return redirect('bundles:dashboard')
        else:
            logout(request)
            
    error_message = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            if user == request.tenant.owner or user.is_superuser:
                login(request, user)
                return redirect('bundles:dashboard')
            else:
                error_message = "Akaunti hii haina ruhusa ya kusimamia duka hili!"
        else:
            error_message = "Jina la siri au neno la siri sio sahihi!"

    return render(request, 'bundles/login.html', {'error': error_message})


def dashboard_logout(request):
    logout(request)
    return redirect('bundles:index')


@login_required(login_url='bundles:login')
def dashboard_home(request):
    if not request.tenant:
        return redirect('bundles:index')
        
    # Security: Ensure current logged-in user owns the tenant or is superuser
    if not (request.user == request.tenant.owner or request.user.is_superuser):
        logout(request)
        return redirect('bundles:login')
        
    tenant = request.tenant
    bundles = Bundle.objects.filter(tenant=tenant).select_related('category').order_by('category__display_order', 'price')
    categories = BundleCategory.objects.all()
    
    # Initialize forms
    bundle_form = BundleForm()
    config_form = ResellerConfigForm(instance=tenant)
    
    context = {
        'config': tenant,
        'bundles': bundles,
        'categories': categories,
        'bundle_form': bundle_form,
        'config_form': config_form,
    }
    return render(request, 'bundles/dashboard.html', context)


@login_required(login_url='bundles:login')
@require_POST
def add_bundle(request):
    if not request.tenant or not (request.user == request.tenant.owner or request.user.is_superuser):
        return redirect('bundles:index')
        
    form = BundleForm(request.POST)
    if form.is_valid():
        bundle = form.save(commit=False)
        bundle.tenant = request.tenant
        bundle.save()
        return redirect('bundles:dashboard')
        
    tenant = request.tenant
    bundles = Bundle.objects.filter(tenant=tenant).select_related('category').order_by('category__display_order', 'price')
    categories = BundleCategory.objects.all()
    context = {
        'config': tenant,
        'bundles': bundles,
        'categories': categories,
        'bundle_form': form,
        'config_form': ResellerConfigForm(instance=tenant),
    }
    return render(request, 'bundles/dashboard.html', context)


@login_required(login_url='bundles:login')
@require_POST
def delete_bundle(request, pk):
    if not request.tenant or not (request.user == request.tenant.owner or request.user.is_superuser):
        return redirect('bundles:index')
        
    bundle = get_object_or_404(Bundle, pk=pk, tenant=request.tenant)
    bundle.delete()
    return redirect('bundles:dashboard')


@login_required(login_url='bundles:login')
@require_POST
def update_settings(request):
    if not request.tenant or not (request.user == request.tenant.owner or request.user.is_superuser):
        return redirect('bundles:index')
        
    tenant = request.tenant
    form = ResellerConfigForm(request.POST, instance=tenant)
    if form.is_valid():
        form.save()
        return redirect('bundles:dashboard')
        
    bundles = Bundle.objects.filter(tenant=tenant).select_related('category').order_by('category__display_order', 'price')
    categories = BundleCategory.objects.all()
    context = {
        'config': tenant,
        'bundles': bundles,
        'categories': categories,
        'bundle_form': BundleForm(),
        'config_form': form,
    }
    return render(request, 'bundles/dashboard.html', context)


@login_required(login_url='bundles:login')
@require_POST
@ensure_csrf_cookie
def toggle_bundle_status(request, pk):
    if not request.tenant or not (request.user == request.tenant.owner or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Ruhusa imekataliwa'}, status=403)
        
    try:
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')
        
        if field not in ['is_active', 'is_hot']:
            return JsonResponse({'success': False, 'error': 'Uwanja usioruhusiwa'}, status=400)
            
        bundle = Bundle.objects.get(pk=pk, tenant=request.tenant)
        setattr(bundle, field, bool(value))
        bundle.save()
        
        return JsonResponse({'success': True})
    except Bundle.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bando halikupatikana'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='bundles:login')
@require_POST
@ensure_csrf_cookie
def update_bundle_price(request, pk):
    if not request.tenant or not (request.user == request.tenant.owner or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Ruhusa imekataliwa'}, status=403)
        
    try:
        data = json.loads(request.body)
        price = int(data.get('price', 0))
        if price <= 0:
            return JsonResponse({'success': False, 'error': 'Bei lazima izidi 0'}, status=400)
            
        bundle = Bundle.objects.get(pk=pk, tenant=request.tenant)
        bundle.price = price
        bundle.save()
        
        return JsonResponse({'success': True})
    except Bundle.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bando halikupatikana'}, status=404)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Bei isiyo halali'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def robots_txt(request):
    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        f"Sitemap: {protocol}://{host}/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{protocol}://{host}/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    return HttpResponse(sitemap_content, content_type="application/xml")



