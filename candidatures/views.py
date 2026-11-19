from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError, transaction

from .models import Candidature
from offres.models import Offre
from comptes.models import Etudiant


@login_required
def postuler(request, offre_id):

    if request.user.role != 'ETUDIANT':
        messages.error(request, "Cette action est réservée aux étudiants.")
        return redirect('liste_offres')

    etudiant = get_object_or_404(
        Etudiant,
        utilisateur=request.user
    )

    offre = get_object_or_404(
        Offre,
        id=offre_id,
        statut=True,
        date_limite__gte=timezone.localdate()
    )

    deja_postule = Candidature.objects.filter(
        etudiant=etudiant,
        offre=offre
    ).exists()

    if deja_postule:
        messages.warning(
            request,
            "Vous avez déjà postulé à cette offre."
        )
        return redirect('tableau_etudiant')

    if request.method == 'POST':
        lettre = request.POST.get('lettre_motivation', '').strip()

        if len(lettre) < 30:
            messages.error(
                request,
                "Votre lettre de motivation doit contenir au moins 30 caractères."
            )
            return render(
                request,
                'candidatures/postuler.html',
                {'offre': offre}
            )

        try:
            with transaction.atomic():
                Candidature.objects.create(
                    etudiant=etudiant,
                    offre=offre,
                    lettre_motivation=lettre
                )

            messages.success(
                request,
                "Votre candidature a été envoyée avec succès."
            )
            return redirect('tableau_etudiant')

        except IntegrityError:
            messages.warning(
                request,
                "Vous avez déjà postulé à cette offre."
            )
            return redirect('tableau_etudiant')

    return render(
        request,
        'candidatures/postuler.html',
        {'offre': offre}
    )


from django.views.decorators.http import require_POST


@login_required
@require_POST
def changer_statut(request, candidature_id):

    if request.user.role != 'ENTREPRISE':
        messages.error(
            request,
            "Accès réservé aux entreprises."
        )
        return redirect('accueil')

    candidature = get_object_or_404(
        Candidature,
        id=candidature_id,
        offre__entreprise__utilisateur=request.user
    )

    statut = request.POST.get('statut')

    statuts_valides = [
        Candidature.Statut.EN_COURS,
        Candidature.Statut.ACCEPTEE,
        Candidature.Statut.REFUSEE
    ]

    if statut in statuts_valides:
        candidature.statut = statut
        candidature.save()

        messages.success(
            request,
            "Le statut de la candidature a été modifié."
        )
    else:
        messages.error(request, "Statut invalide.")

    return redirect('tableau_entreprise')