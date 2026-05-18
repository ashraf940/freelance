from django import forms
from .models import Gig, GigPackage, GigRequirement, GigFaq

class GigCreateForm(forms.ModelForm):
    class Meta:
        model = Gig
        fields = [
            'category', 'title', 'description', 
            'short_description', 'price', 'delivery_days', 
            'featured_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'placeholder': 'Enter gig title'}),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'rows': 5, 'placeholder': 'Detailed description'}),
            'short_description': forms.Textarea(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'rows': 2, 'placeholder': 'Brief summary'}),
            'price': forms.NumberInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'placeholder': '50', 'min': '5'}),
            'delivery_days': forms.NumberInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'placeholder': '3', 'min': '1'}),
            'featured_image': forms.FileInput(attrs={'class': 'w-full border rounded-lg px-3 py-2'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make featured_image optional
        self.fields['featured_image'].required = False
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 5:
            raise forms.ValidationError('Minimum price is $5')
        if price > 10000:
            raise forms.ValidationError('Maximum price is $10,000')
        return price
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters')
        return title
    
    def clean_delivery_days(self):
        days = self.cleaned_data.get('delivery_days')
        if days < 1:
            raise forms.ValidationError('Minimum delivery days is 1')
        if days > 90:
            raise forms.ValidationError('Maximum delivery days is 90')
        return days

class GigPackageForm(forms.ModelForm):
    class Meta:
        model = GigPackage
        fields = ['name', 'price', 'delivery_days', 'revisions', 'features']
        widgets = {
            'name': forms.Select(attrs={'class': 'w-full border rounded-lg px-3 py-2'}),
            'price': forms.NumberInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'min': '5'}),
            'delivery_days': forms.NumberInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'min': '1'}),
            'revisions': forms.NumberInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'min': '0'}),
            'features': forms.Textarea(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'rows': 5, 'placeholder': 'Feature 1\nFeature 2\nFeature 3'}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 5:
            raise forms.ValidationError('Minimum price is $5')
        return price

class GigRequirementForm(forms.ModelForm):
    class Meta:
        model = GigRequirement
        fields = ['question', 'type', 'required', 'options', 'order']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'placeholder': 'Enter question'}),
            'type': forms.Select(attrs={'class': 'w-full border rounded-lg px-3 py-2'}),
            'required': forms.CheckboxInput(attrs={'class': 'mr-2'}),
            'options': forms.Textarea(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'rows': 3, 'placeholder': 'Option 1\nOption 2\nOption 3'}),
            'order': forms.NumberInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'min': '0'}),
        }

class GigFaqForm(forms.ModelForm):
    class Meta:
        model = GigFaq
        fields = ['question', 'answer', 'order']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'placeholder': 'Enter question'}),
            'answer': forms.Textarea(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'rows': 3, 'placeholder': 'Enter answer'}),
            'order': forms.NumberInput(attrs={'class': 'w-full border rounded-lg px-3 py-2', 'min': '0'}),
        }