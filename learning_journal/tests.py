"""Testing for our learning journal."""


import transaction
import datetime
from pyramid import testing
import pytest
from learning_journal.models import Entry, get_tm_session
from learning_journal.models.meta import Base
import faker

fake = faker.Faker()

ENTRIES = [Entry(
    title=fake.catch_phrase(),
    creation_date="Jan 12 2017",
    body=fake.text(100),
) for i in range(10)]


@pytest.fixture(scope="session")
def configuration(request):
    """Fixture of Configuration and setup of testing db."""
    settings = {'sqlalchemy.url': 'postgres://colinlamont@localhost:5432/testing_db'}
    config = testing.setUp(settings=settings)
    config.include('learning_journal.models')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture(scope="session")
def dbsession(configuration, request):
    """A session of a test database."""
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
    """A dummy session."""
    return testing.DummyRequest(dbsession=dbsession)


@pytest.fixture
def add_models(dummy_request):
    """Adding the faker data to the testing database."""
    dummy_request.dbsession.add_all(ENTRIES)


@pytest.fixture
def testapp(request):
    """The test app of our learning journal."""
    from webtest import TestApp
    from pyramid.config import Configurator

    def main(global_config, **settings):
        """The function returns a Pyramid WSGI application."""
        settings = {'sqlalchemy.url': 'postgres://colinlamont@localhost:5432/testing_db'}
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('.models')
        config.include('.routes')
        config.include('.security')
        config.scan()
        return config.make_wsgi_app()

    app = main({}, **{})
    testapp = TestApp(app)

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind

    Base.metadata.create_all(bind=engine)

    def tear_down():
        Base.metadata.drop_all(bind=engine)

    request.addfinalizer(tear_down)

    return testapp


@pytest.fixture
def fill_the_db(testapp):
    """Filling the test db."""
    SessionFactory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(SessionFactory, transaction.manager)
        dbsession.add_all(ENTRIES)


@pytest.fixture
def set_authentications_credentials():
    """Create fake authentication username and pword for testing."""
    import os
    from passlib.apps import custom_app_context as pwd_context

    os.environ["AUTH_USERNAME"] = "testname"
    os.environ["AUTH_PASSWORD"] = pwd_context.hash("testpass")


def test_home_route_has_an_title(testapp):
    """The home page has an title tag."""
    response = testapp.get('/', status=200)
    html = response.html
    assert html.find_all("title")


def test_detail_route_has_no_information(testapp):
    """No infomation when not logged in."""
    response = testapp.get("/journal/7", status=404)
    assert response.status_code == 404

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

def test_new_entries_are_added_to_db(dbsession):
    """Testing this ."""
    dbsession.add_all(ENTRIES)
    query = dbsession.query(Entry).all()
    assert len(query) == len(ENTRIES)


def test_home_route_with_entries_has_h5(testapp, fill_the_db):
    """When there's data in the database, the home page has some H5 tags."""
    response = testapp.get('/', status=200)
    html = response.html
    assert len(html.find_all("h5")) == 10


def test_detail_route_has_some_information(testapp):
    """Foo."""
    response = testapp.get("/journal/4")
    assert "2017" in response.text

# ======== TESTING WITH SECURITY ==========


def test_create_route_is_forbidden(testapp):
    """No login, no access to the create view."""
    response = testapp.get("/create", status=403)
    assert response.status_code == 403


def test_app_can_log_in_and_be_authed(set_authentication_credentials, testapp):
    """Test you can login to site."""
    testapp.post("/login", params={
        "username": "testname",
        "password": "testpass"
    })
    assert "auth_tkt" in testapp.cookies


def test_authenticated_user_can_see_create_route(testapp):
    """Test if an authenticated user can get to the create view."""
    response = testapp.get("/create")
    assert response.status_code == 200


def test_authenticated_user_can_create_new_post(testapp):
    """Test a logged in user can create a new post."""
    response = testapp.get("/create")
    csrf_token = response.html.find(
        "input",
        {"name": "csrf_token"}).attrs["value"]

    testapp.post("/create", params={
        "csrf_token": csrf_token,
        "title": "New Title",
        "body": "some text",
        "creation_date": "2017-01-06",
    })

    response = testapp.get("/")
    assert "New Title" in response.text


def test_logout_removes_authentication(testapp):
    """Test that if you logout, you are no longer authenticated."""
    testapp.get("/logout")
    assert "auth_tkt" not in testapp.cookies


def test_login_button_now_present_on_homepage(testapp):
    """Test the login button is on home page if logged out."""
    response = testapp.get("/")
    assert "Login" in response.text


def test_edit_view_is_forbidden_again(testapp):
    """Test edit view is not allowed when logged out."""
    response = testapp.get("/journal/7/edit", status=403)
    assert response.status_code == 403
