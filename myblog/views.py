from operator import  itemgetter
import myblog.utils as utils
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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from myblog.models import (
    DBSession,
    Post,
    Tags,
    )


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
        categories = []
        for tag in post.tags:
            categories.append(tag.tag)

        item = PyRSS2Gen.RSSItem(title = title,
                    link= link, description= description,
                    #guid= guid,
                    categories = categories,
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
    if not page:
        return HTTPNotFound('no such page exists')
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

    # Get tags and make them into a string
    tags = utils.turn_tag_object_into_html_string_for_display(request,
                                                            page.tags)
    return dict(title = page.name,
                html = page.html,
                tags = tags,
                post_date = ago.human(page.created, precision = 1),
                prev_page = previous,
                next_page = next)

@view_config(route_name = 'view_all_posts',
            renderer = 'templates/multiple_posts.mako')
def view_all_posts(request):

    posts = DBSession.query(Post).order_by(desc(Post.created)).all()
    # TODO-log a critical error here maybe if all posts are deleted
    res, code_styles = utils.create_post_list_from_posts_obj(posts)

    return dict(title = 'All posts',
                posts = res,
                code_styles = code_styles)

@view_config(route_name = 'add_post', renderer = 'templates/edit.mako',
            permission = 'add')
def add_post(request):
    postname = request.matchdict['postname']
    if DBSession.query(Post).filter_by(name = postname).count():
        return HTTPFound(location = request.route_url('edit_post',
                                                postname = postname))

    if 'form.submitted' in request.params:
        post = Post()
        post.name = postname
        post.markdown = request.params['body']
        post.html = utils.to_markdown(post.markdown)
        tags = request.params['tags']
        utils.append_tags_from_string_to_tag_object(tags, post.tags)
        DBSession.add(post)
        return HTTPFound(location = request.route_url('view_post',
                                                postname = postname))

    save_url = request.route_url('add_post', postname = postname)
    # We can then feed the save url into the template for the form
    return dict(title = 'Adding page: ' + postname,
                save_url = save_url,
                post_text = '',
                tags = '')

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
        post.html = utils.to_markdown(request.params['body'])
        tags = request.params['tags']
        utils.append_tags_from_string_to_tag_object(tags, post.tags)
        DBSession.add(post)
        return HTTPFound(location = request.route_url('view_post',
                                                postname = postname))

    save_url = request.route_url('edit_post', postname = postname)
    post_text = post.markdown

    tags = utils.turn_tag_object_into_string_for_forms(post.tags)

    return dict(title = 'Editing page: ' + postname,
                post_text = post_text,
                tags = tags,  # To be modified in a bit
                save_url = save_url)

@view_config(route_name = 'del_post', renderer = 'templates/del.mako',
            permission = 'del')
def del_post(request):
    # TODO-maybe don't allow deletion of a post if it is the only one.
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

@view_config(route_name = 'tag_view', renderer = 'templates/multiple_posts.mako')
def tag_view(request):
    tag = request.matchdict['tag_name']
    try:
        tag_obj = DBSession.query(Tags).filter_by(tag = tag).one()
    except NoResultFound:
        return HTTPNotFound('no such tag exists.')

    posts, code_styles = utils.create_post_list_from_posts_obj(tag_obj.posts)
    posts = sorted(posts, key = itemgetter("date"), reverse = True)

    return dict(title = 'Posts tagged with {}'.format(tag),
                posts = posts,
                code_styles = code_styles)
