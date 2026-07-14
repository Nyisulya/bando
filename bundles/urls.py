from django.urls import path
from . import views

app_name = 'bundles'

urlpatterns = [
    # Customer-facing website
    path('', views.index, name='index'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    
    # Custom dashboard authentication
    path('dashboard/login/', views.dashboard_login, name='login'),
    path('dashboard/logout/', views.dashboard_logout, name='logout'),
    
    # Dashboard controls
    path('dashboard/', views.dashboard_home, name='dashboard'),
    path('dashboard/bundle/add/', views.add_bundle, name='add_bundle'),
    path('dashboard/bundle/delete/<int:pk>/', views.delete_bundle, name='delete_bundle'),
    path('dashboard/bundle/toggle/<int:pk>/', views.toggle_bundle_status, name='toggle_bundle_status'),
    path('dashboard/bundle/update-price/<int:pk>/', views.update_bundle_price, name='update_bundle_price'),
    path('dashboard/settings/update/', views.update_settings, name='update_settings'),
]
