from django import forms
from django.utils.translation import gettext_lazy as _


class FileUploadForm(forms.Form):
    """
    Form for uploading files to OpenAI.
    """
    file = forms.FileField(
        label=_("File"),
        help_text=_("Upload a file to use with OpenAI. Maximum size: 512MB.")
    )
    purpose = forms.ChoiceField(
        label=_("Purpose"),
        choices=[
            ('assistants', _('Assistants')),
            ('fine-tune', _('Fine-Tuning')),
            ('vision', _('Vision')),
            ('user_data', _('User Data'))
        ],
        initial='assistants',
        help_text=_("How this file will be used with OpenAI.")
    )


class TextToSpeechForm(forms.Form):
    """
    Form for text-to-speech synthesis.
    """
    text = forms.CharField(
        label=_("Text"),
        widget=forms.Textarea(attrs={'rows': 3}),
        max_length=4096,
        help_text=_("Text to convert to speech. Maximum 4096 characters.")
    )
    voice = forms.ChoiceField(
        label=_("Voice"),
        choices=[
            ('alloy', _('Alloy')),
            ('echo', _('Echo')),
            ('fable', _('Fable')),
            ('onyx', _('Onyx')),
            ('nova', _('Nova')),
            ('shimmer', _('Shimmer'))
        ],
        initial='alloy',
        help_text=_("Voice to use for speech synthesis.")
    )
    format = forms.ChoiceField(
        label=_("Format"),
        choices=[
            ('mp3', 'MP3'),
            ('opus', 'Opus')
        ],
        initial='mp3',
        help_text=_("Audio format.")
    )


class SpeechToTextForm(forms.Form):
    """
    Form for speech-to-text transcription.
    """
    audio_file = forms.FileField(
        label=_("Audio File"),
        help_text=_("Upload an audio file for transcription. Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm.")
    )
    language = forms.ChoiceField(
        label=_("Language"),
        choices=[
            ('', _('Auto-detect')),
            ('en', _('English')),
            ('es', _('Spanish')),
            ('fr', _('French')),
            ('de', _('German')),
            ('it', _('Italian')),
            ('pt', _('Portuguese')),
            ('nl', _('Dutch')),
            ('ja', _('Japanese')),
            ('ko', _('Korean')),
            ('zh', _('Chinese'))
        ],
        required=False,
        help_text=_("Language of the audio (optional).")
    )


class StructuredOutputForm(forms.Form):
    """
    Form for configuring structured output format.
    """
    schema = forms.CharField(
        label=_("JSON Schema"),
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'code-editor'}),
        help_text=_("JSON schema for structured output response."),
        required=True
    )
    
    def clean_schema(self):
        schema = self.cleaned_data.get('schema')
        try:
            # Validate that the schema is valid JSON
            import json
            json.loads(schema)
            return schema
        except json.JSONDecodeError:
            raise forms.ValidationError(_("Invalid JSON schema format."))
