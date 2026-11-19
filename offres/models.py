from django.db import models
from comptes.models import Entreprise

# Create your models here.


class Offre(models.Model):

    class TypeOffre(models.TextChoices):
        STAGE = 'STAGE', 'Stage'
        EMPLOI = 'EMPLOI', 'Emploi'

    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='offres'
    )

    titre = models.CharField(max_length=150)
    description = models.TextField()
    type_offre = models.CharField(
        max_length=20,
        choices=TypeOffre.choices
    )
    localisation = models.CharField(max_length=150)
    secteur = models.CharField(max_length=100)

    date_publication = models.DateTimeField(auto_now_add=True)
    date_limite = models.DateField()

    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.titre