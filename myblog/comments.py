import myblog.utils as utils
from myblog.views import invalidate_post
import requests
import ago
from pyramid.view import view_config
from pyramid.events import subscriber
from pyramid.httpexceptions import (
HTTPFound,
HTTPNotFound,
)
from myblog.models import (
DBSession,
Post,
Comments,
Users,
)


def add_comment_section_below_posts(event):
    comments = event.post.comments
    comments_list = []
    for comment in comments:
        to_append = {}
        to_append['created'] = ago.human(comment.created, precision = 1)
        to_append['author'] = comment.author.username
        to_append['comment'] = comment.comment
        to_append['uuid'] = comment.uuid
        comments_list.append(to_append)
    html = utils.render_to_response('comments.mako',
                                        {'comments': comments_list,
                                        'comment_add_url': event.request.route_url('comment_add'),
                                        'post_title': event.post.name},
                                    event.request).text
    event.sections.append(html)

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

def includeme(config):
    config.add_route('comment_add', '/add')
    config.add_route('comment_del', '/del')
    config.add_subscriber(add_comment_section_below_posts, utils.RenderingPost)
