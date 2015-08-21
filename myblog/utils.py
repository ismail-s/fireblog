from markdown import markdown
import ago
from myblog.models import DBSession, Tags, Users
from pyramid_dogpile_cache import get_region
import dogpile.cache.util
import functools
from pyramid import renderers
from pyramid.request import Request
from pyramid.response import Response
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPException

# This is the dogpile_cache cache region.
try:
    region = get_region('')
except KeyError:
    # KeyError occurs when this module is directly imported before myblog:main
    # is called. Basically, in the myblog:main function, pyramid_dogpile_cache
    # plugin sets up dogpile.cache using settings from the usual ini files.
    # However, if this module is imported first, then this setup doesn't happen.
    # As a result, as a fallback in these cases (atm only when tests are run,
    # which is when we actually want to check that the cache is correctly
    # managed by the website) we use the memory cache backend.
    region = get_region('', backend = 'dogpile.cache.memory')

def _find_request_obj_in_args(args, *more_args):
    '''
    Pass in a list of args, and this function returns the first one that is an
    instance of pyramid.request.Request. Else, we return None.
    '''
    args = list(args)
    args.extend(more_args)
    for elem in args:
        if isinstance(elem, Request) or isinstance(elem, DummyRequest):
            return elem
    return None

def cache_key_generator(*args, **kwargs):
    old_key_generator = dogpile.cache.util.function_key_generator(*args,
                                                                **kwargs)
    def new_key_generator(*args, **kwargs):
        # args = (context, request) or (request)
        request = _find_request_obj_in_args(args)
        testing_str = ''
        if kwargs:
            NO_ARG = object()
            testing = kwargs.get('testing', NO_ARG)
            if testing != NO_ARG and testing:
                testing_str = 'testing'
        return '|'.join((old_key_generator(), request.matchdict['postname'], testing_str))
    return new_key_generator


class TemplateResponseDict(dict):
    '''Instances of this dict can be used as the return type of a view callable
    that is using the use_template decorator. The use_template decorator will
    notice that an instance of this type is being returned and render it to a
    response.'''
    pass


def use_template(template = None):
    def wrapper(f, template = template):
        @functools.wraps(f)
        def inner(context, request):
            res = f(context, request)
            # Deal with eg HTTPFound or HTTPNotFound by just returning them.
            if isinstance(res, HTTPException):
                return res
            to_render = eval(res.text)
            if type(to_render) != dict:
                raise Exception("The use_template decorator is being used "
                "incorrectly: the decorated view callable must return a dict.")
            return render_to_response(template, to_render, request)
        return inner
    return wrapper

def render_to_response(template, res, request):
    theme = request.registry.settings['myblog.theme']
    template = 'myblog:templates/' + theme + '/' + template
    return renderers.render_to_response(template, res, request)

def get_anonymous_userid():
    anon_email = 'anonymous@example.com'
    user = DBSession.query(Users.userid).filter_by(userid = anon_email).first()
    if not user:
        # Create user
        user = Users(userid = anon_email)
        DBSession.add(user)
    return user.userid

@region.cache_on_arguments()
def to_markdown(input_text):
    '''Basic wrapper around the markdown library.
    
    Basically, it means that we state the extensions we
    use only once-here.'''
    extensions = ['markdown.extensions.codehilite',
                'markdown.extensions.fenced_code']
    res = markdown(input_text, extensions = extensions)
    return res

def append_tags_from_string_to_tag_object(tag_string, tag_object):
    tags_on_tag_object = [] # This is to be a list of tags on the tag_object
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
        existing_tag = DBSession.query(Tags).filter_by(tag = tag).first()
        if not existing_tag:
            tag_obj = Tags(tag = tag)
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
    tags = [t.tag for t in tag_object]
    tags.sort()
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
        tags[e] = "<a href = {link}>{tag}</a>".format(tag = tag,
                            link = request.route_url('tag_view',
                                                    tag_name = tag))
    return ', '.join(tags)

def create_post_list_from_posts_obj(request, post_obj):
    settings =  request.registry.settings
    LENGTH_OF_EACH_POST_TO_INCLUDE_IN_ALL_POST_VIEW = settings['myblog.allViewPostLen']
    l = LENGTH_OF_EACH_POST_TO_INCLUDE_IN_ALL_POST_VIEW
    res = []
    code_styles = False  # Is true if we need to include pygments css
    # in the page
    for post in post_obj:
        to_append = {}
        to_append["name"] = post.name
        to_append["html"] = to_markdown(post.markdown[:l] + '\n\n...')
        to_append["date"] = ago.human(post.created, precision = 1)
        res.append(to_append)
        if not code_styles and 'class="codehilite"' in to_append["html"]:
            code_styles = True
    return res, code_styles


class RenderingPost(object):
    """This is an event that gets fired when a post is being viewed.
    Subscribers can add html sections to self.sections and these will be
    put below the post on the webpage.
    """
    def __init__(self, post, request):
        self.post = post
        self.request = request
        self.sections = []
