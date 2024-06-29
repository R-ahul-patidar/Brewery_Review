from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'description']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),  # Creates options from 1 to 5
            'description': forms.Textarea(attrs={'rows': 3}),
        }
