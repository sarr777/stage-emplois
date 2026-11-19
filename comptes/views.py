from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from .forms import InscriptionForm, EtudiantForm, EntrepriseForm,ContactForm
from comptes.models import Utilisateur, Etudiant, Entreprise
from candidatures.models import Candidature
from .models import Etudiant, Entreprise,Contact
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from offres.models import Offre



def accueil(request):
    offres = Offre.objects.filter(
        statut=True,
        date_limite__gte=timezone.localdate()
    ).select_related('entreprise').order_by('-date_publication')[:3]

    return render(request, 'comptes/accueil.html', {
        'offres': offres
    })

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)

        if form.is_valid():
            utilisateur = form.save()

            login(
                request,
                utilisateur,
                backend='django.contrib.auth.backends.ModelBackend'
            )

            if utilisateur.role == 'ETUDIANT':
                return redirect('completer_etudiant')

            elif utilisateur.role == 'ENTREPRISE':
                return redirect('completer_entreprise')

    else:
        form = InscriptionForm()

    return render(
        request,
        'comptes/inscription.html',
        {'form': form}
    )

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a été envoyé avec succès.")
            return redirect('accueil')
    else:
        form = ContactForm()

    return render(request, 'comptes/contact.html', {
        'form': form
    })

@login_required
def completer_etudiant(request):

    if request.user.role != 'ETUDIANT':
        return redirect('accueil')

    # Vérifier si le profil existe déjà
    if Etudiant.objects.filter(utilisateur=request.user).exists():
        return redirect('tableau_etudiant')

    if request.method == 'POST':
        form = EtudiantForm(request.POST)

        if form.is_valid():
            profil = form.save(commit=False)
            profil.utilisateur = request.user
            profil.save()

            messages.success(
                request,
                "Votre profil étudiant a été créé avec succès."
            )

            return redirect('tableau_etudiant')

    else:
        form = EtudiantForm()

    return render(
        request,
        'comptes/profil_etudiant.html',
        {'form': form}
    )

@login_required
def completer_entreprise(request):

    if request.user.role != 'ENTREPRISE':
        return redirect('accueil')

    # Vérifier si le profil existe déjà
    if Entreprise.objects.filter(utilisateur=request.user).exists():
        return redirect('tableau_entreprise')

    if request.method == 'POST':
        form = EntrepriseForm(request.POST)

        if form.is_valid():
            profil = form.save(commit=False)
            profil.utilisateur = request.user
            profil.save()

            messages.success(
                request,
                "Votre profil entreprise a été créé avec succès."
            )

            return redirect('tableau_entreprise')

    else:
        form = EntrepriseForm()

    return render(
        request,
        'comptes/profil_entreprise.html',
        {'form': form}
    )



def connexion(request):
    from django.contrib.auth import authenticate

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        utilisateur = authenticate(
            request,
            username=username,
            password=password
        )

        if utilisateur is not None:

            if not utilisateur.is_active:
                messages.error(request, "Votre compte est désactivé.")
                return render(request, 'comptes/connexion.html')

            login(request, utilisateur)

            if utilisateur.role == 'ETUDIANT':
                return redirect('tableau_etudiant')

            elif utilisateur.role == 'ENTREPRISE':
                return redirect('tableau_entreprise')

            elif utilisateur.role == 'ADMIN':
                return redirect('tableau_admin')

            else:
                logout(request)
                messages.error(request, "Rôle utilisateur non reconnu.")

        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request, 'comptes/connexion.html')


@login_required
def deconnexion(request):
    logout(request)
    return redirect('connexion')



@login_required
def tableau_etudiant(request):
    from candidatures.models import Candidature

    if request.user.role != 'ETUDIANT':
        return redirect('accueil')

    profil = get_object_or_404(
        Etudiant,
        utilisateur=request.user
    )

    candidatures = Candidature.objects.filter(
        etudiant=profil
    ).select_related('offre')


    en_cours = candidatures.filter(
        statut='EN_COURS'
    ).count()

    acceptees = candidatures.filter(
        statut='ACCEPTEE'
    ).count()
   
    return render(request, 'comptes/dashboard_etudiant.html', {
        'profil': profil,
        'candidatures': candidatures,
        'en_cours': en_cours,
        'acceptees': acceptees,
    })


@login_required
def tableau_entreprise(request):
    from offres.models import Offre
    from candidatures.models import Candidature

    if request.user.role != 'ENTREPRISE':
        return redirect('accueil')

    profil = get_object_or_404(
        Entreprise,
        utilisateur=request.user
    )

    offres = Offre.objects.filter(entreprise=profil)

    candidatures = Candidature.objects.filter(
        offre__entreprise=profil
    ).select_related(
        'etudiant__utilisateur',
        'offre'
    )

    offres_ouvertes = offres.filter(statut=True).count()


    return render(request, 'comptes/dashboard_entreprise.html', {
        'profil': profil,
        'offres': offres,
        'candidatures': candidatures,
        'offres_ouvertes': offres_ouvertes,
    })

@login_required
def tableau_admin(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('accueil')

    statistiques = {
        'total_utilisateurs': Utilisateur.objects.count(),
        'total_etudiants': Etudiant.objects.count(),
        'total_entreprises': Entreprise.objects.count(),
        'total_offres': Offre.objects.count(),
        'offres_actives': Offre.objects.filter(statut=True).count(),
        'total_candidatures': Candidature.objects.count(),
        'total_messages': Contact.objects.count(),
        'messages_non_lus': Contact.objects.filter(lu=False).count(),
    }

    return render(request, 'comptes/dashboard_admin.html', {
        'statistiques': statistiques
    })


@login_required
def messages_contact(request):
    # Réserver cette page aux administrateurs
    if request.user.role != 'ADMIN':
        return redirect('accueil')

    if request.method == 'POST':
        contact_id = request.POST.get('contact_id')
        action = request.POST.get('action')

        contact = get_object_or_404(Contact, id=contact_id)

        if action == 'lu':
            contact.lu = True
            contact.save(update_fields=['lu'])
            messages.success(request, 'Message marqué comme lu.')

        elif action == 'non_lu':
            contact.lu = False
            contact.save(update_fields=['lu'])
            messages.success(request, 'Message marqué comme non lu.')

        elif action == 'supprimer':
            contact.delete()
            messages.success(request, 'Message supprimé.')

        return redirect('messages_contact')

    recherche = request.GET.get('recherche', '')

    contacts = Contact.objects.all()

    if recherche:
        contacts = contacts.filter(
            nom__icontains=recherche
        ) | contacts.filter(
            email__icontains=recherche
        ) | contacts.filter(
            sujet__icontains=recherche
        )

    context = {
        'contacts': contacts,
        'total_messages': Contact.objects.count(),
        'messages_non_lus': Contact.objects.filter(lu=False).count(),
        'recherche': recherche,
    }

    return render(request, 'comptes/messages_contact.html', context)



@login_required
def gestion_utilisateurs(request):
    if request.user.role != 'ADMIN':
        return redirect('accueil')

    if request.method == 'POST':
        action = request.POST.get('action')

        # AJOUTER UN UTILISATEUR
        if action == 'ajouter':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            password = request.POST.get('password', '')
            role = request.POST.get('role')

            if not username or not email or not password:
                messages.error(request, "Les champs obligatoires sont requis.")
            elif role not in ['ETUDIANT', 'ENTREPRISE', 'ADMIN']:
                messages.error(request, "Rôle invalide.")
            elif Utilisateur.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur existe déjà.")
            elif Utilisateur.objects.filter(email=email).exists():
                messages.error(request, "Cette adresse e-mail existe déjà.")
            else:
                utilisateur = Utilisateur(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role=role
                )
                utilisateur.set_password(password)
                utilisateur.save()
                messages.success(request, "Utilisateur ajouté avec succès.")

            return redirect('gestion_utilisateurs')

        # AUTRES ACTIONS
        utilisateur_id = request.POST.get('utilisateur_id')

        if not utilisateur_id:
            messages.error(request, "Utilisateur introuvable.")
            return redirect('gestion_utilisateurs')

        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

        if utilisateur == request.user:
            messages.error(request, "Vous ne pouvez pas modifier votre propre compte ici.")
            return redirect('gestion_utilisateurs')

        if utilisateur.is_superuser:
            messages.error(request, "Impossible de modifier ou supprimer un super administrateur.")
            return redirect('gestion_utilisateurs')

        if action == 'modifier':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            role = request.POST.get('role')

            if not username or not email:
                messages.error(request, "Nom d'utilisateur et e-mail obligatoires.")
            elif Utilisateur.objects.exclude(id=utilisateur.id).filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur existe déjà.")
            elif Utilisateur.objects.exclude(id=utilisateur.id).filter(email=email).exists():
                messages.error(request, "Cette adresse e-mail existe déjà.")
            elif role not in ['ETUDIANT', 'ENTREPRISE', 'ADMIN']:
                messages.error(request, "Rôle invalide.")
            else:
                utilisateur.username = username
                utilisateur.first_name = request.POST.get('first_name', '').strip()
                utilisateur.last_name = request.POST.get('last_name', '').strip()
                utilisateur.email = email
                utilisateur.role = role
                utilisateur.save()
                messages.success(request, "Utilisateur modifié avec succès.")

        elif action == 'activer':
            utilisateur.is_active = True
            utilisateur.save(update_fields=['is_active'])
            messages.success(request, "Compte activé avec succès.")

        elif action == 'desactiver':
            utilisateur.is_active = False
            utilisateur.save(update_fields=['is_active'])
            messages.success(request, "Compte désactivé avec succès.")

        elif action == 'supprimer':
            utilisateur.delete()
            messages.success(request, "Utilisateur supprimé avec succès.")

        return redirect('gestion_utilisateurs')

    recherche = request.GET.get('recherche', '')
    utilisateurs = Utilisateur.objects.all().order_by('-date_joined')

    if recherche:
        utilisateurs = utilisateurs.filter(
            Q(username__icontains=recherche) |
            Q(first_name__icontains=recherche) |
            Q(last_name__icontains=recherche) |
            Q(email__icontains=recherche)
        )

    context = {
        'utilisateurs': utilisateurs,
        'total_utilisateurs': Utilisateur.objects.count(),
        'total_actifs': Utilisateur.objects.filter(is_active=True).count(),
        'total_inactifs': Utilisateur.objects.filter(is_active=False).count(),
        'recherche': recherche,
    }

    return render(request, 'comptes/gestion_utilisateurs.html', context)


@login_required
def gestion_etudiants(request):
    if request.user.role != 'ADMIN':
        return redirect('accueil')

    if request.method == 'POST':
        etudiant_id = request.POST.get('etudiant_id')
        action = request.POST.get('action')

        etudiant = get_object_or_404(Etudiant, id=etudiant_id)
        utilisateur = etudiant.utilisateur

        if utilisateur == request.user or utilisateur.is_superuser:
            messages.error(request, "Cette action n'est pas autorisée.")
            return redirect('gestion_etudiants')

        if action == 'activer':
            utilisateur.is_active = True
            utilisateur.save(update_fields=['is_active'])
            messages.success(request, "Étudiant activé avec succès.")

        elif action == 'desactiver':
            utilisateur.is_active = False
            utilisateur.save(update_fields=['is_active'])
            messages.success(request, "Étudiant désactivé avec succès.")

        elif action == 'supprimer':
            utilisateur.delete()
            messages.success(request, "Étudiant supprimé avec succès.")

        return redirect('gestion_etudiants')

    recherche = request.GET.get('recherche', '').strip()

    etudiants = Etudiant.objects.select_related(
        'utilisateur'
    ).order_by('-utilisateur__date_joined')

    if recherche:
        etudiants = etudiants.filter(
            Q(utilisateur__username__icontains=recherche) |
            Q(utilisateur__first_name__icontains=recherche) |
            Q(utilisateur__last_name__icontains=recherche) |
            Q(utilisateur__email__icontains=recherche) |
            Q(formation__icontains=recherche) |
            Q(competences__icontains=recherche)
        )

    context = {
        'etudiants': etudiants,
        'total_etudiants': Etudiant.objects.count(),
        'etudiants_actifs': Etudiant.objects.filter(
            utilisateur__is_active=True
        ).count(),
        'etudiants_inactifs': Etudiant.objects.filter(
            utilisateur__is_active=False
        ).count(),
        'recherche': recherche,
    }

    return render(request, 'comptes/gestion_etudiants.html', context)


@login_required
def gestion_entreprises(request):
    if request.user.role != 'ADMIN':
        return redirect('accueil')

    if request.method == 'POST':
        entreprise_id = request.POST.get('entreprise_id')
        action = request.POST.get('action')

        entreprise = get_object_or_404(Entreprise, id=entreprise_id)
        utilisateur = entreprise.utilisateur

        # Protection du compte administrateur
        if utilisateur == request.user or utilisateur.is_superuser:
            messages.error(request, "Cette action n'est pas autorisée.")
            return redirect('gestion_entreprises')

        # MODIFICATION
        if action == 'modifier':
            nom = request.POST.get('nom_entreprise', '').strip()
            secteur = request.POST.get('secteur', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()

            if not nom or not secteur or not username or not email:
                messages.error(request, "Tous les champs sont obligatoires.")

            elif Utilisateur.objects.exclude(id=utilisateur.id).filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur existe déjà.")

            elif Utilisateur.objects.exclude(id=utilisateur.id).filter(email=email).exists():
                messages.error(request, "Cette adresse e-mail est déjà utilisée.")

            else:
                entreprise.nom_entreprise = nom
                entreprise.secteur = secteur
                entreprise.save()

                utilisateur.username = username
                utilisateur.email = email
                utilisateur.save()

                messages.success(request, "Entreprise modifiée avec succès.")

        # ACTIVATION
        elif action == 'activer':
            utilisateur.is_active = True
            utilisateur.save(update_fields=['is_active'])
            messages.success(request, "Entreprise activée avec succès.")

        # DÉSACTIVATION
        elif action == 'desactiver':
            utilisateur.is_active = False
            utilisateur.save(update_fields=['is_active'])
            messages.success(request, "Entreprise désactivée avec succès.")

        # SUPPRESSION
        elif action == 'supprimer':
            utilisateur.delete()
            messages.success(request, "Entreprise supprimée avec succès.")

        return redirect('gestion_entreprises')

    # RECHERCHE
    recherche = request.GET.get('recherche', '').strip()

    entreprises = Entreprise.objects.select_related(
        'utilisateur'
    ).order_by('-utilisateur__date_joined')

    if recherche:
        entreprises = entreprises.filter(
            Q(nom_entreprise__icontains=recherche) |
            Q(secteur__icontains=recherche) |
            Q(utilisateur__username__icontains=recherche) |
            Q(utilisateur__email__icontains=recherche)
        )

    context = {
        'entreprises': entreprises,
        'total_entreprises': Entreprise.objects.count(),
        'entreprises_actives': Entreprise.objects.filter(
            utilisateur__is_active=True
        ).count(),
        'entreprises_inactives': Entreprise.objects.filter(
            utilisateur__is_active=False
        ).count(),
        'recherche': recherche,
    }

    return render(
        request,
        'comptes/gestion_entreprises.html',
        context
    )


@login_required
def gestion_offres(request):
    from datetime import date
    from offres.models import Offre

    if request.user.role != 'ADMIN':
        return redirect('accueil')

    if request.method == 'POST':
        offre_id = request.POST.get('offre_id')
        action = request.POST.get('action')

        offre = get_object_or_404(Offre, id=offre_id)

        if action == 'modifier':
            titre = request.POST.get('titre', '').strip()
            description = request.POST.get('description', '').strip()
            type_offre = request.POST.get('type_offre')
            localisation = request.POST.get('localisation', '').strip()
            secteur = request.POST.get('secteur', '').strip()
            date_limite = request.POST.get('date_limite', '')

            try:
                date_valide = date.fromisoformat(date_limite)
            except (ValueError, TypeError):
                date_valide = None

            if not all([titre, description, type_offre,
                        localisation, secteur, date_valide]):
                messages.error(request, "Veuillez remplir correctement tous les champs.")

            elif type_offre not in ['STAGE', 'EMPLOI']:
                messages.error(request, "Type d'offre invalide.")

            else:
                offre.titre = titre
                offre.description = description
                offre.type_offre = type_offre
                offre.localisation = localisation
                offre.secteur = secteur
                offre.date_limite = date_valide
                offre.save()

                messages.success(request, "Offre modifiée avec succès.")

        elif action == 'activer':
            offre.statut = True
            offre.save(update_fields=['statut'])
            messages.success(request, "Offre activée avec succès.")

        elif action == 'desactiver':
            offre.statut = False
            offre.save(update_fields=['statut'])
            messages.success(request, "Offre désactivée avec succès.")

        elif action == 'supprimer':
            offre.delete()
            messages.success(request, "Offre supprimée avec succès.")

        return redirect('gestion_offres')

    recherche = request.GET.get('recherche', '').strip()

    offres = Offre.objects.select_related(
        'entreprise', 'entreprise__utilisateur'
    ).order_by('-date_publication')

    if recherche:
        offres = offres.filter(
            Q(titre__icontains=recherche) |
            Q(description__icontains=recherche) |
            Q(type_offre__icontains=recherche) |
            Q(localisation__icontains=recherche) |
            Q(secteur__icontains=recherche) |
            Q(entreprise__nom_entreprise__icontains=recherche)
        )

    context = {
        'offres': offres,
        'total_offres': Offre.objects.count(),
        'offres_actives': Offre.objects.filter(statut=True).count(),
        'offres_inactives': Offre.objects.filter(statut=False).count(),
        'recherche': recherche,
    }

    return render(request, 'comptes/gestion_offres.html', context)

@login_required
def gestion_candidatures(request):
    if request.user.role != 'ADMIN':
        return redirect('accueil')

    if request.method == 'POST':
        candidature_id = request.POST.get('candidature_id')
        action = request.POST.get('action')
        candidature = get_object_or_404(Candidature, id=candidature_id)

        if action == 'modifier_statut':
            statut = request.POST.get('statut')
            statuts_valides = ['SOUMISE', 'EN_COURS', 'ACCEPTEE', 'REFUSEE']

            if statut in statuts_valides:
                candidature.statut = statut
                candidature.save(update_fields=['statut'])
                messages.success(request, "Statut de la candidature modifié avec succès.")
            else:
                messages.error(request, "Statut invalide.")

        elif action == 'supprimer':
            candidature.delete()
            messages.success(request, "Candidature supprimée avec succès.")

        return redirect('gestion_candidatures')

    recherche = request.GET.get('recherche', '').strip()

    candidatures = Candidature.objects.select_related(
        'etudiant__utilisateur',
        'offre__entreprise'
    ).order_by('-date_candidature')

    if recherche:
        candidatures = candidatures.filter(
            Q(etudiant__utilisateur__username__icontains=recherche) |
            Q(etudiant__utilisateur__first_name__icontains=recherche) |
            Q(etudiant__utilisateur__last_name__icontains=recherche) |
            Q(etudiant__utilisateur__email__icontains=recherche) |
            Q(offre__titre__icontains=recherche) |
            Q(offre__entreprise__nom_entreprise__icontains=recherche)
        )

    context = {
        'candidatures': candidatures,
        'total_candidatures': Candidature.objects.count(),
        'candidatures_soumises': Candidature.objects.filter(statut='SOUMISE').count(),
        'candidatures_en_cours': Candidature.objects.filter(statut='EN_COURS').count(),
        'candidatures_acceptees': Candidature.objects.filter(statut='ACCEPTEE').count(),
        'candidatures_refusees': Candidature.objects.filter(statut='REFUSEE').count(),
        'recherche': recherche,
    }

    return render(request, 'comptes/gestion_candidatures.html', context)

def apropos(request):
    return render(request, 'comptes/apropos.html')