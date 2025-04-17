from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Rating
from .constants import RATING_CHOICES, CATEGORY_CHOICES



class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars', 'comment']
        widgets = {
            'stars': forms.RadioSelect(
                attrs={'class': 'star-rating'},
                choices=[(5, '★'), (4, '★'), (3, '★'), (2, '★'), (1, '★')]
            ),
            'comment': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Write your opinion here (Optional)...'}
            ),
        }


class SearchForm(forms.Form):
    """
    Form for searching AI tools.
    """
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search AI tools...'})
    )
    
    category = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'category-checkbox'})
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('popularity', _('Popularity')),
            ('rating', _('Rating')),
            ('name', _('Name (A-Z)')),
            ('-name', _('Name (Z-A)')),
            ('newest', _('Newest')),
        ],
        required=False,
        initial='popularity',
        widget=forms.Select(attrs={'class': 'form-select'})
    )