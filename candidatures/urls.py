from django.urls import path
from . import views

urlpatterns = [
    path('postuler/<int:offre_id>/', views.postuler, name='postuler'),

    path(
        'statut/<int:candidature_id>/',
        views.changer_statut,
        name='changer_statut'
    ),
]