from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.exc import DBAPIError
from ..models import Entry
import datetime
from learning_journal.security import check_credentials
from pyramid.security import remember, forget


@view_config(route_name='home', renderer='../templates/list.jinja2')
def my_view(request):
    try:
        entries = request.dbsession.query(Entry).all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'entries': entries[::-1]}


@view_config(route_name='detail', renderer='../templates/detail.jinja2')
def detail_view(request):
    """The detail view ."""
    the_id = int(request.matchdict["id"])
    entry = request.dbsession.query(Entry).get(the_id)
    return {'entry': entry}


@view_config(route_name='edit', renderer='../templates/edit.jinja2', permission="add")
def edit_view(request):
    """The edit post view."""
    the_id = int(request.matchdict["id"])
    entry = request.dbsession.query(Entry).get(the_id)
    if request.method == "POST":
        entry.title = request.POST["title"]
        entry.body = request.POST["body"]

        request.dbsession.flush()
        return HTTPFound(location=request.route_url('home'))
    return {'data': entry}


@view_config(route_name='create', renderer='../templates/create.jinja2', permission="add")
def create_view(request):
    """The create post view."""
    if request.method == "POST":
        new_title = request.POST["title"]
        new_body = request.POST["body"]
        new_date = datetime.datetime.now()
        new_entry = Entry(title=new_title, body=new_body, creation_date=new_date)

        request.dbsession.add(new_entry)

        return HTTPFound(location=request.route_url('home'))
    return {"data": {"title": "Make a new entry!"}}


@view_config(route_name='login', renderer='../templates/login.jinja2', require_csrf=False) 
def login(request):
    """The login view."""
    if request.method == 'POST':
        username = request.params.get('username', '')
        password = request.params.get('password', '')
        if check_credentials(username, password):
            headers = remember(request, username)
            return HTTPFound(location=request.route_url('home'), headers=headers)
    return {}


@view_config(route_name="logout")
def logout_view(request):
    """The logout view."""
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


@view_config(route_name="api_list", renderer="json")
def api_list_view(request):
    """The conversion to JSON view."""
    entries = request.dbsession.query(Entry).all()
    output = [item.to_json() for item in entries]
    return output


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_learning_journal_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
