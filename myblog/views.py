from operator import itemgetter
import myblog.utils as utils
from myblog.utils import use_template
import ago
import PyRSS2Gen
import datetime
import requests
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
import sqlalchemy.sql as sql
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from myblog.models import (
    DBSession,
    Post,
    Tags,
    Comments,
    Users,
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

@view_config(route_name = 'home')
@use_template('post.mako')
def home(request):
    # Get the most recent post.
    # We use the Core of sqlalchemy here for performance, and because
    # we don't need the power of the ORM here.
    query = sql.select([Post.name]).order_by(Post.created.desc()).limit(1)
    postname = DBSession.execute(query).fetchone().name
    request.matchdict['postname'] = postname
    return view_post(request, testing = 1)  # We do testing = 1 to get just the
    # dict back, Not a rendered response.

@view_config(route_name = 'view_post')
@utils.region.cache_on_arguments(function_key_generator = utils.cache_key_generator)
@use_template('post.mako')
def view_post(request):
    postname = request.matchdict['postname']
    page = DBSession.query(Post).filter_by(name = postname).first()
    if not page:
        return HTTPNotFound('no such page exists')

    # Here we use sqlalchemy Core in order to get a slight speed boost.
    previous_sql = sql.select([Post.name]).\
                where(Post.created < page.created).\
                order_by(Post.created.desc())
    previous = DBSession.execute(previous_sql).first()
    next_sql = sql.select([Post.name]).\
                where(Post.created > page.created).\
                order_by(Post.created)
    next = DBSession.execute(next_sql).first()

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

    comments = page.comments
    comments_list = []
    for comment in comments:
        to_append = {}
        to_append['created'] = ago.human(comment.created, precision = 1)
        to_append['author'] = comment.author.username
        to_append['comment'] = comment.comment
        to_append['uuid'] = comment.uuid
        comments_list.append(to_append)

    return dict(title = page.name,
                html = page.html,
                uuid = page.uuid,
                tags = tags,
                post_date = ago.human(page.created, precision = 1),
                prev_page = previous,
                next_page = next,
                comment_add_url = request.route_url('comment_add'),
                comments = comments_list)

def invalidate_post(postname):
    dummy_request = DummyRequest()
    dummy_request.matchdict['postname'] = postname
    view_post.invalidate(dummy_request)
    view_post.invalidate(dummy_request, testing = 1)

@view_config(route_name = 'view_all_posts')
@use_template('multiple_posts.mako')
def view_all_posts(request):
    # We use sqlalchemy Core here for performance.
    query = sql.select([Post.name, Post.markdown, Post.created]).\
            order_by(Post.created.desc())
    posts = DBSession.execute(query).fetchall()
    # TODO-log a critical error here maybe if all posts are deleted
    res, code_styles = utils.create_post_list_from_posts_obj(request, posts)

    return dict(title = 'All posts',
                posts = res,
                uuid = None,
                code_styles = code_styles)

@view_config(route_name = 'add_post', permission = 'add')
@use_template('edit.mako')
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

@view_config(route_name = 'edit_post', permission = 'edit')
@use_template('edit.mako')
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
        location = request.route_url('view_post',
                                    postname = postname)
        invalidate_post(postname)
        return HTTPFound(location = location)

    save_url = request.route_url('edit_post', postname = postname)
    post_text = post.markdown

    tags = utils.turn_tag_object_into_string_for_forms(post.tags)

    return dict(title = 'Editing page: ' + postname,
                post_text = post_text,
                tags = tags,  # To be modified in a bit
                save_url = save_url)

@view_config(route_name = 'del_post', permission = 'del')
@use_template('del.mako')
def del_post(request):
    # TODO-maybe don't allow deletion of a post if it is the only one.
    postname = request.matchdict['postname']
    if not DBSession.query(Post).\
                    filter_by(name = postname).count() == 1:
        return HTTPFound(location = request.route_url('home'))

    if 'form.submitted' in request.params:
        post = DBSession.query(Post).filter_by(name = postname).one()
        DBSession.delete(post)
        invalidate_post(postname)
        return HTTPFound(location = request.route_url('home'))
    save_url = request.route_url('del_post', postname = postname)
    return dict(title = "Deleting post: " + postname,
                save_url = save_url)

@view_config(route_name = 'tag_view')
@use_template('multiple_posts.mako')
def tag_view(request):
    tag = request.matchdict['tag_name']
    try:
        tag_obj = DBSession.query(Tags).filter_by(tag = tag).one()
    except NoResultFound:
        return HTTPNotFound('no such tag exists.')

    posts, code_styles = utils.create_post_list_from_posts_obj(request, tag_obj.posts)
    posts = sorted(posts, key = itemgetter("date"), reverse = True)

    return dict(title = 'Posts tagged with {}'.format(tag),
                posts = posts,
                uuid = tag_obj.uuid,
                code_styles = code_styles)

@view_config(route_name = 'tag_manager', permission = 'manage-tags')
@use_template('tag_manager.mako')
def tag_manager(request):
    tags = DBSession.query(Tags).order_by(Tags.tag).all()
    if 'form.submitted' in request.params:
        for tag in tags:
            # 1. If it is unchecked, delete it
            keep_tag = request.params.get('check-' + tag.tag)
            if not keep_tag:
                # Delete the tag
                DBSession.delete(tag)
            # 2. Else, if the name has been changed, update the name
            else:
                new_tag_name = request.params.get('text-' + tag.tag)
                if tag.tag != new_tag_name:
                    # Change the tag name in the db
                    tag.tag = new_tag_name
        return HTTPFound(location = request.route_url('tag_manager'))
    tags = [(tag.tag, len(tag.posts)) for tag in tags]
    return dict(tags = tags,
                title = 'Tag manager',
                save_url = request.route_url('tag_manager') )

@view_config(route_name = 'uuid')
def uuid(request):
    uuid_to_find = request.matchdict['uuid']

    # Check for a matching post.
    posts = DBSession.query(Post.uuid, Post.name).\
                filter(Post.uuid.startswith(uuid_to_find)).all()

    if len(posts) > 1:
        # TODO-give a more helpful response here.
        return Response('More than one uuid matched.')
    if posts:  # Here we check if there was just one post.
        return HTTPFound(location = request.route_url('view_post',
                                    postname = posts[0].name))

    # Check for a matching tag
    tags = DBSession.query(Tags.uuid, Tags.tag).\
           filter(Tags.uuid.startswith(uuid_to_find)).all()

    if len(tags) > 1:
        # TODO-give a more helpful response here.
        return Response('More than one uuid matched.')
    if tags:  # Here we check if there was just one post.
        return HTTPFound(location = request.route_url('tag_view',
                                    tag_name = tags[0].tag))
    return HTTPNotFound('No uuid matches.')

@view_config(route_name = 'comment_add')
def comment_add(request):
    '''We allow anyone to have access to this view. But we check whether a
    person is authenticated or not within this view. This is because we are
    allowing people to add comments anonymously ie not under an individual
    userid/username.'''
    if 'form.submitted' not in request.params:
        return HTTPNotFound()
    postname = request.params.get('postname', None)
    comment_text = request.params.get('comment', None)
    if not request.authenticated_userid:
        recaptcha = request.params.get('g-recaptcha-response', '')
        payload = dict(secret = '6LdPugUTAAAAACBpJ6IvHD2EF-PI-TaIhXvmbPf6',
                        response = recaptcha)
        result = requests.post('https://www.google.com/recaptcha/api/siteverify',
                    data = payload)
        try:
            if result.json()['success'] != True:
                return HTTPNotFound()
        except Exception:
            return HTTPNotFound()
    author = request.authenticated_userid or utils.get_anonymous_userid()
    if not all((postname, comment_text, author)):
        return HTTPNotFound()
    post = DBSession.query(Post).filter_by(name = postname).one()
    author = DBSession.query(Users).filter_by(userid = author).one()
    comment = Comments(comment = comment_text)
    comment.author = author
    post.comments.append(comment)
    invalidate_post(postname)
    return HTTPFound(location = request.route_url('view_post',
                                                postname = postname))

@view_config(route_name = 'comment_del', permission = 'comment-del')
def comment_delete(request):
    comment_uuid = request.params.get('comment-uuid', None)
    postname = request.params.get('postname', None)
    if not all((comment_uuid, postname)):
        return HTTPNotFound()
    comment = DBSession.query(Comments).filter_by(uuid = comment_uuid).first()
    if not comment:
        return HTTPNotFound()
    DBSession.delete(comment)
    invalidate_post(postname)
    return HTTPFound(location = request.route_url('view_post',
                                                postname = postname))
