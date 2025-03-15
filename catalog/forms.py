from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Rating, AITool
from .constants import RATING_CHOICES, CATEGORY_CHOICES

class RatingForm(forms.ModelForm):
    """
    Form for submitting AI tool ratings.
    """
    stars = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-input'}),
        label=_('Your Rating')
    )
    
    review = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience with this AI tool...'}),
        required=False,
        label=_('Your Review (Optional)')
    )
    
    class Meta:
        model = Rating
        fields = ['stars', 'review']


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