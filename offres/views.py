from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Offre
from .forms import OffreForm
from comptes.models import Entreprise


def liste_offres(request):
    offres = Offre.objects.filter(
        statut=True,
        date_limite__gte=timezone.localdate()
    ).select_related('entreprise')

    recherche = request.GET.get('recherche', '')
    type_offre = request.GET.get('type_offre', '')
    localisation = request.GET.get('localisation', '')

    if recherche:
        offres = offres.filter(titre__icontains=recherche)

    if type_offre:
        offres = offres.filter(type_offre=type_offre)

    if localisation:
        offres = offres.filter(localisation__icontains=localisation)

    return render(request, 'offres/liste_offres.html', {
        'offres': offres,
    })


@login_required
def ajouter_offre(request):
    if request.user.role != 'ENTREPRISE':
        messages.error(request, "Accès réservé aux entreprises.")
        return redirect('accueil')

    entreprise = get_object_or_404(
        Entreprise,
        utilisateur=request.user
    )

    if request.method == 'POST':
        form = OffreForm(request.POST)

        if form.is_valid():
            offre = form.save(commit=False)
            offre.entreprise = entreprise
            offre.save()

            messages.success(request, "Offre publiée avec succès.")
            return redirect('tableau_entreprise')
    else:
        form = OffreForm()

    return render(request, 'offres/formulaire_offre.html', {
        'form': form,
        'titre': 'Publier une offre',
    })


@login_required
def modifier_offre(request, offre_id):
    if request.user.role != 'ENTREPRISE':
        messages.error(request, "Accès réservé aux entreprises.")
        return redirect('accueil')

    offre = get_object_or_404(
        Offre,
        id=offre_id,
        entreprise__utilisateur=request.user
    )

    if request.method == 'POST':
        form = OffreForm(request.POST, instance=offre)

        if form.is_valid():
            form.save()
            messages.success(request, "Offre modifiée avec succès.")
            return redirect('tableau_entreprise')
    else:
        form = OffreForm(instance=offre)

    return render(request, 'offres/formulaire_offre.html', {
        'form': form,
        'titre': 'Modifier une offre',
    })


@login_required
@require_POST
def supprimer_offre(request, offre_id):
    if request.user.role != 'ENTREPRISE':
        messages.error(request, "Accès réservé aux entreprises.")
        return redirect('accueil')

    offre = get_object_or_404(
        Offre,
        id=offre_id,
        entreprise__utilisateur=request.user
    )

    offre.delete()
    messages.success(request, "Offre supprimée avec succès.")

    return redirect('tableau_entreprise')

@login_required
@require_POST
def fermer_offre(request, offre_id):

    if request.user.role != 'ENTREPRISE':
        messages.error(request, "Accès réservé aux entreprises.")
        return redirect('accueil')

    offre = get_object_or_404(
        Offre,
        id=offre_id,
        entreprise__utilisateur=request.user
    )

    offre.statut = False
    offre.save(update_fields=['statut'])

    messages.success(request, "L'offre a été fermée avec succès.")

    return redirect('tableau_entreprise')