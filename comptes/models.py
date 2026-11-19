from django.db import models
from django.contrib.auth.models import AbstractUser


class Utilisateur(AbstractUser):

    class Role(models.TextChoices):
        ETUDIANT = 'ETUDIANT', 'Étudiant'
        ENTREPRISE = 'ENTREPRISE', 'Entreprise'
        ADMIN = 'ADMIN', 'Administrateur'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ETUDIANT
    )


class Etudiant(models.Model):

    utilisateur = models.OneToOneField(
        'comptes.Utilisateur',
        on_delete=models.CASCADE,
        related_name='profil_etudiant'
    )

    formation = models.CharField(max_length=150)
    competences = models.TextField(blank=True)

    def __str__(self):
        return self.utilisateur.username


class Entreprise(models.Model):

    utilisateur = models.OneToOneField(
        'comptes.Utilisateur',
        on_delete=models.CASCADE,
        related_name='profil_entreprise'
    )

    nom_entreprise = models.CharField(max_length=150)
    secteur = models.CharField(max_length=100)

    def __str__(self):
        return self.nom_entreprise

class Contact(models.Model):
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_envoi']
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'

    def __str__(self):
        return f"{self.nom} - {self.sujet}"