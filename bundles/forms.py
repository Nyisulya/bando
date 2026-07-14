from django import forms
from .models import Bundle, Tenant

class BundleForm(forms.ModelForm):
    class Meta:
        model = Bundle
        fields = ['name', 'category', 'price', 'validity', 'data_limit', 'description', 'is_active', 'is_hot']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mfano: Internet ya Siku 1.5GB'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Mfano: 1000'}),
            'validity': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mfano: Masaa 24, Siku 7, au Siku 30'}),
            'data_limit': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mfano: 1.5 GB'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Maelezo ya ziada...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_hot': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class ResellerConfigForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['business_name', 'whatsapp_number', 'welcome_message', 'payment_instructions', 'primary_color', 'secondary_color']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Jina la Duka'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mfano: 255620123456'}),
            'welcome_message': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'payment_instructions': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-color-picker', 'style': 'width: 100%; height: 42px; padding: 0; border: none; border-radius: var(--radius-md); cursor: pointer; background: none;'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-color-picker', 'style': 'width: 100%; height: 42px; padding: 0; border: none; border-radius: var(--radius-md); cursor: pointer; background: none;'}),
        }

