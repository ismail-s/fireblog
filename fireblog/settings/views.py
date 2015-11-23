from fireblog.settings import mapping, settings_dict, validate_value
from fireblog.utils import use_template, TemplateResponseDict
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
import logging


log = logging.getLogger(__name__)


@view_defaults(route_name='settings', permission='change-settings')
class Settings:

    def __init__(self, request):
        self.request = request

    @view_config(decorator=use_template('settings.mako'), request_method="GET")
    def settings(self):
        new_mapping = (e._replace(
            value=settings_dict[e.registry_name]) for e in mapping)
        new_mapping = tuple(new_mapping)
        save_url = self.request.route_url('settings')
        return TemplateResponseDict(mapping=new_mapping, save_url=save_url)

    @view_config(request_method="POST")
    def settings_post(self):
        params = self.request.params
        errors = []
        to_set = []
        for entry in mapping:
            value = params.get(entry.registry_name, None)
            valid, value, error_str = validate_value(entry, value)
            if not valid:
                errors.append(error_str)
                continue
            to_set.append((entry.registry_name, value))
        if not errors:
            # Settings will only be changed if all settings on the page were
            # valid.
            for reg_name, value in to_set:
                log.info('Changing {} setting to {}'.format(reg_name, value))
                settings_dict[reg_name] = value
        else:
            log.info('Invalid changes to settings attempted:')
            for e in errors:
                log.info(e)
                self.request.session.flash(e)
        return HTTPFound(location=self.request.route_url('settings'))
