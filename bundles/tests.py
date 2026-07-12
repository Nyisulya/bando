from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import BundleCategory, Bundle, ResellerConfig

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
        
        # 2. Create a bundle
        self.bundle = Bundle.objects.create(
            name='Internet ya Siku 1.5GB',
            category=self.category,
            price=1000,
            validity='Masaa 24',
            data_limit='1.5 GB',
            is_active=True
        )
        
        # 3. Create config
        self.config = ResellerConfig.objects.create(
            business_name='Bando Test Shop',
            whatsapp_number='255620123456',
            welcome_message='Karibu kwetu',
            payment_instructions='Lipa hapa',
            is_active_config=True
        )
        
        # 4. Create user
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        self.client = Client()

    def test_landing_page(self):
        # Verify landing page returns 200
        url = reverse('bundles:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bando Test Shop')
        self.assertContains(response, 'Internet ya Siku 1.5GB')

    def test_login_page_renders(self):
        # Verify login page loads
        url = reverse('bundles:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_functionality(self):
        # Verify correct credentials can log in
        url = reverse('bundles:login')
        response = self.client.post(url, {
            'username': 'admin',
            'password': 'admin123'
        })
        # Should redirect to dashboard
        self.assertRedirects(response, reverse('bundles:dashboard'))

    def test_dashboard_login_required(self):
        # Dashboard should redirect unauthenticated users to login
        url = reverse('bundles:dashboard')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('bundles:login') + '?next=' + url)

    def test_dashboard_access_for_logged_in_user(self):
        # Login
        self.client.login(username='admin', password='admin123')
        url = reverse('bundles:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Internet ya Siku 1.5GB')
        self.assertContains(response, '255620123456')

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
        })
        self.assertRedirects(response, reverse('bundles:dashboard'))
        self.assertTrue(Bundle.objects.filter(name='Internet ya Wiki 3.5GB').exists())

    def test_delete_bundle(self):
        self.client.login(username='admin', password='admin123')
        url = reverse('bundles:delete_bundle', kwargs={'pk': self.bundle.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('bundles:dashboard'))
        self.assertFalse(Bundle.objects.filter(pk=self.bundle.pk).exists())

    def test_toggle_bundle_status(self):
        self.client.login(username='admin', password='admin123')
        url = reverse('bundles:toggle_bundle_status', kwargs={'pk': self.bundle.pk})
        # Toggle is_active from True to False
        response = self.client.post(url, data='{"field": "is_active", "value": false}', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify it changed in db
        self.bundle.refresh_from_db()
        self.assertFalse(self.bundle.is_active)

    def test_update_bundle_price(self):
        self.client.login(username='admin', password='admin123')
        url = reverse('bundles:update_bundle_price', kwargs={'pk': self.bundle.pk})
        # Change price to 1200
        response = self.client.post(url, data='{"price": 1200}', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify it changed in db
        self.bundle.refresh_from_db()
        self.assertEqual(self.bundle.price, 1200)
