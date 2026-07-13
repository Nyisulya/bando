from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import BundleCategory, Bundle, Tenant
import datetime

User = get_user_model()

class BundleResellerTestCase(TestCase):
    def setUp(self):
        # 1. Create a category
        self.category = BundleCategory.objects.create(
            name='Daily',
            slug='daily',
            icon='calendar-day',
            display_order=1
        )
        
        # 2. Create user (owner of tenant)
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        # 3. Create tenant
        self.tenant = Tenant.objects.create(
            owner=self.user,
            subdomain='testshop',
            business_name='Bando Test Shop',
            whatsapp_number='255620123456',
            welcome_message='Karibu kwetu',
            payment_instructions='Lipa hapa',
            is_active=True,
            paid_until=datetime.date.today() + datetime.timedelta(days=30)
        )
        
        # 4. Create a bundle
        self.bundle = Bundle.objects.create(
            tenant=self.tenant,
            name='Internet ya Siku 1.5GB',
            category=self.category,
            price=1000,
            validity='Masaa 24',
            data_limit='1.5 GB',
            is_active=True
        )
        
        self.client = Client()

    def test_landing_page(self):
        # Verify central landing page of the platform returns 200 (no subdomain)
        url = reverse('bundles:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Anzisha Duka Lako la Mabando')

    def test_tenant_shop_page(self):
        # Verify tenant shop returns 200 and details when visited via subdomain
        url = reverse('bundles:index')
        response = self.client.get(url, HTTP_HOST='testshop.testserver')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bando Test Shop')
        self.assertContains(response, 'Internet ya Siku 1.5GB')

    def test_login_page_renders(self):
        # Verify login page loads for tenant subdomain
        url = reverse('bundles:login')
        response = self.client.get(url, HTTP_HOST='testshop.testserver')
        self.assertEqual(response.status_code, 200)

    def test_login_page_redirects_on_main_domain(self):
        # Logging in on main domain is not allowed, redirects to landing page
        url = reverse('bundles:login')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('bundles:index'))

    def test_login_functionality(self):
        # Verify correct credentials can log in on tenant subdomain
        url = reverse('bundles:login')
        # We need to associate session with HTTP_HOST so auth works correctly
        response = self.client.post(url, {
            'username': 'admin',
            'password': 'admin123'
        }, HTTP_HOST='testshop.testserver')
        # Should redirect to dashboard
        self.assertRedirects(response, reverse('bundles:dashboard'))

    def test_dashboard_login_required(self):
        # Dashboard should redirect unauthenticated users to login
        url = reverse('bundles:dashboard')
        response = self.client.get(url, HTTP_HOST='testshop.testserver')
        self.assertRedirects(response, reverse('bundles:login') + '?next=' + url)

    def test_dashboard_access_for_logged_in_user(self):
        # Login via HTTP_HOST
        self.client.login(username='admin', password='admin123')
        url = reverse('bundles:dashboard')
        response = self.client.get(url, HTTP_HOST='testshop.testserver')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Internet ya Siku 1.5GB')
        self.assertContains(response, '255620123456')

    def test_unauthorized_dashboard_access(self):
        # Create another user
        User.objects.create_user(
            username='other_user',
            password='otherpassword'
        )
        # Login as other_user
        self.client.login(username='other_user', password='otherpassword')
        
        # Try to access testshop dashboard
        url = reverse('bundles:dashboard')
        response = self.client.get(url, HTTP_HOST='testshop.testserver')
        # Should redirect to login since they do not own this tenant
        self.assertRedirects(response, reverse('bundles:login'))

    def test_add_bundle(self):
        # Login
        self.client.login(username='admin', password='admin123')
        url = reverse('bundles:add_bundle')
        response = self.client.post(url, {
            'category': self.category.id,
            'name': 'Internet ya Wiki 3.5GB',
            'data_limit': '3.5 GB',
            'validity': 'Siku 7',
            'price': 3000,
            'description': 'Bando ya wiki',
            'is_active': True,
            'is_hot': False
        }, HTTP_HOST='testshop.testserver')
        self.assertRedirects(response, reverse('bundles:dashboard'))
        self.assertTrue(Bundle.objects.filter(name='Internet ya Wiki 3.5GB', tenant=self.tenant).exists())

    def test_delete_bundle(self):
        self.client.login(username='admin', password='admin123')
        url = reverse('bundles:delete_bundle', kwargs={'pk': self.bundle.pk})
        response = self.client.post(url, HTTP_HOST='testshop.testserver')
        self.assertRedirects(response, reverse('bundles:dashboard'))
        self.assertFalse(Bundle.objects.filter(pk=self.bundle.pk).exists())

    def test_toggle_bundle_status(self):
        self.client.login(username='admin', password='admin123')
        url = reverse('bundles:toggle_bundle_status', kwargs={'pk': self.bundle.pk})
        # Toggle is_active from True to False
        response = self.client.post(
            url, 
            data='{"field": "is_active", "value": false}', 
            content_type='application/json',
            HTTP_HOST='testshop.testserver'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify it changed in db
        self.bundle.refresh_from_db()
        self.assertFalse(self.bundle.is_active)

    def test_update_bundle_price(self):
        self.client.login(username='admin', password='admin123')
        url = reverse('bundles:update_bundle_price', kwargs={'pk': self.bundle.pk})
        # Change price to 1200
        response = self.client.post(
            url, 
            data='{"price": 1200}', 
            content_type='application/json',
            HTTP_HOST='testshop.testserver'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify it changed in db
        self.bundle.refresh_from_db()
        self.assertEqual(self.bundle.price, 1200)

    def test_subscription_expiration_suspension(self):
        # Set paid_until to yesterday
        self.tenant.paid_until = datetime.date.today() - datetime.timedelta(days=1)
        self.tenant.save()
        
        url = reverse('bundles:index')
        response = self.client.get(url, HTTP_HOST='testshop.testserver')
        
        # Should return 403 Forbidden and show suspended template
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'Huduma Imesitishwa kwa Muda', status_code=403)

