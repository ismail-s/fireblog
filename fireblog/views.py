from operator import itemgetter
import fireblog.utils as utils
from fireblog.utils import use_template, TemplateResponseDict
import PyRSS2Gen
import dogpile.cache.util
import datetime
from pyramid.view import view_config, view_defaults
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
from fireblog.models import (
    DBSession,
    Post,
    Tags,
    Comments,
    Users,
)


@view_config(route_name='rss')
def render_rss_feed(request):
    posts = DBSession.query(Post).order_by(desc(Post.created)).all()
    items = []
    for post in posts[:10]:
        title = post.name
        link = request.route_url('view_post', id=post.id, postname=title)
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
    # Get the most recent post.
    # We use the Core of sqlalchemy here for performance, and because
    # we don't need the power of the ORM here.
    query = sql.select([Post.id, Post.name]).order_by(Post.created.desc()).limit(1)
    query_res = DBSession.execute(query).fetchone()
    request.matchdict['postname'] = query_res.name
    request.matchdict['id'] = query_res.id
    return view_post(request)


@view_config(route_name='view_post', decorator=use_template('post.mako'))
def view_post(request):
    page = DBSession.query(Post).filter_by(id=request.matchdict['id']).first()
    if not page:
        return HTTPNotFound('no such page exists')
    post_dict = get_post_section_as_dict(request, page, postname=page.name)

    # Fire off an event that lets any plugins or whatever add content below the
    # post. Currently this is used just to add comments below the post.
    event = utils.RenderingPost(post=page, request=request)
    request.registry.notify(event)

    post_dict['bottom_of_page_sections'] = event.sections
    return TemplateResponseDict(post_dict)


def post_key_generator(*args, **kwargs):
    old_key_generator = dogpile.cache.util.function_key_generator(*args,
                                                                  **kwargs)

    def new_key_generator(*args, **kwargs):
        postname = kwargs['postname']
        return '|'.join((old_key_generator(), postname))
    return new_key_generator


@utils.region.cache_on_arguments(function_key_generator=post_key_generator)
def get_post_section_as_dict(request, page, postname):
    if not all((request, page, postname)):
        raise Exception('Function called incorrectly-check calling code.')
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
                                     id=previous.id,
                                     postname=previous.name)
    else:
        previous = None
    if next:
        next = request.route_url('view_post', id=next.id, postname=next.name)
    else:
        next = None

    # Get tags and make them into a string
    tags = utils.turn_tag_object_into_html_string_for_display(request,
                                                              page.tags)

    post_date = utils.format_datetime(page.created)
    return dict(title=page.name,
                html=page.html,
                uuid=page.uuid,
                tags=tags,
                post_date=post_date,
                prev_page=previous,
                next_page=next)


def invalidate_post(postname):
    get_post_section_as_dict.invalidate(None, None, postname=postname)


@view_config(route_name='view_all_posts',
             decorator=use_template('multiple_posts.mako'))
def view_all_posts(request):
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


@view_defaults(route_name='change_post')
class Post_modifying_views(object):

    def __init__(self, request):
        self.request = request
        self.postname = self.request.matchdict['postname']
        self.no_of_posts_with_postname = DBSession.query(Post).\
            filter_by(name=self.postname).count()
        self.matching_posts = DBSession.query(Post).\
            filter_by(name=self.postname).all()

    @view_config(match_param="action=add", request_method="GET",
                 decorator=use_template('edit.mako'), permission='add')
    def add_post(self):
        if len(self.matching_posts):
            return HTTPFound(
                location=self.request.route_url(
                    'change_post',
                    postname=self.postname,
                    action='edit'))
        save_url = self.request.route_url(
            'change_post', postname=self.postname, action='add')
        # We can then feed the save url into the template for the form
        return TemplateResponseDict(title='Adding page: ' + self.postname,
                                    save_url=save_url,
                                    post_text='',
                                    tags='')

    @view_config(match_param="action=add", request_method="POST",
                 request_param='form.submitted', permission='add')
    def add_post_POST(self):
        if len(self.matching_posts):
            return HTTPFound(
                location=self.request.route_url(
                    'change_post',
                    postname=self.postname,
                    action='edit'))
        post = Post()
        post.name = self.postname
        post.markdown = self.request.params['body']
        post.html = utils.to_markdown(post.markdown)
        tags = self.request.params['tags']
        utils.append_tags_from_string_to_tag_object(tags, post.tags)
        DBSession.add(post)
        # Make sure the non-existence of this post is not cached. ie someone
        # could have previously tried to get this post, but the 404 response
        # could have been cached.
        invalidate_post(self.postname)
        return HTTPFound(
            location=self.request.route_url(
                'view_post',
                postname=self.postname))

    @view_config(match_param="action=edit", request_method="GET",
                 decorator=use_template('edit.mako'), permission='edit')
    def edit_post(self):
        if len(self.matching_posts) != 1:
            return HTTPFound(location=self.request.route_url('home'))

        post = self.matching_posts[0]
        save_url = self.request.route_url(
            'change_post', postname=self.postname, action='edit')
        post_text = post.markdown

        tags = utils.turn_tag_object_into_string_for_forms(post.tags)

        return TemplateResponseDict(title='Editing page: ' + self.postname,
                                    post_text=post_text,
                                    tags=tags,  # To be modified in a bit
                                    save_url=save_url)

    @view_config(match_param="action=edit", request_method="POST",
                 request_param='form.submitted', permission='edit')
    def edit_post_POST(self):
        if len(self.matching_posts) != 1:
            return HTTPFound(location=self.request.route_url('home'))

        post = self.matching_posts[0]
        post.markdown = self.request.params['body']
        post.html = utils.to_markdown(self.request.params['body'])
        tags = self.request.params['tags']
        utils.append_tags_from_string_to_tag_object(tags, post.tags)
        DBSession.add(post)
        location = self.request.route_url('view_post',
                                          postname=self.postname)
        invalidate_post(self.postname)
        return HTTPFound(location=location)

    @view_config(match_param="action=del", request_method="GET",
                 decorator=use_template('del.mako'), permission='del')
    def del_post(self):
        # TODO-maybe don't allow deletion of a post if it is the only one.
        if len(self.matching_posts) != 1:
            return HTTPFound(location=self.request.route_url('home'))
        save_url = self.request.route_url(
            'change_post', postname=self.postname, action='del')
        return TemplateResponseDict(title="Deleting post: " + self.postname,
                                    save_url=save_url)

    @view_config(match_param="action=del", request_method="POST",
                 request_param='form.submitted', permission='del')
    def del_post_POST(self):
        # TODO-maybe don't allow deletion of a post if it is the only one.
        if len(self.matching_posts) != 1:
            return HTTPFound(location=request.route_url('home'))
        post = self.matching_posts[0]
        DBSession.delete(post)
        invalidate_post(self.postname)
        return HTTPFound(location=self.request.route_url('home'))


@view_config(route_name='uuid')
def uuid(request):
    uuid_to_find = request.matchdict['uuid']

    # Check for a matching post.
    posts = DBSession.query(Post.uuid, Post.name).\
        filter(Post.uuid.startswith(uuid_to_find)).all()

    if len(posts) > 1:
        # TODO-give a more helpful response here.
        return Response('More than one uuid matched.')
    if posts:  # Here we check if there was just one post.
        return HTTPFound(location=request.route_url('view_post',
                                                    postname=posts[0].name))

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
