from django.db import models
from comptes.models import Etudiant
from offres.models import Offre


class Candidature(models.Model):

    class Statut(models.TextChoices):
        SOUMISE = 'SOUMISE', 'Soumise'
        EN_COURS = 'EN_COURS', 'En cours'
        ACCEPTEE = 'ACCEPTEE', 'Acceptée'
        REFUSEE = 'REFUSEE', 'Refusée'

    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.CASCADE,
        related_name='candidatures'
    )

    offre = models.ForeignKey(
        Offre,
        on_delete=models.CASCADE,
        related_name='candidatures'
    )

    lettre_motivation = models.TextField(blank=True)

    date_candidature = models.DateTimeField(auto_now_add=True)

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.SOUMISE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['etudiant', 'offre'],
                name='candidature_unique_etudiant_offre'
            )
        ]

    def __str__(self):
        return f"{self.etudiant} - {self.offre}"