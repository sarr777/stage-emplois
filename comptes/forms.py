from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur, Etudiant, Entreprise,Contact


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={
            'placeholder': 'exemple@email.com'
        })
    )

    role = forms.ChoiceField(
        label="Vous êtes",
        choices=[
            ('ETUDIANT', 'Étudiant'),
            ('ENTREPRISE', 'Entreprise'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'placeholder': 'Choisissez un nom d’utilisateur'
        })
    )

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Choisissez un mot de passe'
        })
    )

    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Répétez votre mot de passe'
        })
    )

    class Meta:
        model = Utilisateur
        fields = [
            'username',
            'email',
            'role',
            'password1',
            'password2'
        ]

class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['formation', 'competences']


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['nom_entreprise', 'secteur']


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['nom', 'email', 'sujet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Votre adresse e-mail'
            }),
            'sujet': forms.TextInput(attrs={
                'placeholder': 'Sujet de votre message'
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Écrivez votre message...',
                'rows': 5
            }),
        }