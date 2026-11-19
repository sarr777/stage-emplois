from django import forms
from .models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = [
            'titre',
            'description',
            'type_offre',
            'localisation',
            'secteur',
            'date_limite',
        ]

        widgets = {
            'date_limite': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }