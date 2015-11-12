from fireblog.settings import mapping, registry_names, settings_dict
from fireblog.utils import use_template, TemplateResponseDict
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError

@view_defaults(route_name='settings', permission=None)
class Settings:
    def __init__(self, request):
        self.request = request

    @view_config(decorator=use_template('settings.mako'), request_method="GET")
    def settings(self):
        # TODO-get the current values
        save_url = self.request.route_url('settings')
        return TemplateResponseDict(mapping=mapping, save_url=save_url)

    @view_config(request_method="POST")
    def settings_post(self):
        invalid_value_str = '{} is invalid.'
        params = self.request.params
        errors = []
        to_set = []
        for entry in mapping:
            value = params.get(entry.registry_name, None)
            if not value:
                # Only a malformed request should hit this
                return HTTPInternalServerError()
            try:
                value = entry.type(value)
            except Exception:
                errors.append(invalid_value_str.format(entry.display_name))
                continue
            if not entry.validator(value):
                errors.append(invalid_value_str.format(entry.display_name))
                continue
            if entry.min and entry.min > value:
                error_str = '{} is too small (it should be bigger than {})'
                errors.append(error_str.format(entry.display_name, entry.min))
                continue
            if entry.max and entry.max < value:
                error_str = '{} is too large (it should be smaller than {})'
                errors.append(error_str.format(entry.display_name, entry.max))
                continue
            # Settings will only be changed if all settings on the page were
            # valid.
            to_set.append((entry.registry_name, value))
        if not errors:
            for reg_name, value in to_set:
                settings_dict[reg_name] = value
        else:
            (self.request.session.flash(e) for e in errors)
        return HTTPFound(location=self.request.route_url('settings'))
