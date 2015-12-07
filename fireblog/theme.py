'''
Code that allows for changing the template files used at runtime. This
provides support for themes, which are just folders containing template files.
'''
from fireblog.settings import settings_dict
from pyramid.response import Response
from pyramid.httpexceptions import HTTPException
from pyramid import renderers
import functools
import logging


log = logging.getLogger(__name__)


class TemplateResponseDict(dict):
    '''Instances of this dict can be used as the return type of a view callable
    that is using the use_template decorator. The :py:func:`use_template`
    decorator will notice that an instance of this type is being returned and
    render it to a response.

    This class is used in tandem with
    :py:func:`template_response_adapter`'''
    pass


def use_template(template: str=None):
    """This decorator allows a view to be rendered using whatever the current
    active template aka theme is."""
    def wrapper(f, template=template):
        @functools.wraps(f)
        def inner(context, request):
            res = f(context, request)
            # Deal with eg HTTPFound or HTTPNotFound by just returning them.
            if isinstance(res, HTTPException):
                return res
            # Pull out the custom dict object set by
            # :py:func:`fireblog.template_response_adapter`
            to_render = res._fireblog_custom_response
            if not isinstance(to_render, dict):
                raise Exception(  # pragma: no cover
                    "The use_template decorator is being used "
                    "incorrectly: the decorated view callable must return a "
                    "dict.")
            return render_to_response(template, to_render, request)
        return inner
    return wrapper


def render_to_response(template, res, request):
    theme = settings_dict['fireblog.theme']
    template = 'fireblog:templates/' + theme + '/' + template
    log.debug('Rendering template {}'.format(template))
    return renderers.render_to_response(template, res, request)


def template_response_adapter(s: TemplateResponseDict):
    """This function works in tandem with
    :py:class:`TemplateResponseDict`. This function assumes s
    is an instance of :py:func:`TemplateResponseDict` and
    returns a :py:class:`pyramid.response.Response` containing a string
    representation of s."""
    assert isinstance(s, TemplateResponseDict)
    # We need to return a Response() object, as per the Pyramid specs. But we
    # want to not store a string in the Response yet, but an arbitrary dict
    # as after this function returns, :py:func:`use_template` will do further
    # processing on this arbitrary dict. So we set a custom field on this
    # Respnse object, which we can retrieve in :py:func:`use_template`.
    response = Response()
    response._fireblog_custom_response = s
    return response


def includeme(config):
    config.add_response_adapter(
        template_response_adapter, TemplateResponseDict)
