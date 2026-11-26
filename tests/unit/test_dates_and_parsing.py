from datetime import datetime

import pytest

import server

REF_NOW = datetime(2026, 6, 15, 12, 0, 0)


@pytest.mark.parametrize(
    ('comp_date', 'expected'),
    [
        ('2026-06-15 11:59:59', True),
        ('2026-06-15 12:00:00', False),
        ('2026-06-15 12:00:01', False),
        ('2020-01-01 00:00:00', True),
        ('2030-12-31 23:59:59', False),
    ],
)
def test_is_past_with_reference_now(comp_date, expected):
    assert server.is_past({'date': comp_date}, now=REF_NOW) is expected


@pytest.mark.parametrize(
    ('comp_date', 'expected'),
    [
        ('2000-01-01 00:00:00', True),
        ('2999-01-01 10:00:00', False),
    ],
)
def test_is_past_with_default_now(comp_date, expected):
    assert server.is_past({'date': comp_date}) is expected


@pytest.mark.parametrize(
    'bad_date',
    ['', '2026-06-15', '15/06/2026 12:00:00', 'invalid'],
)
def test_is_past_invalid_format_raises(bad_date):
    with pytest.raises(ValueError):
        server.is_past({'date': bad_date}, now=REF_NOW)


@pytest.mark.parametrize(
    ('raw_value', 'expected'),
    [
        ('1', 1),
        ('12', 12),
        (' 5 ', 5),
        (3, 3),
        ('0', 0),
        (0, 0),
        ('-1', -1),
        (-5, -5),
        ('', 0),
        ('   ', 0),
        ('abc', 0),
        ('1.5', 0),
        (None, 0),
        (True, 0),
        (False, 0),
    ],
)
def test_parse_places(raw_value, expected):
    assert server.parse_places(raw_value) == expected
