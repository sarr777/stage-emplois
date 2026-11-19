from django.contrib import admin
from .models import Offre


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = (
        'titre',
        'entreprise',
        'type_offre',
        'localisation',
        'date_limite',
        'statut'
    )

    list_filter = ('type_offre', 'statut', 'secteur')

    search_fields = ('titre', 'description', 'secteur')