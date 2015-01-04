from myblog.utils import to_markdown
import ago
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
from myblog.models import (
    DBSession,
    Post,
    )


LENGTH_OF_EACH_POST_TO_INCLUDE_IN_ALL_POST_VIEW = 200

@view_config(route_name = 'rss')
def render_rss_feed(request):
    posts = DBSession.query(Post).order_by(desc(Post.created)).all()
    items= []
    for post in posts[:10]:
        title = post.name
        link = request.route_url('view_post', postname = title)
        description = post.html
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
    # maybe write the file into the static folder and remake it whenever
    # a post is modified...
    return Response(rss.to_xml(), content_type = 'application/xml')

@view_config(route_name = 'home', renderer = 'templates/post.mako')
def home(request):
    # Get the most recent post. This maybe should use invoke_subrequest,
    # but for the moment it works fine.
    postname = DBSession.query(Post).\
                order_by(desc(Post.created)).first().name
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
                    post_date = ago.human(page.created, precision = 1),
                    prev_page = previous,
                    next_page = next)
    return HTTPNotFound('no such page exists')

@view_config(route_name = 'view_all_posts',
            renderer = 'templates/all_posts.mako')
def view_all_posts(request):
    # I use "l" here. The variable is only used once below anyways.
    l = LENGTH_OF_EACH_POST_TO_INCLUDE_IN_ALL_POST_VIEW

    posts = DBSession.query(Post).order_by(desc(Post.created)).all()
    # TODO-log a critical error here maybe if all posts are deleted
    res = []
    code_styles = False  # Is true if we need to include pygments css
    # in the page
    for post in posts:
        to_append = {}
        to_append["name"] = post.name
        to_append["html"] = to_markdown(post.markdown[:l] + '\n\n...')
        res.append(to_append)
        if not code_styles and 'class="codehilite"' in post.html:
            code_styles = True

    return dict(posts = res,
                code_styles = code_styles)

@view_config(route_name = 'add_post', renderer = 'templates/edit.mako',
            permission = 'add')
def add_post(request):
    postname = request.matchdict['postname']
    if DBSession.query(Post).filter_by(name = postname).count():
        return HTTPFound(location = request.route_url('edit_post',
                                                postname = postname))

    if 'form.submitted' in request.params:
        body = request.params['body']
        html = to_markdown(body)
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

@view_config(route_name = 'edit_post', renderer = 'templates/edit.mako',
            permission = 'edit')
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
        post.html = to_markdown(request.params['body'])
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

@view_config(route_name = 'del_post', renderer = 'templates/del.mako',
            permission = 'del')
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
