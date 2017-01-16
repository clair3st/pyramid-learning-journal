"""Testing for our learning journal."""


import unittest
import transaction
import random
import datetime

from pyramid import testing
import pytest
from learning_journal.models import Entry, get_tm_session
from learning_journal.models.meta import Base
import faker

fake = faker.Faker()

ENTRIES = [Entry(
    title=fake.catch_phrase(),
    creation_date=datetime.datetime.now(),
    body=fake.text(100),
) for i in range(10)]



@pytest.fixture(scope="session")
def configuration(request):
    settings = {'sqlalchemy.url': 'postgres://colinlamont@localhost:5432/testing_db'}
    config = testing.setUp(settings=settings)
    config.include('learning_journal.models')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture()
def dbsession(configuration, request):
    SessionFactory = configuration.registry['dbsession_factory']
    session = SessionFactory()
    engine = session.bind
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def teardown():
        session.transaction.rollback()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)

@pytest.fixture
def add_models(dummy_request):
    dummy_request.dbsession.add_all(ENTRIES)


@pytest.fixture
def testapp():
    from webtest import TestApp
    from pyramid.config import Configurator

    def main(global_config, **settings):
        """ The function returns a Pyramid WSGI application.
        """
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('.models')
        config.include('.routes')
        config.include('.security')
        config.scan()
        return config.make_wsgi_app()

    app = main({}, **{"sqlalchemy.url": 'postgres://colinlamont@localhost:5432/testing_db'})
    testapp = TestApp(app)

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.create_all(bind=engine)
    return testapp


@pytest.fixture
def fill_the_db(testapp):
    SessionFactory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(SessionFactory, transaction.manager)
        dbsession.add_all(Entry)

def test_home_route_has_an_title(testapp):
    """The home page has an title tag."""
    response = testapp.get('/', status=200)
    html = response.html
    assert html.find_all("title")


# def test_home_route_with_data_has_filled_table(testapp, fill_the_db):
#     """When there's data in the database, the home page has rows."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert len(html.find_all("tr")) == 101


# def test_home_route_has_table2(testapp):
#     """The home page has a table with no rows."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert len(html.find_all("tr")) == 1

def test_db(dbsession):
    """Testing this stuff."""
    dbsession.add_all(ENTRIES)
    query = dbsession.query(Entry).all()
    assert len(query) == len(ENTRIES)
