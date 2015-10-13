import fireblog.utils as utils
from fireblog.views import invalidate_post
import requests
from webhelpers2.text import urlify as u
from pyramid.view import view_config
from pyramid.events import subscriber
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)
from fireblog.models import (
    DBSession,
    Post,
    Comments,
    Users,
)


def add_comment_section_below_posts(event):
    comments_list = render_comments_list_from_event(event)
    comment_add_url = event.request.route_url('comment_add')
    html = utils.render_to_response('comments.mako',
                                    {'comments': comments_list,
                                     'comment_add_url': comment_add_url,
                                     'post_title': event.post.name,
                                     'post_id': event.post.id},
                                    event.request).text
    event.sections.append(html)


def render_comments_list_from_event(event):
    comments = event.post.comments
    comments_list = []
    for comment in comments:
        to_append = {}
        to_append['created'] = utils.format_datetime(comment.created)
        to_append['author'] = comment.author.username
        to_append['comment'] = comment.comment
        to_append['uuid'] = comment.uuid
        comments_list.append(to_append)
    return comments_list


@view_config(route_name='comment_add', request_param='form.submitted')
def comment_add(request):
    '''We allow anyone to have access to this view. But we check whether a
    person is authenticated or not within this view. This is because we are
    allowing people to add comments anonymously ie not under an individual
    userid/username.'''
    post_id = request.params.get('post-id', None)
    comment_text = request.params.get('comment', None)
    if not request.authenticated_userid:
        recaptcha = request.params.get('g-recaptcha-response', '')
        settings = request.registry.settings
        recaptcha_site_secret = settings['fireblog.recaptcha-secret']
        payload = dict(secret=recaptcha_site_secret,
                       response=recaptcha)
        result = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=payload)
        try:
            if not result.json()['success']:
                return HTTPNotFound()
        except Exception:
            return HTTPNotFound()
    author = request.authenticated_userid or utils.get_anonymous_userid()
    if not all((post_id, comment_text, author)):
        return HTTPNotFound()
    post = DBSession.query(Post).filter_by(id=post_id).one()
    author = DBSession.query(Users).filter_by(userid=author).one()
    comment = Comments(comment=comment_text)
    comment.author = author
    post.comments.append(comment)
    invalidate_post(post.name)
    return HTTPFound(location=request.route_url('view_post',
                                                id=post_id,
                                                postname=u(post.name)))


@view_config(route_name='comment_del', permission='comment-del')
def comment_delete(request):
    comment_uuid = request.params.get('comment-uuid', None)
    post_id = request.params.get('post-id', None)
    if not all((comment_uuid, post_id)):
        return HTTPNotFound()
    comment = DBSession.query(Comments).filter_by(uuid=comment_uuid).first()
    if not comment:
        return HTTPNotFound()
    DBSession.delete(comment)
    invalidate_post(comment.post.name)
    return HTTPFound(location=request.route_url('view_post',
                                                id=post_id,
                                                postname=u(comment.post.name)))


def includeme(config):
    config.add_route('comment_add', '/add')
    config.add_route('comment_del', '/del')
    config.add_subscriber(add_comment_section_below_posts, utils.RenderingPost)
