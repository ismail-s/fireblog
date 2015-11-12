from fireblog.settings import mapping
from fireblog.utils import use_template, TemplateResponseDict
from pyramid.view import view_config, view_defaults


@view_config(route_name='settings', decorator=use_template(
    'settings.mako'), permission=None, request_method="GET")
def settings(request):
    save_url = request.route_url('settings')
    return TemplateResponseDict(mapping=mapping, save_url=save_url)
