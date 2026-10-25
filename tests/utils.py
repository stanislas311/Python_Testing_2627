import html

import server


def texte(response):
    """Retourne le contenu HTML décodé (accents et apostrophes lisibles)."""
    return html.unescape(response.data.decode('utf-8'))


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


def annuler(client, nomCompetition, nomClub, places):
    """Annule des places et suit la redirection vers « Mes réservations »."""
    reponse = client.post('/annulerReservation', data={
        'competition': nomCompetition,
        'club': nomClub,
        'places': places,
    }, follow_redirects=True)
    return texte(reponse)
