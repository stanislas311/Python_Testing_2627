import json

import pytest

import server

SAMPLE_CLUBS = [
    {'name': 'Simply Lift', 'email': 'john@simplylift.co', 'points': '13'},
    {'name': 'Iron Temple', 'email': 'admin@irontemple.com', 'points': '4'},
]

SAMPLE_COMPETITIONS = [
    {
        'name': 'Spring Festival',
        'date': '2026-12-15 10:00:00',
        'numberOfPlaces': '25',
    },
    {
        'name': 'Winter Cup',
        'date': '2026-01-10 09:00:00',
        'numberOfPlaces': '10',
    },
]


@pytest.mark.parametrize(
    ('loader', 'required_fields', 'known_name'),
    [
        (server.loadClubs, {'name', 'email', 'points'}, 'Simply Lift'),
        (
            server.loadCompetitions,
            {'name', 'date', 'numberOfPlaces'},
            'Spring Festival',
        ),
    ],
)
def test_loaders_default_files(loader, required_fields, known_name):
    records = loader()
    assert isinstance(records, list)
    record = next(row for row in records if row['name'] == known_name)
    assert required_fields <= record.keys()


def test_load_clubs_custom_utf8_file(tmp_path):
    fichier = tmp_path / 'clubs.json'
    payload = {'clubs': [{'name': 'Haltéro Élite', 'email': 'a@b.fr'}]}
    fichier.write_text(json.dumps(payload), encoding='utf-8')
    assert server.loadClubs(str(fichier)) == payload['clubs']


def test_load_competitions_empty_list(tmp_path):
    fichier = tmp_path / 'competitions.json'
    fichier.write_text(json.dumps({'competitions': []}), encoding='utf-8')
    assert server.loadCompetitions(str(fichier)) == []


def test_loader_raises_when_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        server.loadClubs(str(tmp_path / 'absent.json'))


def test_loader_raises_when_json_invalid(tmp_path):
    fichier = tmp_path / 'invalid.json'
    fichier.write_text('{not valid json', encoding='utf-8')
    with pytest.raises(json.JSONDecodeError):
        server.loadCompetitions(str(fichier))


def test_loader_raises_when_expected_key_missing(tmp_path):
    fichier = tmp_path / 'wrong_key.json'
    fichier.write_text(json.dumps({'items': []}), encoding='utf-8')
    with pytest.raises(KeyError):
        server.loadClubs(str(fichier))


@pytest.mark.parametrize(
    ('name', 'expected_email'),
    [
        ('Simply Lift', 'john@simplylift.co'),
        ('Iron Temple', 'admin@irontemple.com'),
        ('simply lift', None),
        ('Unknown', None),
        ('', None),
    ],
)
def test_find_club(name, expected_email):
    result = server.find_club(name, SAMPLE_CLUBS)
    if expected_email is None:
        assert result is None
    else:
        assert result['email'] == expected_email


def test_find_club_empty_list():
    assert server.find_club('Simply Lift', []) is None


@pytest.mark.parametrize(
    ('email', 'expected_name'),
    [
        ('john@simplylift.co', 'Simply Lift'),
        ('admin@irontemple.com', 'Iron Temple'),
        ('JOHN@simplylift.co', None),
        ('unknown@test.com', None),
        ('', None),
    ],
)
def test_find_club_by_email(email, expected_name):
    result = server.find_club_by_email(email, SAMPLE_CLUBS)
    if expected_name is None:
        assert result is None
    else:
        assert result['name'] == expected_name


def test_find_club_by_email_empty_list():
    assert server.find_club_by_email('john@simplylift.co', []) is None


@pytest.mark.parametrize(
    ('name', 'expected_places'),
    [
        ('Spring Festival', '25'),
        ('Winter Cup', '10'),
        ('spring festival', None),
        ('Unknown', None),
        ('', None),
    ],
)
def test_find_competition(name, expected_places):
    result = server.find_competition(name, SAMPLE_COMPETITIONS)
    if expected_places is None:
        assert result is None
    else:
        assert result['numberOfPlaces'] == expected_places


def test_find_competition_empty_list():
    assert server.find_competition('Spring Festival', []) is None
