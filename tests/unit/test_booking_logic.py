from datetime import datetime

import pytest

import server

NOW = datetime(2026, 6, 15, 12, 0, 0)
FUTURE_DATE = '2026-12-15 10:00:00'
PAST_DATE = '2026-01-10 09:00:00'


def make_club(name='Simply Lift', points='13'):
    return {'name': name, 'email': 'club@test.co', 'points': points}


def make_comp(name='Spring Festival', places='25', date=FUTURE_DATE):
    return {'name': name, 'date': date, 'numberOfPlaces': places}


# ---------- book_places ----------

def test_book_places_success_updates_state():
    club = make_club(points='13')
    comp = make_comp(places='25')
    store = {}
    ok, msg = server.book_places(club, comp, 4, bookings_store=store, now=NOW)
    assert ok is True
    assert msg == server.MSG_RESERVATION_REUSSIE
    assert club['points'] == 9
    assert comp['numberOfPlaces'] == 21
    assert store[(comp['name'], club['name'])] == 4


@pytest.mark.parametrize(
    ('points', 'comp_places', 'requested', 'already'),
    [
        (5, 10, 5, 0),
        (10, 4, 4, 0),
        (15, 20, 12, 0),
        (15, 20, 4, 8),
    ],
)
def test_book_places_exact_boundaries_succeed(
    points, comp_places, requested, already
):
    club = make_club(points=points)
    comp = make_comp(places=comp_places)
    key = (comp['name'], club['name'])
    store = {key: already} if already else {}
    ok, _ = server.book_places(
        club, comp, requested, bookings_store=store, now=NOW
    )
    assert ok is True
    assert club['points'] == points - requested
    assert comp['numberOfPlaces'] == comp_places - requested
    assert store[key] == already + requested


def test_book_places_refused_when_competition_past():
    club = make_club(points=10)
    comp = make_comp(places=10, date=PAST_DATE)
    store = {}
    ok, msg = server.book_places(club, comp, 1, bookings_store=store, now=NOW)
    assert ok is False
    assert msg == server.MSG_RESERVATION_TERMINEE
    assert club['points'] == 10
    assert comp['numberOfPlaces'] == 10
    assert store == {}


@pytest.mark.parametrize('places', [0, -1, -10])
def test_book_places_refused_when_non_positive(places):
    club = make_club(points=10)
    comp = make_comp(places=10)
    store = {}
    ok, msg = server.book_places(
        club, comp, places, bookings_store=store, now=NOW
    )
    assert ok is False
    assert msg == server.MSG_PLACES_INVALIDES
    assert club['points'] == 10
    assert comp['numberOfPlaces'] == 10
    assert store == {}


def test_book_places_refused_when_insufficient_points():
    club = make_club(points='4')
    comp = make_comp(places='25')
    store = {}
    ok, msg = server.book_places(club, comp, 5, bookings_store=store, now=NOW)
    assert ok is False
    assert msg == server.MSG_POINTS_INSUFFISANTS
    assert club['points'] == '4'
    assert comp['numberOfPlaces'] == '25'
    assert store == {}


def test_book_places_refused_when_insufficient_competition_places():
    club = make_club(points='13')
    comp = make_comp(places='3')
    store = {}
    ok, msg = server.book_places(club, comp, 4, bookings_store=store, now=NOW)
    assert ok is False
    assert msg == server.MSG_PLACES_INSUFFISANTES
    assert club['points'] == '13'
    assert comp['numberOfPlaces'] == '3'
    assert store == {}


@pytest.mark.parametrize(
    ('already', 'requested'),
    [(0, 13), (10, 3), (12, 1)],
)
def test_book_places_refused_when_exceeding_max_limit(already, requested):
    club = make_club(points=20)
    comp = make_comp(places=30)
    key = (comp['name'], club['name'])
    store = {key: already} if already else {}
    ok, msg = server.book_places(
        club, comp, requested, bookings_store=store, now=NOW
    )
    assert ok is False
    assert msg == server.MSG_LIMITE_PLACES
    assert club['points'] == 20
    assert comp['numberOfPlaces'] == 30
    assert store.get(key, 0) == already


def test_book_places_limit_is_per_club_and_competition():
    club_a = make_club(name='Club A', points=24)
    club_b = make_club(name='Club B', points=15)
    comp_1 = make_comp(name='Comp 1', places=30)
    comp_2 = make_comp(name='Comp 2', places=30)
    store = {}
    assert server.book_places(
        club_a, comp_1, 12, bookings_store=store, now=NOW
    )[0] is True
    assert server.book_places(
        club_a, comp_2, 12, bookings_store=store, now=NOW
    )[0] is True
    assert server.book_places(
        club_b, comp_1, 12, bookings_store=store, now=NOW
    )[0] is True


@pytest.mark.parametrize(
    ('requested', 'expected_ok'),
    [(5, True), (6, False)],
)
def test_book_places_custom_max_places(requested, expected_ok):
    club = make_club(points=10)
    comp = make_comp(places=20)
    ok, _ = server.book_places(
        club, comp, requested, bookings_store={}, max_places=5, now=NOW
    )
    assert ok is expected_ok


def test_book_places_preserves_other_club_bookings():
    club_a = make_club(name='Club A', points=10)
    comp = make_comp(name='Spring', places=20)
    store = {('Spring', 'Club B'): 7}
    ok, _ = server.book_places(
        club_a, comp, 3, bookings_store=store, now=NOW
    )
    assert ok is True
    assert store == {('Spring', 'Club B'): 7, ('Spring', 'Club A'): 3}


# ---------- get_club_reservations ----------

def test_get_club_reservations_empty():
    reservations, total = server.get_club_reservations(
        'Simply Lift', bookings_store={}, competitions_list=[], now=NOW
    )
    assert reservations == []
    assert total == 0


def test_get_club_reservations_filters_and_computes_total():
    comps = [
        make_comp(name='Spring', places=20, date=FUTURE_DATE),
        make_comp(name='Winter', places=10, date=PAST_DATE),
    ]
    store = {
        ('Spring', 'Simply Lift'): 3,
        ('Winter', 'Simply Lift'): 2,
        ('Spring', 'Other Club'): 5,
        ('Fall', 'Simply Lift'): 0,
        ('Missing Comp', 'Simply Lift'): 4,
    }
    reservations, total = server.get_club_reservations(
        'Simply Lift', bookings_store=store, competitions_list=comps, now=NOW
    )
    assert reservations == [
        {
            'competition': 'Spring',
            'date': FUTURE_DATE,
            'places': 3,
            'past': False,
        },
        {
            'competition': 'Winter',
            'date': PAST_DATE,
            'places': 2,
            'past': True,
        },
    ]
    assert total == 5


# ---------- cancel_places ----------

def test_cancel_places_partial_updates_state():
    club = make_club(points=10)
    comp = make_comp(places=20)
    key = (comp['name'], club['name'])
    store = {key: 5}
    ok, msg = server.cancel_places(
        club, comp, 2, bookings_store=store, now=NOW
    )
    assert ok is True
    assert msg == 'Annulation effectuée : 2 place(s) rendue(s).'
    assert club['points'] == 12
    assert comp['numberOfPlaces'] == 22
    assert store[key] == 3


def test_cancel_places_full_removes_booking_entry():
    club = make_club(points=10)
    comp = make_comp(places=20)
    key = (comp['name'], club['name'])
    store = {key: 4}
    ok, msg = server.cancel_places(
        club, comp, 4, bookings_store=store, now=NOW
    )
    assert ok is True
    assert msg == 'Annulation effectuée : 4 place(s) rendue(s).'
    assert club['points'] == 14
    assert comp['numberOfPlaces'] == 24
    assert key not in store


def test_cancel_places_frees_allowance_for_rebooking():
    club = make_club(points=20)
    comp = make_comp(places=30)
    store = {}
    assert server.book_places(
        club, comp, 12, bookings_store=store, now=NOW
    )[0] is True
    assert server.cancel_places(
        club, comp, 5, bookings_store=store, now=NOW
    )[0] is True
    assert server.book_places(
        club, comp, 5, bookings_store=store, now=NOW
    )[0] is True
    assert server.book_places(
        club, comp, 1, bookings_store=store, now=NOW
    )[0] is False


def test_cancel_places_refused_when_competition_past():
    club = make_club(points=10)
    comp = make_comp(places=10, date=PAST_DATE)
    key = (comp['name'], club['name'])
    store = {key: 2}
    ok, msg = server.cancel_places(
        club, comp, 1, bookings_store=store, now=NOW
    )
    assert ok is False
    assert msg == server.MSG_ANNULATION_TERMINEE
    assert club['points'] == 10
    assert comp['numberOfPlaces'] == 10
    assert store[key] == 2


@pytest.mark.parametrize('places', [0, -1, -5])
def test_cancel_places_refused_when_non_positive(places):
    club = make_club(points=10)
    comp = make_comp(places=20)
    key = (comp['name'], club['name'])
    store = {key: 3}
    ok, msg = server.cancel_places(
        club, comp, places, bookings_store=store, now=NOW
    )
    assert ok is False
    assert msg == server.MSG_PLACES_INVALIDES
    assert club['points'] == 10
    assert comp['numberOfPlaces'] == 20
    assert store[key] == 3


@pytest.mark.parametrize(
    ('booked', 'to_cancel'),
    [(0, 1), (2, 3), (5, 10)],
)
def test_cancel_places_refused_when_more_than_booked(booked, to_cancel):
    club = make_club(points=10)
    comp = make_comp(places=20)
    key = (comp['name'], club['name'])
    store = {key: booked} if booked else {}
    ok, msg = server.cancel_places(
        club, comp, to_cancel, bookings_store=store, now=NOW
    )
    assert ok is False
    assert msg == server.MSG_ANNULATION_TROP_DE_PLACES
    assert club['points'] == 10
    assert comp['numberOfPlaces'] == 20
    assert store.get(key, 0) == booked


def test_cancel_places_preserves_other_club_bookings():
    club_a = make_club(name='Club A', points=10)
    comp = make_comp(name='Spring', places=20)
    store = {('Spring', 'Club A'): 2, ('Spring', 'Club B'): 5}
    ok, _ = server.cancel_places(
        club_a, comp, 2, bookings_store=store, now=NOW
    )
    assert ok is True
    assert store == {('Spring', 'Club B'): 5}


def test_get_club_reservations_ignores_other_clubs_only():
    comps = [make_comp(name='Spring', places=20, date=FUTURE_DATE)]
    store = {('Spring', 'Other Club'): 4}
    reservations, total = server.get_club_reservations(
        'Simply Lift', bookings_store=store, competitions_list=comps, now=NOW
    )
    assert reservations == []
    assert total == 0
