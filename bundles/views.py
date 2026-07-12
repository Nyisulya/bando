import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import BundleCategory, Bundle, ResellerConfig
from .forms import BundleForm, ResellerConfigForm

def index(request):
    config = ResellerConfig.objects.filter(is_active_config=True).first()
    if not config:
        config = ResellerConfig(
            business_name="Halotel Bundle Reseller",
            whatsapp_number="255621234567",
            welcome_message="Habari! Karibu kwenye duka letu la mabando ya Halotel ya bei nafuu. Chagua bando lako hapa chini.",
            payment_instructions="Lipa kwa:\n1. HaloPesa: Lipa Namba 123456\n2. M-Pesa: Lipa Namba 654321"
        )
    
    categories = BundleCategory.objects.all().order_by('display_order', 'name')
    active_bundles = Bundle.objects.filter(is_active=True).select_related('category').order_by('price')

    context = {
        'config': config,
        'categories': categories,
        'bundles': active_bundles,
    }
    return render(request, 'bundles/index.html', context)


def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect('bundles:dashboard')
        
    error_message = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('bundles:dashboard')
        else:
            error_message = "Jina la siri au neno la siri sio sahihi!"

    return render(request, 'bundles/login.html', {'error': error_message})


def dashboard_logout(request):
    logout(request)
    return redirect('bundles:index')


@login_required(login_url='bundles:login')
def dashboard_home(request):
    # Fetch configurations
    config = ResellerConfig.objects.filter(is_active_config=True).first()
    if not config:
        config = ResellerConfig.objects.create(
            business_name="Halotel Bundle Reseller",
            whatsapp_number="255621234567",
            is_active_config=True
        )
        
    bundles = Bundle.objects.all().select_related('category').order_by('category__display_order', 'price')
    categories = BundleCategory.objects.all()
    
    # Initialize forms
    bundle_form = BundleForm()
    config_form = ResellerConfigForm(instance=config)
    
    context = {
        'config': config,
        'bundles': bundles,
        'categories': categories,
        'bundle_form': bundle_form,
        'config_form': config_form,
    }
    return render(request, 'bundles/dashboard.html', context)


@login_required(login_url='bundles:login')
@require_POST
def add_bundle(request):
    form = BundleForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('bundles:dashboard')
    # If invalid, render dashboard with errors
    config = ResellerConfig.objects.filter(is_active_config=True).first()
    bundles = Bundle.objects.all().select_related('category').order_by('category__display_order', 'price')
    categories = BundleCategory.objects.all()
    context = {
        'config': config,
        'bundles': bundles,
        'categories': categories,
        'bundle_form': form,
        'config_form': ResellerConfigForm(instance=config),
    }
    return render(request, 'bundles/dashboard.html', context)


@login_required(login_url='bundles:login')
@require_POST
def delete_bundle(request, pk):
    bundle = get_object_or_404(Bundle, pk=pk)
    bundle.delete()
    return redirect('bundles:dashboard')


@login_required(login_url='bundles:login')
@require_POST
def update_settings(request):
    config = ResellerConfig.objects.filter(is_active_config=True).first()
    form = ResellerConfigForm(request.POST, instance=config)
    if form.is_valid():
        form.save()
        return redirect('bundles:dashboard')
        
    # If invalid, render dashboard with errors
    bundles = Bundle.objects.all().select_related('category').order_by('category__display_order', 'price')
    categories = BundleCategory.objects.all()
    context = {
        'config': config,
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
    try:
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')
        
        if field not in ['is_active', 'is_hot']:
            return JsonResponse({'success': False, 'error': 'Uwanja usioruhusiwa'}, status=400)
            
        bundle = Bundle.objects.get(pk=pk)
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
    try:
        data = json.loads(request.body)
        price = int(data.get('price', 0))
        if price <= 0:
            return JsonResponse({'success': False, 'error': 'Bei lazima izidi 0'}, status=400)
            
        bundle = Bundle.objects.get(pk=pk)
        bundle.price = price
        bundle.save()
        
        return JsonResponse({'success': True})
    except Bundle.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bando halikupatikana'}, status=404)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Bei isiyo halali'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
