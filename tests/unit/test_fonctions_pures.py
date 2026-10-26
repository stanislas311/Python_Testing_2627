import pytest

import server


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('2', 2),
        ('0', 0),
        ('-3', -3),
        ('', 0),
        ('abc', 0),
    ],
)
def test_parse_places(value, expected):
    assert server.parse_places(value) == expected


@pytest.mark.parametrize(
    ('clubs', 'expected'),
    [
        (
            [
                {'name': 'Iron Temple', 'points': '4'},
                {'name': 'Simply Lift', 'points': '13'},
                {'name': 'She Lifts', 'points': 13},
            ],
            [
                {'rank': 1, 'name': 'Simply Lift', 'points': 13},
                {'rank': 1, 'name': 'She Lifts', 'points': 13},
                {'rank': 3, 'name': 'Iron Temple', 'points': 4},
            ],
        ),
        ([], []),
    ],
)
def test_compute_ranking(clubs, expected):
    original = [club.copy() for club in clubs]
    assert server.compute_ranking(clubs) == expected
    assert clubs == original


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
def test_loaders_return_expected_records(loader, required_fields, known_name):
    records = loader()
    assert isinstance(records, list)
    record = next(row for row in records if row['name'] == known_name)
    assert required_fields <= record.keys()


@pytest.mark.parametrize(
    ('date', 'expected'),
    [
        ('2020-01-01 10:00:00', True),
        ('2999-01-01 10:00:00', False),
    ],
)
def test_is_past_for_past_and_future_dates(date, expected):
    assert server.is_past({'date': date}) is expected
