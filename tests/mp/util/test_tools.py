import pytest
from assertpy import assert_that

from mp.util.tools import DatabaseUrlType

sqlite_testdata = [
    ('sqlite:foo/bar', 'foo/bar'),
    ('sqlite:/foo/bar', 'foo/bar'),
    ('sqlite:///foo/bar', 'foo/bar'),
    ('sqlite:////foo/bar', '/foo/bar'),
    ('sqlite::memory:', ':memory:'),
]


@pytest.mark.parametrize('input,expected', sqlite_testdata)
def test_parse_sqlite_url(input, expected):
    under_test = DatabaseUrlType()
    actual = under_test.convert(input, None, None)
    assert expected == actual['dbname']
    assert input == actual['url']
    assert 'sqlite' == actual['dbtype']
    assert actual['hostname'] is None
    assert actual['port'] is None
    assert actual['username'] is None
    assert actual['password'] is None


postgres_testdata = [
    (
        'postgresql://postgres:postgres@localhost:5432/postgres',
        {
            'url': 'postgresql://postgres:postgres@localhost:5432/postgres',
            'dbtype': 'postgresql',
            'username': 'postgres',
            'password': 'postgres',
            'hostname': 'localhost',
            'port': 5432,
            'dbname': 'postgres',
        },
    ),
    (
        'postgresql:database',
        {
            'url': 'postgresql:database',
            'dbtype': 'postgresql',
            'username': None,
            'password': None,
            'hostname': None,
            'port': None,
            'dbname': 'database',
        },
    ),
    (
        'postgresql://host/database',
        {
            'url': 'postgresql://host/database',
            'dbtype': 'postgresql',
            'username': None,
            'password': None,
            'hostname': 'host',
            'port': None,
            'dbname': 'database',
        },
    ),
    (
        'postgresql://host:1234/database',
        {
            'url': 'postgresql://host:1234/database',
            'dbtype': 'postgresql',
            'username': None,
            'password': None,
            'hostname': 'host',
            'port': 1234,
            'dbname': 'database',
        },
    ),
]


@pytest.mark.parametrize('input, expected', postgres_testdata)
def test_parse_postgres_url(input, expected):
    under_test = DatabaseUrlType()
    actual = under_test.convert(input, None, None)
    assert_that(expected).is_equal_to(actual)
