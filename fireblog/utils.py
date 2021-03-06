from markdown import markdown
from fireblog.models import DBSession, Tags, Users
from fireblog.htmltruncate import truncate as truncate_html
from fireblog.settings import settings_dict
from fireblog.dogpile_region import region
import arrow
import transaction


def urlify(string: str) -> str:
    """Replace spaces with dashes. We don't do anything else like urlencoding,
    as pyramid does that already for us."""
    return string.replace(' ', '-')


def format_datetime(datetime):
    '''Return a string representing the datetime object. eg \'20 Jan 2014\''''
    return arrow.get(datetime).format('DD MMM YYYY')


def get_anonymous_userid() -> str:
    """Returns the userid of the unique anonymous id. This userid is used
    whenever somneone wants to post a comment anonymously, as all comments
    must be associated with some author.

    If the anonymous user doesn't exist in the db, they are created on the
    fly."""
    anon_email = 'anonymous@example.com'
    user = DBSession.query(Users.userid).filter_by(userid=anon_email).first()
    with transaction.manager:
        if not user:
            # Create user
            user = Users(userid=anon_email)
            DBSession.add(user)
    return anon_email


@region.cache_on_arguments()
def to_markdown(input_text):
    '''Basic wrapper around the markdown library. This function accepts
    markdown and returns html. It enables extensions that allow for code
    highlighting and writing code using fenced code blocks.'''
    extensions = ['markdown.extensions.codehilite',
                  'markdown.extensions.fenced_code']
    res = markdown(input_text, extensions=extensions)
    return res


def append_tags_from_string_to_tag_object(tag_string, tag_object):
    tags_on_tag_object = []  # This is to be a list of tags on the tag_object
    for tag in tag_object:
        tags_on_tag_object.append(tag.tag)
    new_tag_list = tag_string.split(',')
    new_tag_list = [x.strip() for x in new_tag_list]
    new_tag_list = list(set(new_tag_list))

    # 1. Add the tag if it needs to be added.
    for tag in new_tag_list:
        # If the tag exists already, we get the object from DBSession.
        # If it doesn't, then we create a new tag object.
        if not tag:
            continue
        if tag in tags_on_tag_object:
            continue

        # 1.1 Get a tag object.
        existing_tag = DBSession.query(Tags).filter_by(tag=tag).first()
        if not existing_tag:
            tag_obj = Tags(tag=tag)
            DBSession.add(tag_obj)
        else:
            tag_obj = existing_tag

        # 1.2 Update the post with the tag object
        tag_object.append(tag_obj)

    # 2. Remove tags that need to be removed
    for tag in tags_on_tag_object:
        if tag not in new_tag_list:
            tag_object.remove(DBSession.query(Tags).filter_by(tag=tag).first())


def _turn_tag_object_into_sorted_list(tag_object):
    tags = sorted([t.tag for t in tag_object])
    return tags


def turn_tag_object_into_string_for_forms(tag_object):
    tags = _turn_tag_object_into_sorted_list(tag_object)
    tags = ', '.join(tags)
    return tags


def turn_tag_object_into_html_string_for_display(request, tag_object):
    tags = _turn_tag_object_into_sorted_list(tag_object)
    if not tags:
        return ''
    for e, tag in enumerate(tags):
        tags[e] = "<a href = {link}>{tag}</a>".format(
            tag=tag, link=request.route_url('tag_view', tag_name=tag))
    return ', '.join(tags)


def create_post_list_from_posts_obj(request, post_obj):
    LENGTH_OF_EACH_POST_TO_INCLUDE_IN_ALL_POST_VIEW = settings_dict[
        'fireblog.all_view_post_len']
    l = LENGTH_OF_EACH_POST_TO_INCLUDE_IN_ALL_POST_VIEW
    res = []
    code_styles = False  # Is true if we need to include pygments css
    # in the page
    for post in post_obj:
        to_append = {}
        to_append["id"] = post.id
        to_append["name"] = post.name
        html = to_markdown(post.markdown)
        html = truncate_html(html, l, ellipsis='...')
        to_append["html"] = html
        to_append["date"] = format_datetime(post.created)
        res.append(to_append)
        if not code_styles and 'class="codehilite"' in to_append["html"]:
            code_styles = True
    return res, code_styles
