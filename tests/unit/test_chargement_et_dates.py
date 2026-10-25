from server import is_past, loadClubs, loadCompetitions


def test_load_clubs_retourne_les_clubs():
    clubs = loadClubs()
    assert isinstance(clubs, list)
    assert any(c['email'] == 'john@simplylift.co' for c in clubs)


def test_load_competitions_retourne_les_competitions():
    competitions = loadCompetitions()
    assert len(competitions) >= 1
    assert all('name' in c and 'date' in c for c in competitions)


def test_is_past_vrai_pour_une_date_passee():
    assert is_past({'date': '2020-01-01 10:00:00'}) is True


def test_is_past_faux_pour_une_date_future():
    assert is_past({'date': '2999-01-01 10:00:00'}) is False
