import markdown
import PyRSS2Gen
import datetime
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc
from .models import (
    DBSession,
    Post,
    )


#@view_config(route_name='home', renderer='templates/mytemplate.pt')
#def my_view(request):
    #try:
        #one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    #except DBAPIError:
        #return Response(conn_err_msg, content_type='text/plain', status_int=500)
    #return {'one': one, 'project': 'myblog'}


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_myblog_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


@view_config(route_name = 'rss')
def render_rss_feed(request):
    posts = DBSession.query(Post).order_by(desc(Post.created)).all()
    items= []
    for post in posts[:10]:
        title = post.name
        link = request.route_url('view_post', postname = title)
        description = post.markdown[:200]
        #guid = PyRSS2Gen.Guid('')
        pub_date = post.created

        item = PyRSS2Gen.RSSItem(title = title,
                    link= link, description= description,
                    #guid= guid,
                    pubDate = pub_date)

        items.append(item)

    rss = PyRSS2Gen.RSS2(
        title = "Not the Answer",
        link = "https://blog.ismail-s.com",
        description = "A personal blog about science, computers and life.",

        lastBuildDate = datetime.datetime.utcnow(),

        items = items)
    # maybe write the file into the static folder and remake it whenever a post is modified...
    return Response(rss.to_xml(), content_type = 'application/xml')

#@view_config(renderer = 'templates/home.mako')
@view_config(route_name = 'home', renderer = 'templates/post.mako')
def home(request):
    # Get the most recent post
    postname = DBSession.query(Post).\
                order_by(desc(Post.created)).first().name
    #return HTTPFound(location = request.route_url('view_post',
                                                #postname = 'Homepage'))
    request.matchdict['postname'] = postname
    return view_post(request)

@view_config(route_name = 'view_post', renderer = 'templates/post.mako')
def view_post(request):
    postname = request.matchdict['postname']
    page = DBSession.query(Post).filter_by(name = postname).first()
    if page:
        previous = DBSession.query(Post).\
                filter(Post.created < page.created).\
                order_by(desc(Post.created)).first()
        next = DBSession.query(Post).\
                filter(Post.created > page.created).\
                order_by(Post.created).first()

        if previous:
            previous = request.route_url('view_post',
                                        postname = previous.name)
        else:
            previous = None
        if next:
            next = request.route_url('view_post', postname = next.name)
        else:
            next = None
        return dict(title = page.name,
                    html = page.html,
                    prev_page = previous,
                    next_page = next)
    return HTTPNotFound('no such page exists')

@view_config(route_name = 'add_post', renderer = 'templates/edit.mako', permission = 'add')
def add_post(request):
    postname = request.matchdict['postname']
    if DBSession.query(Post).filter_by(name = postname).count():
        return HTTPFound(location = request.route_url('edit_post',
                                                postname = postname))

    if 'form.submitted' in request.params:
        body = request.params['body']
        html = markdown.markdown(body)
        DBSession.add(Post(name = postname,
                        markdown = body,
                        html = html))
        return HTTPFound(location = request.route_url('view_post',
                                                postname = postname))

    save_url = request.route_url('add_post', postname = postname)
    # We can then feed the save url into the template for the form
    return dict(title = 'Adding page: ' + postname,
                save_url = save_url,
                post_text = '')

@view_config(route_name = 'edit_post', renderer = 'templates/edit.mako', permission = 'edit')
def edit_post(request):
    postname = request.matchdict['postname']
    if not DBSession.query(Post).\
            filter_by(name = postname).count() == 1:
        return HTTPFound(location = request.route_url('home'))

    post = DBSession.query(Post).\
                filter_by(name = postname).\
                one()
    if 'form.submitted' in request.params:
        post.markdown = request.params['body']
        post.html = markdown.markdown(request.params['body'])
        DBSession.add(post)
        return HTTPFound(location = request.route_url('view_post',
                                                postname = postname))

    save_url = request.route_url('edit_post', postname = postname)
    post_text = DBSession.query(Post).\
                filter_by(name = postname).\
                one().markdown

    return dict(title = 'Editing page: ' + postname,
                post_text = post_text,
                save_url = save_url)
    

@view_config(route_name = 'del_post', renderer = 'templates/del.mako', permission = 'del')
def del_post(request):
    postname = request.matchdict['postname']
    if not DBSession.query(Post).\
                    filter_by(name = postname).count() == 1:
        return HTTPFound(location = request.route_url('home'))

    if 'form.submitted' in request.params:
        post = DBSession.query(Post).filter_by(name = postname).one()
        DBSession.delete(post)
        return HTTPFound(location = request.route_url('home'))
    save_url = request.route_url('del_post', postname = postname)
    return dict(title = "Deleting post: " + postname,
                save_url = save_url)
    
