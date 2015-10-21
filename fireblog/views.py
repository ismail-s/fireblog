'Views for doing stuff with posts, generating RSS feeds and dealing with uuids.'
import fireblog.utils as utils
import fireblog.events as events
from fireblog.utils import use_template, TemplateResponseDict
from fireblog.utils import urlify as u
import PyRSS2Gen
import dogpile.cache.util
import datetime
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)
import sqlalchemy.sql as sql
from sqlalchemy import desc
from fireblog.models import (
    DBSession,
    Post,
    Tags,
)


@view_config(route_name='rss')
def render_rss_feed(request):
    "Generate an RSS feed of all posts."
    posts = DBSession.query(Post).order_by(desc(Post.created)).all()
    items = []
    for post in posts[:10]:
        title = post.name
        link = request.route_url('view_post', id=post.id, postname=u(title))
        description = post.html
        # guid = PyRSS2Gen.Guid('')
        pub_date = post.created
        categories = []
        for tag in post.tags:
            categories.append(tag.tag)

        item = PyRSS2Gen.RSSItem(title=title,
                                 link=link, description=description,
                                 # guid= guid,
                                 categories=categories,
                                 pubDate=pub_date)

        items.append(item)

    rss = PyRSS2Gen.RSS2(
        title="Not the Answer",
        link="https://blog.ismail-s.com",
        description="A personal blog about science, computers and life.",

        lastBuildDate=datetime.datetime.utcnow(),

        items=items)
    # maybe write the file into the static folder and remake it whenever
    # a post is modified...
    return Response(rss.to_xml(), content_type='application/xml')


@view_config(route_name='home', decorator=use_template('post.mako'))
def home(request):
    """Call :py:func:`view_post` and display the most recent post."""
    # Get the most recent post.
    # We use the Core of sqlalchemy here for performance, and because
    # we don't need the power of the ORM here.
    query = sql.select([Post.id, Post.name]).\
        order_by(Post.created.desc()).limit(1)
    query_res = DBSession.execute(query).fetchone()
    request.matchdict['postname'] = query_res.name
    request.matchdict['id'] = query_res.id
    return view_post(request)


@view_config(route_name='view_post', decorator=use_template('post.mako'))
def view_post(request):
    """Find the post in the db with an ``id == request.matchdict['id']`` and
    display this post, along with associated comments, tags, and links to
    previous, next and all posts."""
    post_id = request.matchdict['id']
    page = DBSession.query(Post).filter_by(id=post_id).first()
    if not page:
        return HTTPNotFound('no such page exists')
    post_dict = _get_post_section_as_dict(request, page, post_id=post_id)

    # Fire off an event that lets any plugins or whatever add content below the
    # post. Currently this is used just to add comments below the post.
    event = events.RenderingPost(post=page, request=request)
    request.registry.notify(event)

    post_dict['bottom_of_page_sections'] = event.sections
    return TemplateResponseDict(post_dict)


def post_key_generator(*args, **kwargs):
    old_key_generator = dogpile.cache.util.function_key_generator(*args,
                                                                  **kwargs)

    def new_key_generator(*args, **kwargs):
        post_id = str(kwargs['post_id'])
        return '|'.join((old_key_generator(), post_id))
    return new_key_generator


@utils.region.cache_on_arguments(function_key_generator=post_key_generator)
def _get_post_section_as_dict(request, page, post_id):
    post_id = int(post_id)
    assert page.id == post_id
    # Here we use sqlalchemy Core in order to get a slight speed boost.
    previous_sql = sql.select([Post.id, Post.name]).\
        where(Post.created < page.created).\
        order_by(Post.created.desc())
    previous = DBSession.execute(previous_sql).first()
    next_sql = sql.select([Post.id, Post.name]).\
        where(Post.created > page.created).\
        order_by(Post.created)
    next = DBSession.execute(next_sql).first()

    if previous:
        previous = request.route_url('view_post',
                                     id=previous.id,
                                     postname=u(previous.name))
    else:
        previous = None
    if next:
        next = request.route_url(
            'view_post', id=next.id, postname=u(next.name))
    else:
        next = None

    # Get tags and make them into a string
    tags = utils.turn_tag_object_into_html_string_for_display(request,
                                                              page.tags)

    post_date = utils.format_datetime(page.created)
    return dict(title=page.name,
                post_id=post_id,
                html=page.html,
                uuid=page.uuid,
                tags=tags,
                post_date=post_date,
                prev_page=previous,
                next_page=next)


def invalidate_post(post_id):
    "Invalidate post entry in the cache based on the supplied post_id."
    # Make sure post_id is an int
    assert int(post_id)
    _get_post_section_as_dict.invalidate(None, None, post_id=post_id)


def invalidate_current_post(event):
    assert hasattr(event, 'post')
    post_id = event.post.id
    invalidate_post(post_id)


def invalidate_previous_post(event):
    assert hasattr(event, 'post')
    previous_sql = sql.select([Post.id]).\
        where(Post.created < event.post.created).\
        order_by(Post.created.desc())
    post = DBSession.execute(previous_sql).first()
    if post:
        invalidate_post(post.id)


def invalidate_next_post(event):
    assert hasattr(event, 'post')
    next_sql = sql.select([Post.id]).\
        where(Post.created > event.post.created).\
        order_by(Post.created)
    next = DBSession.execute(next_sql).first()
    if next:
        invalidate_post(next.id)


@view_config(route_name='view_all_posts',
             decorator=use_template('multiple_posts.mako'))
def view_all_posts(request):
    """Display a page containing all posts, with a sample of each post and
    links to each post."""
    # We use sqlalchemy Core here for performance.
    query = sql.select([Post.id, Post.name, Post.markdown, Post.created]).\
        order_by(Post.created.desc())
    posts = DBSession.execute(query).fetchall()
    # TODO-log a critical error here maybe if all posts are deleted
    res, code_styles = utils.create_post_list_from_posts_obj(request, posts)

    return TemplateResponseDict(title='All posts',
                                posts=res,
                                uuid=None,
                                code_styles=code_styles)


@view_defaults(route_name='add_post', permission='add')
class Add_Post(object):
    """Views that deal with adding a new post."""

    def __init__(self, request):
        self.request = request
        self.postname = request.matchdict['postname']
        self.matching_post = DBSession.query(Post.id).\
            filter_by(name=self.postname).first()

    @view_config(request_method="GET",
                 decorator=use_template('edit.mako'))
    def add_post(self):
        "Disply the page that the user can use to add a new post."
        if self.matching_post:
            return HTTPFound(
                location=self.request.route_url(
                    'change_post',
                    id=self.matching_post.id,
                    postname=u(self.postname),
                    action='edit'))
        save_url = self.request.route_url('add_post', postname=self.postname)
        # We can then feed the save url into the template for the form
        return TemplateResponseDict(title='Adding page: ' + self.postname,
                                    save_url=save_url,
                                    post_text='',
                                    tags='')

    @view_config(request_method="POST",
                 request_param='form.submitted')
    def add_post_POST(self):
        "Handle a POST submission of a new post."
        if self.matching_post:
            return HTTPFound(
                location=self.request.route_url(
                    'change_post',
                    id=self.matching_post.id,
                    postname=u(self.postname),
                    action='edit'))
        post = Post()
        post.name = self.postname
        post.markdown = self.request.params['body']
        post.html = utils.to_markdown(post.markdown)
        tags = self.request.params['tags']
        utils.append_tags_from_string_to_tag_object(tags, post.tags)
        DBSession.add(post)
        DBSession.flush()
        self.request.registry.notify(events.PostCreated(post))
        return HTTPFound(location=self.request.route_url('home'))


@view_defaults(route_name='change_post')
class Post_modifying_views(object):
    "Views that edit or delete posts."

    def __init__(self, request):
        self.request = request
        self.post_id = request.matchdict['id']
        self.postname = request.matchdict['postname']
        self.post = DBSession.query(Post).\
            filter_by(id=self.post_id).first()
        if self.post and self.postname != self.post.name:
            self.postname = self.post.name

    @view_config(match_param="action=edit", request_method="GET",
                 decorator=use_template('edit.mako'), permission='edit')
    def edit_post(self):
        "Display the page used to edit posts."
        if not self.post:
            return HTTPFound(location=self.request.route_url('home'))

        post = self.post
        save_url = self.request.route_url(
            'change_post',
            id=self.post_id,
            postname=u(self.postname),
            action='edit')
        post_text = post.markdown

        tags = utils.turn_tag_object_into_string_for_forms(post.tags)

        return TemplateResponseDict(title='Editing page: ' + self.postname,
                                    post_text=post_text,
                                    tags=tags,  # To be modified in a bit
                                    save_url=save_url)

    @view_config(match_param="action=edit", request_method="POST",
                 request_param='form.submitted', permission='edit')
    def edit_post_POST(self):
        "Handle a POST submission of an edited post."
        if not self.post:
            return HTTPFound(location=self.request.route_url('home'))

        post = self.post
        post.markdown = self.request.params['body']
        post.html = utils.to_markdown(self.request.params['body'])
        tags = self.request.params['tags']
        utils.append_tags_from_string_to_tag_object(tags, post.tags)
        DBSession.add(post)
        location = self.request.route_url('view_post',
                                          id=self.post_id,
                                          postname=u(self.postname))
        self.request.registry.notify(events.PostEdited(post))
        invalidate_post(self.post_id)
        return HTTPFound(location=location)

    @view_config(match_param="action=del", request_method="GET",
                 decorator=use_template('del.mako'), permission='del')
    def del_post(self):
        "Display a page with a button to delete the specified post."
        # TODO-maybe don't allow deletion of a post if it is the only one.
        if not self.post:
            return HTTPFound(location=self.request.route_url('home'))
        save_url = self.request.route_url(
            'change_post',
            id=self.post_id,
            postname=u(self.postname),
            action='del')
        return TemplateResponseDict(title="Deleting post: " + self.postname,
                                    save_url=save_url)

    @view_config(match_param="action=del", request_method="POST",
                 request_param='form.submitted', permission='del')
    def del_post_POST(self):
        "Handle a POST submission to delete a post."
        # TODO-maybe don't allow deletion of a post if it is the only one.
        if not self.post:
            return HTTPFound(location=self.request.route_url('home'))
        self.request.registry.notify(events.PostDeleted(self.post))
        DBSession.delete(self.post)
        invalidate_post(self.post_id)
        return HTTPFound(location=self.request.route_url('home'))


@view_config(route_name='uuid')
def uuid(request):
    """UUIDs are randomly generated strings associated with various objects.
    They are virtually guaranteed to be unique (by probability), and are used
    to provide permalinks to posts, posts with a certain tag, basically any
    kind of object.

    This function redirects the user to a page that is the one associated to
    the supplied uuid (which is supplied as ``request.matchdict['uuid']``)."""
    uuid_to_find = request.matchdict['uuid']

    # Check for a matching post.
    posts = DBSession.query(Post.id, Post.uuid, Post.name).\
        filter(Post.uuid.startswith(uuid_to_find)).all()

    if len(posts) > 1:
        # TODO-give a more helpful response here.
        return Response('More than one uuid matched.')
    if posts:  # Here we check if there was just one post.
        post = posts[0]
        return HTTPFound(location=request.route_url('view_post',
                                                    id=post.id,
                                                    postname=u(post.name)))

    # Check for a matching tag
    tags = DBSession.query(Tags.uuid, Tags.tag).\
        filter(Tags.uuid.startswith(uuid_to_find)).all()

    if len(tags) > 1:
        # TODO-give a more helpful response here.
        return Response('More than one uuid matched.')
    if tags:  # Here we check if there was just one post.
        return HTTPFound(location=request.route_url('tag_view',
                                                    tag_name=tags[0].tag))
    return HTTPNotFound('No uuid matches.')


def includeme(config) -> None:
    """Contains configuration to invalidate cached posts when they become
    invalid in various situations."""
    # These config statements invalidate cached posts when they become invalid.
    config.add_subscriber(invalidate_current_post, events.PostCreated)
    config.add_subscriber(invalidate_previous_post, events.PostCreated)
    config.add_subscriber(invalidate_current_post, events.PostEdited)
    config.add_subscriber(invalidate_current_post, events.PostDeleted)
    config.add_subscriber(invalidate_previous_post, events.PostDeleted)
    config.add_subscriber(invalidate_next_post, events.PostDeleted)
