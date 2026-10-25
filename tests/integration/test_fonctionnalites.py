import pytest

import server
from tests.utils import annuler, club, competition, reserver, texte

EMAIL_JOHN = 'john@simplylift.co'


# ---------- Page du club et déconnexion ----------

def test_logout_redirige_vers_l_accueil(client):
    reponse = client.get('/logout')
    assert reponse.status_code == 302
    assert reponse.headers['Location'].endswith('/')


def test_page_club_affiche_les_badges_de_statut(client):
    page = texte(client.post('/showSummary', data={'email': EMAIL_JOHN}))
    assert 'Places disponibles' in page
    assert 'Compétition terminée' in page


def test_page_club_badges_complet_et_dernieres_places(client):
    competition('Spring Festival')['numberOfPlaces'] = 0
    competition('Fall Classic')['numberOfPlaces'] = 3
    page = texte(client.post('/showSummary', data={'email': EMAIL_JOHN}))
    assert 'Complet' in page
    assert 'Dernières places' in page


# ---------- Tableau des points ----------

def test_tableau_des_points_est_public(client):
    assert client.get('/points').status_code == 200


def test_tableau_trie_par_points_decroissants(client):
    page = texte(client.get('/points'))
    simply = page.index('Simply Lift')
    she = page.index('She Lifts')
    iron = page.index('Iron Temple')
    assert simply < she < iron


def test_tableau_ex_aequo_ont_le_meme_rang(client):
    club('Iron Temple')['points'] = 13
    page = texte(client.get('/points'))
    assert page.count('<td>1</td>') == 2
    assert page.count('<td>3</td>') == 1


def test_tableau_marque_le_club_connecte(client):
    page = texte(client.get('/points', query_string={'club': 'She Lifts'}))
    assert 'She Lifts (vous)' in page
    assert 'Simply Lift (vous)' not in page


def test_tableau_sans_club_ne_marque_personne(client):
    assert '(vous)' not in texte(client.get('/points'))


# ---------- Recherche de compétitions ----------

def rechercher(client, nomClub, terme):
    reponse = client.get(
        '/rechercher', query_string={'club': nomClub, 'q': terme})
    return texte(reponse)


def test_recherche_filtre_par_nom(client):
    page = rechercher(client, 'Simply Lift', 'spring')
    assert 'Spring Festival' in page
    assert 'Fall Classic' not in page
    assert 'Winter Cup' not in page


def test_recherche_ignore_la_casse(client):
    page = rechercher(client, 'Simply Lift', 'FALL')
    assert 'Fall Classic' in page
    assert 'Spring Festival' not in page


def test_recherche_sans_resultat(client):
    page = rechercher(client, 'Simply Lift', 'xyz')
    assert 'Aucune compétition ne correspond' in page
    assert 'Spring Festival' not in page


def test_recherche_club_inconnu(client):
    assert 'Club introuvable' in rechercher(client, 'Inconnu', 'spring')


def test_recherche_vide_affiche_toutes_les_competitions(client):
    page = rechercher(client, 'Simply Lift', '')
    assert 'Spring Festival' in page
    assert 'Fall Classic' in page
    assert 'Winter Cup' in page


# ---------- Historique des réservations ----------

def historique(client, nomClub):
    reponse = client.get('/mesReservations', query_string={'club': nomClub})
    return texte(reponse)


def test_historique_vide_au_depart(client):
    page = historique(client, 'Simply Lift')
    assert 'Aucune réservation pour le moment' in page


def test_historique_affiche_les_reservations_du_club(client):
    reserver(client, 'Spring Festival', 'Simply Lift', 2)
    reserver(client, 'Fall Classic', 'Simply Lift', 3)
    reserver(client, 'Spring Festival', 'Simply Lift', 1)
    page = historique(client, 'Simply Lift')
    assert 'Spring Festival' in page
    assert 'Fall Classic' in page
    assert 'Total : <strong>6</strong>' in page


def test_historique_ne_montre_pas_les_reservations_des_autres_clubs(client):
    reserver(client, 'Spring Festival', 'Simply Lift', 2)
    page = historique(client, 'She Lifts')
    assert 'Aucune réservation pour le moment' in page


def test_historique_club_inconnu(client):
    assert 'Club introuvable' in historique(client, 'Inconnu')


def test_historique_competition_terminee_non_annulable(client):
    server.bookings[('Winter Cup', 'Simply Lift')] = 2
    page = historique(client, 'Simply Lift')
    assert 'Terminée' in page
    assert 'Non annulable' in page


# ---------- Annulation ----------

def test_annulation_rend_points_et_places(client):
    reserver(client, 'Spring Festival', 'Simply Lift', 3)
    page = annuler(client, 'Spring Festival', 'Simply Lift', 2)
    assert 'Annulation effectuée : 2 place(s) rendue(s).' in page
    assert int(club('Simply Lift')['points']) == 12
    assert int(competition('Spring Festival')['numberOfPlaces']) == 24
    assert server.bookings[('Spring Festival', 'Simply Lift')] == 1


def test_annulation_totale_supprime_la_ligne(client):
    reserver(client, 'Spring Festival', 'Simply Lift', 2)
    page = annuler(client, 'Spring Festival', 'Simply Lift', 2)
    assert 'Aucune réservation pour le moment' in page
    assert int(club('Simply Lift')['points']) == 13


def test_annulation_refusee_si_plus_que_reserve(client):
    reserver(client, 'Spring Festival', 'Simply Lift', 2)
    page = annuler(client, 'Spring Festival', 'Simply Lift', 3)
    assert "plus de places que vous n'en avez réservé" in page
    assert int(club('Simply Lift')['points']) == 11
    assert server.bookings[('Spring Festival', 'Simply Lift')] == 2


def test_annulation_refusee_pour_une_competition_passee(client):
    server.bookings[('Winter Cup', 'Simply Lift')] = 2
    page = annuler(client, 'Winter Cup', 'Simply Lift', 1)
    assert "l'annulation n'est plus possible" in page
    assert int(club('Simply Lift')['points']) == 13
    assert server.bookings[('Winter Cup', 'Simply Lift')] == 2


@pytest.mark.parametrize('saisie', ['', '0', '-1', 'abc'])
def test_annulation_refusee_si_saisie_invalide(client, saisie):
    reserver(client, 'Spring Festival', 'Simply Lift', 2)
    page = annuler(client, 'Spring Festival', 'Simply Lift', saisie)
    assert 'nombre de places valide' in page
    assert int(club('Simply Lift')['points']) == 11


def test_annulation_club_inconnu(client):
    page = annuler(client, 'Spring Festival', 'Inconnu', 1)
    assert 'Club introuvable' in page


def test_annulation_competition_inconnue(client):
    page = annuler(client, 'Inconnue', 'Simply Lift', 1)
    assert 'Compétition introuvable' in page


def test_annulation_libere_la_limite_de_12_places(client):
    reserver(client, 'Spring Festival', 'Simply Lift', 12)
    annuler(client, 'Spring Festival', 'Simply Lift', 5)
    page = texte(reserver(client, 'Spring Festival', 'Simply Lift', 5))
    assert 'Great-booking complete!' in page
    page = texte(reserver(client, 'Spring Festival', 'Simply Lift', 1))
    assert 'plus de 12 places' in page
