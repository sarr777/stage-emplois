from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_offres, name='liste_offres'),
    path('ajouter/', views.ajouter_offre, name='ajouter_offre'),
    path('modifier/<int:offre_id>/', views.modifier_offre, name='modifier_offre'),
    path('supprimer/<int:offre_id>/', views.supprimer_offre, name='supprimer_offre'),
    path('fermer/<int:offre_id>/', views.fermer_offre, name='fermer_offre'),
]

