import pytest

import server

COMPETITIONS = [
    {'name': 'Spring Festival', 'date': '2026-12-15 10:00:00'},
    {'name': 'Fall Classic', 'date': '2027-02-20 13:30:00'},
    {'name': 'Winter Cup', 'date': '2026-01-10 09:00:00'},
]


def test_compute_ranking_empty_list():
    assert server.compute_ranking([]) == []


def test_compute_ranking_single_club():
    clubs = [{'name': 'Solo', 'points': '7'}]
    assert server.compute_ranking(clubs) == [
        {'rank': 1, 'name': 'Solo', 'points': 7},
    ]


def test_compute_ranking_strictly_descending():
    clubs = [
        {'name': 'Low', 'points': '4'},
        {'name': 'High', 'points': 20},
        {'name': 'Mid', 'points': '12'},
    ]
    assert server.compute_ranking(clubs) == [
        {'rank': 1, 'name': 'High', 'points': 20},
        {'rank': 2, 'name': 'Mid', 'points': 12},
        {'rank': 3, 'name': 'Low', 'points': 4},
    ]


def test_compute_ranking_ties_at_top():
    clubs = [
        {'name': 'Club B', 'points': '4'},
        {'name': 'Club A', 'points': '13'},
        {'name': 'Club C', 'points': 13},
    ]
    assert server.compute_ranking(clubs) == [
        {'rank': 1, 'name': 'Club A', 'points': 13},
        {'rank': 1, 'name': 'Club C', 'points': 13},
        {'rank': 3, 'name': 'Club B', 'points': 4},
    ]


def test_compute_ranking_ties_in_middle():
    clubs = [
        {'name': 'D', 'points': '2'},
        {'name': 'A', 'points': '20'},
        {'name': 'B', 'points': '10'},
        {'name': 'C', 'points': '10'},
    ]
    assert server.compute_ranking(clubs) == [
        {'rank': 1, 'name': 'A', 'points': 20},
        {'rank': 2, 'name': 'B', 'points': 10},
        {'rank': 2, 'name': 'C', 'points': 10},
        {'rank': 4, 'name': 'D', 'points': 2},
    ]


def test_compute_ranking_all_tied_zero_points():
    clubs = [
        {'name': 'A', 'points': '0'},
        {'name': 'B', 'points': 0},
    ]
    assert server.compute_ranking(clubs) == [
        {'rank': 1, 'name': 'A', 'points': 0},
        {'rank': 1, 'name': 'B', 'points': 0},
    ]


def test_compute_ranking_with_negative_points_and_bottom_tie():
    clubs = [
        {'name': 'C', 'points': '-2'},
        {'name': 'A', 'points': '10'},
        {'name': 'D', 'points': -2},
        {'name': 'B', 'points': '5'},
    ]
    assert server.compute_ranking(clubs) == [
        {'rank': 1, 'name': 'A', 'points': 10},
        {'rank': 2, 'name': 'B', 'points': 5},
        {'rank': 3, 'name': 'C', 'points': -2},
        {'rank': 3, 'name': 'D', 'points': -2},
    ]


def test_compute_ranking_does_not_mutate_input():
    clubs = [
        {'name': 'B', 'points': '4'},
        {'name': 'A', 'points': '13'},
    ]
    snapshot = [c.copy() for c in clubs]
    server.compute_ranking(clubs)
    assert clubs == snapshot


@pytest.mark.parametrize(
    ('term', 'expected_names'),
    [
        ('', ['Spring Festival', 'Fall Classic', 'Winter Cup']),
        ('   ', ['Spring Festival', 'Fall Classic', 'Winter Cup']),
        (None, ['Spring Festival', 'Fall Classic', 'Winter Cup']),
        ('Spring Festival', ['Spring Festival']),
        ('spring', ['Spring Festival']),
        ('FALL', ['Fall Classic']),
        ('  cup  ', ['Winter Cup']),
        ('c', ['Fall Classic', 'Winter Cup']),
        ('xyz', []),
    ],
)
def test_filter_competitions(term, expected_names):
    results = server.filter_competitions(term, COMPETITIONS)
    assert [c['name'] for c in results] == expected_names


def test_filter_competitions_empty_source():
    assert server.filter_competitions('spring', []) == []


def test_filter_competitions_returns_new_list():
    results = server.filter_competitions('', COMPETITIONS)
    assert results is not COMPETITIONS
