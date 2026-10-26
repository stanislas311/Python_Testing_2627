from tests.utils import annuler, club, competition, reserver, texte


EMAIL_JOHN = 'john@simplylift.co'


def test_parcours_complet_secretaire(client):
    connexion = client.post('/showSummary', data={'email': EMAIL_JOHN})
    assert 'Welcome, john@simplylift.co' in texte(connexion)

    reservation = reserver(client, 'Spring Festival', 'Simply Lift', 2)
    assert 'Great-booking complete!' in texte(reservation)
    assert int(club('Simply Lift')['points']) == 11
    assert int(competition('Spring Festival')['numberOfPlaces']) == 23

    historique = texte(client.get(
        '/mesReservations', query_string={'club': 'Simply Lift'}))
    assert 'Mes réservations' in historique
    assert 'Total : <strong>2</strong>' in historique

    annulation = annuler(
        client, 'Spring Festival', 'Simply Lift', 1)
    assert 'Annulation effectuée : 1 place(s) rendue(s).' in annulation

    tableau = texte(client.get('/points'))
    simply_lift = tableau.index('Simply Lift')
    assert '<td>12</td>' in tableau[simply_lift:]

    deconnexion = client.get('/logout')
    assert deconnexion.status_code == 302
    assert deconnexion.headers['Location'].endswith('/')


def test_parcours_erreur_email_inconnu_et_trop_de_places(client):
    connexion = client.post(
        '/showSummary', data={'email': 'inconnu@example.com'})
    assert 'cet email est inconnu' in texte(connexion)

    reservation = reserver(client, 'Spring Festival', 'Simply Lift', 13)
    assert 'plus de 12 places' in texte(reservation)
    assert int(club('Simply Lift')['points']) == 13
    assert int(competition('Spring Festival')['numberOfPlaces']) == 25
