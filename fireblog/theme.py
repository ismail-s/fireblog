'''
Code that allows for changing the template files used at runtime. This
provides support for themes, which are just folders containing template files.
'''
import fireblog.utils as utils
from pyramid.response import Response


def template_response_adapter(s: utils.TemplateResponseDict):
    """This function works in tandem with
    :py:class:`fireblog.utils.TemplateResponseDict`. This function assumes s
    is an instance of :py:func:`fireblog.utils.TemplateResponseDict` and
    returns a :py:class:`pyramid.response.Response` containing a string
    representation of s."""
    assert isinstance(s, utils.TemplateResponseDict)
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
        template_response_adapter, utils.TemplateResponseDict)
