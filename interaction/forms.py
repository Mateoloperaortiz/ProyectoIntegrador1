from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Message, Conversation

class MessageForm(forms.ModelForm):
    """
    Form for creating a new message in a conversation.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Type your message here...',
            'autofocus': 'autofocus'
        }),
        label='',
        max_length=4000
    )
    
    class Meta:
        model = Message
        fields = ['content']


class ConversationTitleForm(forms.ModelForm):
    """
    Form for updating a conversation title.
    """
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Conversation
        fields = ['title']