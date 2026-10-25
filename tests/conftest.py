import copy

import pytest

import server


@pytest.fixture
def client():
    """Client de test Flask avec des données remises à zéro."""
    savedClubs = copy.deepcopy(server.clubs)
    savedCompetitions = copy.deepcopy(server.competitions)
    # Dates fixes pour que les tests ne dépendent pas de la date du jour
    for competition in server.competitions:
        if competition['name'] != 'Winter Cup':
            competition['date'] = '2999-01-01 10:00:00'
    server.bookings.clear()
    server.app.config['TESTING'] = True
    with server.app.test_client() as testClient:
        yield testClient
    server.clubs[:] = savedClubs
    server.competitions[:] = savedCompetitions
    server.bookings.clear()
