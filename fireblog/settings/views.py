from fireblog.settings import mapping, registry_names
from fireblog.utils import use_template, TemplateResponseDict
from pyramid.view import view_config, view_defaults


@view_defaults(route_name='settings', permission=None)
class Settings:
    def __init__(self, request):
        self.request = request

    @view_config(decorator=use_template('settings.mako'), request_method="GET")
    def settings(self):
        save_url = self.request.route_url('settings')
        return TemplateResponseDict(mapping=mapping, save_url=save_url)
