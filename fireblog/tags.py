'Views for managing tags, and viewing all posts with a particular tag.'
from operator import attrgetter
import fireblog.utils as utils
from fireblog.utils import use_template, TemplateResponseDict
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)
from sqlalchemy.orm.exc import NoResultFound
from fireblog.models import (
    DBSession,
    Tags,
)


@view_config(route_name='tag_view',
             decorator=use_template('multiple_posts.mako'))
def tag_view(request):
    """Display a page similar to that of
    :py:func:`fireblog.views.view_all_posts` but just showing the posts that
    have the supplied tag on them. The tag supplied is
    ``request.matchdict['tag_name']``."""
    tag = request.matchdict['tag_name']
    try:
        tag_obj = DBSession.query(Tags).filter_by(tag=tag).one()
    except NoResultFound:
        return HTTPNotFound('no such tag exists.')
    posts_obj = tag_obj.posts
    posts_obj = sorted(posts_obj, key=attrgetter("created"))
    posts, code_styles = utils.create_post_list_from_posts_obj(
        request, posts_obj)

    return TemplateResponseDict(title='Posts tagged with {}'.format(tag),
                                posts=posts,
                                uuid=tag_obj.uuid,
                                code_styles=code_styles)


@view_config(route_name='tag_manager', decorator=use_template(
    'tag_manager.mako'), permission='manage-tags')
def tag_manager(request):
    """Display a page listing all the tags that exist in the db, and how many
    posts have been tagged with each tag. The user can then rename one or
    more tags, and specify if any tags should be deleted."""
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
        return HTTPFound(location=request.route_url('tag_manager'))
    tags = [(tag.tag, len(tag.posts)) for tag in tags]
    return TemplateResponseDict(tags=tags,
                                title='Tag manager',
                                save_url=request.route_url('tag_manager'))
