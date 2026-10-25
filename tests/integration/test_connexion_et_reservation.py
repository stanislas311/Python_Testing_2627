import pytest

import server
from tests.utils import texte

EMAIL_JOHN = 'john@simplylift.co'


def club(nom):
    return next(c for c in server.clubs if c['name'] == nom)


def competition(nom):
    return next(c for c in server.competitions if c['name'] == nom)


def reserver(client, nomCompetition, nomClub, places):
    return client.post('/purchasePlaces', data={
        'competition': nomCompetition,
        'club': nomClub,
        'places': places,
    })


# ---------- Connexion ----------

def test_accueil_repond_200(client):
    assert client.get('/').status_code == 200


def test_connexion_email_connu(client):
    reponse = client.post('/showSummary', data={'email': EMAIL_JOHN})
    assert reponse.status_code == 200
    assert 'Welcome, john@simplylift.co' in texte(reponse)


def test_connexion_email_inconnu_affiche_un_message(client):
    reponse = client.post('/showSummary', data={'email': 'inconnu@test.com'})
    assert reponse.status_code == 200
    assert 'cet email est inconnu' in texte(reponse)


def test_connexion_sans_email_ne_plante_pas(client):
    reponse = client.post('/showSummary', data={})
    assert reponse.status_code == 200
    assert 'cet email est inconnu' in texte(reponse)


# ---------- Page de réservation ----------

def test_book_affiche_la_page_de_reservation(client):
    reponse = client.get('/book/Spring%20Festival/Simply%20Lift')
    assert reponse.status_code == 200
    assert 'How many places?' in texte(reponse)


def test_book_competition_inconnue(client):
    reponse = client.get('/book/Inconnue/Simply%20Lift')
    assert 'Compétition introuvable' in texte(reponse)


def test_book_club_inconnu(client):
    reponse = client.get('/book/Spring%20Festival/Inconnu')
    assert 'Club introuvable' in texte(reponse)


def test_book_competition_passee(client):
    reponse = client.get('/book/Winter%20Cup/Simply%20Lift')
    assert "la réservation n'est plus possible" in texte(reponse)


# ---------- Achat de places ----------

def test_reservation_valide_deduit_points_et_places(client):
    reponse = reserver(client, 'Spring Festival', 'Simply Lift', 2)
    assert 'Great-booking complete!' in texte(reponse)
    assert int(club('Simply Lift')['points']) == 11
    assert int(competition('Spring Festival')['numberOfPlaces']) == 23


def test_reservation_refusee_si_points_insuffisants(client):
    reponse = reserver(client, 'Spring Festival', 'Iron Temple', 5)
    assert "pas assez de points" in texte(reponse)
    assert int(club('Iron Temple')['points']) == 4


def test_reservation_refusee_si_pas_assez_de_places(client):
    competition('Fall Classic')['numberOfPlaces'] = 5
    reponse = reserver(client, 'Fall Classic', 'Simply Lift', 6)
    assert "pas assez de places disponibles" in texte(reponse)
    assert int(club('Simply Lift')['points']) == 13


def test_reservation_refusee_au_dela_de_12_places(client):
    reponse = reserver(client, 'Spring Festival', 'Simply Lift', 13)
    assert "plus de 12 places" in texte(reponse)
    assert int(club('Simply Lift')['points']) == 13


def test_limite_de_12_places_cumulee(client):
    reserver(client, 'Spring Festival', 'Simply Lift', 12)
    reponse = reserver(client, 'Spring Festival', 'Simply Lift', 1)
    assert "plus de 12 places" in texte(reponse)
    assert int(club('Simply Lift')['points']) == 1


@pytest.mark.parametrize('saisie', ['', '0', '-5', 'abc'])
def test_reservation_refusee_si_saisie_invalide(client, saisie):
    reponse = reserver(client, 'Spring Festival', 'Simply Lift', saisie)
    assert "nombre de places valide" in texte(reponse)
    assert int(club('Simply Lift')['points']) == 13
    assert int(competition('Spring Festival')['numberOfPlaces']) == 25


def test_reservation_refusee_pour_une_competition_passee(client):
    reponse = reserver(client, 'Winter Cup', 'Simply Lift', 1)
    assert "la réservation n'est plus possible" in texte(reponse)
    assert int(club('Simply Lift')['points']) == 13
