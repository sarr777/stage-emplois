from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),

    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),

    path('profil/etudiant/', views.completer_etudiant, name='completer_etudiant'),
    path('profil/entreprise/', views.completer_entreprise, name='completer_entreprise'),

    path('etudiant/dashboard/', views.tableau_etudiant, name='tableau_etudiant'),
    path('entreprise/dashboard/', views.tableau_entreprise, name='tableau_entreprise'),

    path('contact/', views.contact, name='contact'),
    path('apropos/', views.apropos, name='apropos'),
    path('gestion/', views.tableau_admin, name='tableau_admin'),
    path('gestion/messages/', views.messages_contact, name='messages_contact'),
    path('gestion/utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('gestion/etudiants/', views.gestion_etudiants, name='gestion_etudiants'),
    path('gestion/entreprises/',views.gestion_entreprises, name='gestion_entreprises'),
    path('gestion/offres/', views.gestion_offres, name='gestion_offres'),
    path('gestion/candidatures/', views.gestion_candidatures, name='gestion_candidatures'),
]